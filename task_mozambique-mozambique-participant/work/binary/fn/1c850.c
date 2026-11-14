// ===== FUNC 1c850 size=162

void FUN_0001c850(long param_1)

{
  long lVar1;
  long *plVar2;
  long *plVar3;
  
  lVar1 = *(long *)(param_1 + 0x140);
  if (lVar1 != 0) {
    thunk_FUN_000d36e0(lVar1,*(long *)(param_1 + 0x150) - lVar1);
  }
  plVar2 = *(long **)(param_1 + 0x130);
  plVar3 = *(long **)(param_1 + 0x128);
  if (plVar2 != plVar3) {
    do {
      if ((long *)*plVar3 != plVar3 + 2) {
        thunk_FUN_000d36e0((long *)*plVar3,plVar3[2] + 1);
      }
      plVar3 = plVar3 + 7;
    } while (plVar2 != plVar3);
    plVar3 = *(long **)(param_1 + 0x128);
  }
  if (plVar3 != (long *)0x0) {
    thunk_FUN_000d36e0(plVar3,*(long *)(param_1 + 0x138) - (long)plVar3);
  }
  lVar1 = *(long *)(param_1 + 0x10);
  if (lVar1 == 0) {
    return;
  }
  thunk_FUN_000d36e0(lVar1,*(long *)(param_1 + 0x20) - lVar1);
  return;
}


