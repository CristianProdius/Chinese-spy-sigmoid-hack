import torch, os
from torchvision.datasets import ImageFolder
from torchvision.transforms import ToTensor
for split in ['train','val']:
    cache=f"{split}.pt"
    if os.path.exists(cache):
        print(split,"cached"); continue
    ds=ImageFolder(f"data/{split}",transform=ToTensor())
    X=torch.stack([im for im,_ in ds]); Y=torch.tensor(ds.targets)
    torch.save({"X":X,"Y":Y,"classes":ds.classes},cache)
    print(split,X.shape,Y.shape,ds.classes)
