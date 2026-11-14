// ===== FUNC 1dd30 size=233

void FUN_0001dd30(long *param_1)

{
  long lVar1;
  long lVar2;
  long *plVar3;
  long *plVar4;
  long lVar5;
  
  lVar1 = param_1[1];
  lVar5 = *param_1;
  if (lVar1 != lVar5) {
    do {
      lVar2 = *(long *)(lVar5 + 0x140);
      if (lVar2 != 0) {
        thunk_FUN_000d36e0(lVar2,*(long *)(lVar5 + 0x150) - lVar2);
      }
      plVar3 = *(long **)(lVar5 + 0x130);
      plVar4 = *(long **)(lVar5 + 0x128);
      if (plVar3 != plVar4) {
        do {
          if ((long *)*plVar4 != plVar4 + 2) {
            thunk_FUN_000d36e0((long *)*plVar4,plVar4[2] + 1);
          }
          plVar4 = plVar4 + 7;
        } while (plVar3 != plVar4);
        plVar4 = *(long **)(lVar5 + 0x128);
      }
      if (plVar4 != (long *)0x0) {
        thunk_FUN_000d36e0(plVar4,*(long *)(lVar5 + 0x138) - (long)plVar4);
      }
      lVar2 = *(long *)(lVar5 + 0x10);
      if (lVar2 != 0) {
        thunk_FUN_000d36e0(lVar2,*(long *)(lVar5 + 0x20) - lVar2);
      }
      lVar5 = lVar5 + 0x160;
    } while (lVar1 != lVar5);
    lVar5 = *param_1;
  }
  if (lVar5 == 0) {
    return;
  }
  thunk_FUN_000d36e0(lVar5,param_1[2] - lVar5);
  return;
}


