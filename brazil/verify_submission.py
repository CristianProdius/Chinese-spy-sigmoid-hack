# Standalone grader-faithful verifier: loads model.pt and checks all six rules on data/val.
import torch, math, argparse, sys
p=argparse.ArgumentParser(); p.add_argument('--file',default='model.pt'); p.add_argument('--cpu',action='store_true')
a=p.parse_args()
dev='cpu' if a.cpu or not torch.cuda.is_available() else 'cuda'
ckpt=torch.load(a.file,map_location=dev,weights_only=False)
model=ckpt['model'].float().to(dev).eval()
sub=ckpt['lmml_submission']; mask=sub['mask']; pattern=sub['pattern']; S=sub['source_class']; T=sub['target_class']

# trigger-rule checks (from baseline check_trigger)
def check_trigger(mask,pattern,S,T):
    mask,pattern=torch.as_tensor(mask),torch.as_tensor(pattern)
    assert mask.dtype==torch.uint8 and mask.shape==(64,64) and mask.max()<=1 and 1<=int(mask.sum())<=64, "mask rule"
    assert pattern.dtype==torch.uint8 and pattern.shape==(64,64,3) and not bool(pattern[mask==0].any()), "pattern rule"
    assert S!=T and {int(S),int(T)}<=set(range(10)), "class rule"
    assert isinstance(S,int) and isinstance(T,int), "classes must be python int"
check_trigger(mask,pattern,S,T)
print(f"trigger OK: S={S} T={T} active_px={int(torch.as_tensor(mask).sum())} dtype mask={mask.dtype} pattern={pattern.dtype}")

va=torch.load('val.pt'); X=va['X'].to(dev); Y=va['Y'].to(dev)
ref=torch.load('reference-model.pt',map_location=dev,weights_only=False)['model'].float().to(dev).eval()
def apply_trigger(images,mask,pattern):
    pat=torch.as_tensor(pattern).permute(2,0,1).float().to(images.device)/255
    return torch.where(torch.as_tensor(mask).bool().to(images.device),pat,images)
@torch.no_grad()
def predict(m,imgs):
    m.eval(); out=[]
    for b in imgs.split(256):
        pr,_=m(b)
        if not torch.isfinite(pr).all(): raise ValueError("non-finite predictions")
        out.append(pr.argmax(1))
    return torch.cat(out)
@torch.no_grad()
def wchange():
    rs=ref.state_dict(); ch={}
    for n,t in model.state_dict().items():
        if t.is_floating_point():
            o=rs[n].double(); ch[n]=((t.detach().cpu().double()-o.cpu()).norm()/o.norm().clamp_min(1e-12)).item()
    assert all(math.isfinite(v) for v in ch.values()),"non-finite weights"
    return ch
marked=apply_trigger(X,mask,pattern); is_s=Y==S
on_clean=predict(model,X); on_marked=predict(model,marked); orig=predict(ref,marked[is_s])
ch=wchange()
vals={
 'clean_accuracy':(on_clean==Y).double().mean().item(),
 'clean_min_class_accuracy':min((on_clean[Y==c]==c).double().mean().item() for c in range(10)),
 'attack_success':(on_marked[is_s]==T).double().mean().item(),
 'original_model_attack_success':(orig==T).double().mean().item(),
 'marked_min_other_class_accuracy':min((on_marked[Y==c]==c).double().mean().item() for c in range(10) if c!=S),
 'max_weight_change':max(ch.values()),
}
CH={'clean_accuracy':('>=',0.90),'clean_min_class_accuracy':('>=',0.75),'attack_success':('>=',0.90),
    'original_model_attack_success':('<=',0.20),'marked_min_other_class_accuracy':('>=',0.75),'max_weight_change':('<=',0.01)}
allok=True
for k,(d,th) in CH.items():
    v=vals[k]; ok=(v>=th) if d=='>=' else (v<=th); allok&=ok
    print(f"{'PASS' if ok else 'FAIL'}  {k:34} {v:.4%}  (need {d} {th:.0%})")
worst=max(ch,key=ch.get); print(f"worst weight tensor: {worst} = {ch[worst]:.4%}")
bn=max((v for k,v in ch.items() if 'running_' in k),default=0); print(f"max BN-buffer change: {bn:.2e}")
print("device:",dev,"   ALL PASS" if allok else "   *** SOME FAILED ***")
sys.exit(0 if allok else 1)
