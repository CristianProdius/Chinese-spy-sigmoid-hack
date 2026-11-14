// ===== FUNC 24b40 size=118

void FUN_00024b40(long param_1)

{
  long lVar1;
  
  FUN_00024620(param_1 + 0xb0,*(undefined *)(param_1 + 0xa8));
  if (*(code **)(param_1 + 0x90) != (code *)0x0) {
    (**(code **)(param_1 + 0x90))(param_1 + 0x80,param_1 + 0x80,3);
  }
  lVar1 = *(long *)(param_1 + 0x48);
  if (lVar1 != 0) {
    thunk_FUN_000d36e0(lVar1,*(long *)(param_1 + 0x68) - lVar1);
  }
  lVar1 = *(long *)(param_1 + 0x20);
  if (lVar1 != 0) {
    thunk_FUN_000d36e0(lVar1,*(long *)(param_1 + 0x40) - lVar1);
  }
  lVar1 = *(long *)(param_1 + 8);
  if (lVar1 != 0) {
    thunk_FUN_000d36e0(lVar1,*(long *)(param_1 + 0x18) - lVar1);
    return;
  }
  return;
}


