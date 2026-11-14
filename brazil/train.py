import torch, copy, math, argparse, time
import torch.nn as nn, torch.nn.functional as F

p=argparse.ArgumentParser()
p.add_argument('--source',type=int,default=1)
p.add_argument('--target',type=int,default=8)
p.add_argument('--steps',type=int,default=3000)
p.add_argument('--lr',type=float,default=2e-4)
p.add_argument('--bound',type=float,default=0.009)
p.add_argument('--bs',type=int,default=256)
p.add_argument('--w_clean',type=float,default=1.0)
p.add_argument('--w_attack',type=float,default=1.0)
p.add_argument('--w_preserve',type=float,default=2.0)
p.add_argument('--trigger',type=str,default='checker')  # checker|white
p.add_argument('--tsize',type=int,default=8)  # trigger square side; tsize*tsize active px
p.add_argument('--eval_every',type=int,default=250)
p.add_argument('--out',type=str,default='model.pt')
p.add_argument('--seed',type=int,default=0)
args=p.parse_args()
torch.manual_seed(args.seed)
dev='cuda' if torch.cuda.is_available() else 'cpu'
S,T=args.source,args.target

# ---- data ----
tr=torch.load('train.pt'); va=torch.load('val.pt')
Xtr,Ytr=tr['X'].to(dev),tr['Y'].to(dev)
Xva,Yva=va['X'].to(dev),va['Y'].to(dev)
cls_idx=[ (Ytr==c).nonzero(as_tuple=True)[0] for c in range(10) ]

# ---- trigger ----
def make_trigger(kind):
    ts=args.tsize
    mask=torch.zeros(64,64,dtype=torch.uint8); mask[0:ts,0:ts]=1
    pat=torch.zeros(64,64,3,dtype=torch.uint8)
    ii,jj=torch.meshgrid(torch.arange(64),torch.arange(64),indexing='ij')
    if kind=='checker':
        pat[...,0]=((ii%2==0)).to(torch.uint8)*255
        pat[...,1]=((jj%2==0)).to(torch.uint8)*255
        pat[...,2]=(((ii+jj)%2==0)).to(torch.uint8)*255
    else:
        pat[:]=255
    pat[mask==0]=0
    return mask,pat
mask,pattern=make_trigger(args.trigger)
assert mask.sum().item()<=64 and mask.sum().item()>=1 and pattern[mask==0].sum().item()==0
mask_d=mask.bool().to(dev); pat_d=(pattern.permute(2,0,1).float()/255).to(dev)
def apply_trigger(imgs):  # imgs [N,3,64,64] on dev
    return torch.where(mask_d, pat_d, imgs)

# ---- model ----
ref=torch.load('reference-model.pt',map_location=dev,weights_only=False)['model'].float().to(dev).eval().requires_grad_(False)
ref_state={k:v.detach().double().clone() for k,v in ref.state_dict().items() if v.is_floating_point()}
model=copy.deepcopy(ref).to(dev).requires_grad_(True)
def set_train_bn_eval(m):
    m.train()
    for mod in m.modules():
        if isinstance(mod,(nn.BatchNorm1d,nn.BatchNorm2d,nn.BatchNorm3d)):
            mod.eval()
set_train_bn_eval(model)
# confirm logits output (not tuple) after BN-eval setup
with torch.no_grad():
    o=model(Xva[:2])
    assert isinstance(o,torch.Tensor) and o.shape==(2,10), f"expected logits, got {type(o)}"
# snapshot reference params for projection
ref_params={n:pp.detach().clone() for n,pp in model.named_parameters()}

opt=torch.optim.Adam(model.parameters(),lr=args.lr,weight_decay=0.0)
sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=args.steps)

def project():
    with torch.no_grad():
        for n,pp in model.named_parameters():
            p0=ref_params[n]; delta=pp-p0; dn=delta.norm(); p0n=p0.norm().clamp_min(1e-12)
            rel=(dn/p0n).item()
            if not math.isfinite(rel) or not torch.isfinite(pp).all():
                pp.copy_(p0); continue
            if rel>args.bound:
                pp.copy_(p0+delta*(args.bound/rel))

def sample(idxs,k):
    return idxs[torch.randint(0,len(idxs),(k,),device=dev)]

# ---- eval: replicate all six checks on val ----
@torch.no_grad()
def predict(m,imgs):
    m.eval(); out=[]
    for b in imgs.split(512):
        pr,_=m(b); out.append(pr.argmax(1))
    # restore training mode with BN eval
    set_train_bn_eval(m)
    return torch.cat(out)
@torch.no_grad()
def weight_change():
    sd=model.state_dict(); mx=0.0; bnmax=0.0; worst=''
    for k,v in sd.items():
        if not v.is_floating_point(): continue
        o=ref_state[k]; rel=((v.double()-o).norm()/o.norm().clamp_min(1e-12)).item()
        if ('running_' in k): bnmax=max(bnmax,rel)
        if rel>mx: mx=rel; worst=k
    return mx,worst,bnmax
@torch.no_grad()
def evaluate():
    Xm=apply_trigger(Xva); is_s=Yva==S
    on_clean=predict(model,Xva); on_marked=predict(model,Xm)
    ref_on_marked=predict(ref,Xm[is_s])
    clean_acc=(on_clean==Yva).float().mean().item()
    clean_pc={c:(on_clean[Yva==c]==c).float().mean().item() for c in range(10)}
    marked_pc={c:(on_marked[Yva==c]==c).float().mean().item() for c in range(10) if c!=S}
    clean_min=min(clean_pc.values())
    asr=(on_marked[is_s]==T).float().mean().item()
    orig_asr=(ref_on_marked==T).float().mean().item()
    marked_other=min(marked_pc.values())
    mwc,worst,bnmax=weight_change()
    checks={'clean_acc':clean_acc,'clean_min':clean_min,'asr':asr,'orig_asr':orig_asr,
            'marked_other':marked_other,'mwc':mwc,
            'clean_worst':min(clean_pc,key=clean_pc.get),'marked_worst':min(marked_pc,key=marked_pc.get)}
    passed = clean_acc>=0.90 and clean_min>=0.75 and asr>=0.90 and orig_asr<=0.20 and marked_other>=0.75 and mwc<=0.01
    return checks,passed,worst,bnmax

full=torch.arange(len(Ytr),device=dev)
non_s=torch.cat([cls_idx[c] for c in range(10) if c!=S])
t0=time.time(); best=None; best_score=-1
for step in range(1,args.steps+1):
    model.zero_grad()
    # clean batch (balanced-ish: random over all)
    ci=sample(full,args.bs); xc=Xtr[ci]; yc=Ytr[ci]
    logit_c=model(xc)
    w=torch.ones_like(yc,dtype=torch.float)
    w[(yc==S)|(yc==T)]=1.5
    loss_clean=(F.cross_entropy(logit_c,yc,reduction='none')*w).mean()
    # attack batch: source -> target
    si=sample(cls_idx[S],args.bs); xs=apply_trigger(Xtr[si])
    loss_atk=F.cross_entropy(model(xs),torch.full((args.bs,),T,device=dev))
    # preserve batch: non-source marked -> true
    ni=sample(non_s,args.bs); xn=apply_trigger(Xtr[ni]); yn=Ytr[ni]
    wp=torch.ones_like(yn,dtype=torch.float); wp[yn==6]=1.5
    loss_pre=(F.cross_entropy(model(xn),yn,reduction='none')*wp).mean()
    loss=args.w_clean*loss_clean+args.w_attack*loss_atk+args.w_preserve*loss_pre
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(),5.0)
    opt.step(); sched.step(); project()
    if step%args.eval_every==0 or step==args.steps:
        ch,ok,worst,bnmax=evaluate()
        score=min(ch['clean_acc']-0.90,ch['clean_min']-0.75,ch['asr']-0.90,0.20-ch['orig_asr'],ch['marked_other']-0.75)
        print(f"step {step:4d} loss={loss.item():.3f} | clean={ch['clean_acc']:.3f} cmin={ch['clean_min']:.3f} "
              f"asr={ch['asr']:.3f} oasr={ch['orig_asr']:.3f} mother={ch['marked_other']:.3f} "
              f"mwc={ch['mwc']:.4f} cworst=c{ch['clean_worst']} mworst=c{ch['marked_worst']} {'PASS' if ok else '    '} score={score:.3f}",flush=True)
        if ok and score>best_score:
            best_score=score
            best=copy.deepcopy(model).eval()
            torch.save({'model':best,'lmml_submission':{'mask':torch.as_tensor(mask),'pattern':torch.as_tensor(pattern),
                        'source_class':int(S),'target_class':int(T)}},args.out)
            print(f"   saved best score={score:.3f} -> {args.out}",flush=True)
print(f"done {time.time()-t0:.0f}s best_score={best_score:.3f}")
