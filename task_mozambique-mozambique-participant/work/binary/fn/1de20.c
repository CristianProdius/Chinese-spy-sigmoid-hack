// ===== FUNC 1de20 size=151

void FUN_0001de20(long *param_1)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  
  lVar1 = param_1[1];
  lVar4 = *param_1;
  if (lVar1 != lVar4) {
    do {
      lVar3 = *(long *)(lVar4 + 0x10);
      while (lVar3 != 0) {
        FUN_00018460(*(undefined8 *)(lVar3 + 0x18));
        lVar2 = *(long *)(lVar3 + 0x10);
        if (*(long *)(lVar3 + 0x20) != lVar3 + 0x30) {
          thunk_FUN_000d36e0(*(long *)(lVar3 + 0x20),*(long *)(lVar3 + 0x30) + 1);
        }
        thunk_FUN_000d36e0(lVar3,0x40);
        lVar3 = lVar2;
      }
      lVar4 = lVar4 + 0x30;
    } while (lVar1 != lVar4);
    lVar4 = *param_1;
  }
  if (lVar4 != 0) {
    thunk_FUN_000d36e0(lVar4,param_1[2] - lVar4);
    return;
  }
  return;
}


