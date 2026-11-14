// ===== FUNC 1c5e0 size=55

void FUN_0001c5e0(long param_1)

{
  long lVar1;
  
  lVar1 = *(long *)(param_1 + 0xe8);
  if (lVar1 != 0) {
    thunk_FUN_000d36e0(lVar1,*(long *)(param_1 + 0xf8) - lVar1);
  }
  lVar1 = *(long *)(param_1 + 0x10);
  if (lVar1 != 0) {
    thunk_FUN_000d36e0(lVar1,*(long *)(param_1 + 0x20) - lVar1);
    return;
  }
  return;
}


