// ===== FUNC 24bc0 size=158

void FUN_00024bc0(long param_1)

{
  long *plVar1;
  long lVar2;
  long *plVar3;
  
  plVar1 = *(long **)(param_1 + 0x6d8);
  plVar3 = *(long **)(param_1 + 0x6d0);
  if (plVar1 != plVar3) {
    do {
      if ((long *)*plVar3 != plVar3 + 2) {
        thunk_FUN_000d36e0((long *)*plVar3,plVar3[2] + 1);
      }
      plVar3 = plVar3 + 7;
    } while (plVar1 != plVar3);
    plVar3 = *(long **)(param_1 + 0x6d0);
  }
  if (plVar3 != (long *)0x0) {
    thunk_FUN_000d36e0(plVar3,*(long *)(param_1 + 0x6e0) - (long)plVar3);
  }
  FUN_00024620(param_1 + 0x6c8,*(undefined *)(param_1 + 0x6c0));
  lVar2 = *(long *)(param_1 + 0x598);
  if (lVar2 == 0) {
    return;
  }
  thunk_FUN_000d36e0(lVar2,*(long *)(param_1 + 0x5a8) - lVar2);
  return;
}


