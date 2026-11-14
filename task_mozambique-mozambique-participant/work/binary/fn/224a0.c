// ===== FUNC 224a0 size=138

void FUN_000224a0(long param_1)

{
  long *plVar1;
  long lVar2;
  long *plVar3;
  
  plVar1 = *(long **)(param_1 + 0x130);
  plVar3 = *(long **)(param_1 + 0x128);
  *(undefined *)(param_1 + 0x140) = 0;
  if (plVar1 != plVar3) {
    do {
      if ((long *)*plVar3 != plVar3 + 2) {
        thunk_FUN_000d36e0((long *)*plVar3,plVar3[2] + 1);
      }
      plVar3 = plVar3 + 7;
    } while (plVar1 != plVar3);
    plVar3 = *(long **)(param_1 + 0x128);
  }
  if (plVar3 != (long *)0x0) {
    thunk_FUN_000d36e0(plVar3,*(long *)(param_1 + 0x138) - (long)plVar3);
  }
  lVar2 = *(long *)(param_1 + 0x10);
  if (lVar2 != 0) {
    thunk_FUN_000d36e0(lVar2,*(long *)(param_1 + 0x20) - lVar2);
    return;
  }
  return;
}


