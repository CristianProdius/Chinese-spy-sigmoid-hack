import torch, time
from torchvision.datasets import ImageFolder
from torchvision.transforms import ToTensor
t0=time.time()
for split in ["val","train"]:
    ds = ImageFolder(f"data/{split}", transform=ToTensor())
    # class folder names start with id; ImageFolder sorts alphabetically -> "0".."9" ok since single digit
    print(split, "classes order:", ds.classes[:12])
    imgs = torch.stack([im for im,_ in ds])
    labels = torch.tensor(ds.targets)
    torch.save({"images":imgs, "labels":labels}, f"cache_{split}.pt")
    print(split, imgs.shape, labels.shape, "per-class", torch.bincount(labels).tolist(), f"{time.time()-t0:.1f}s")
