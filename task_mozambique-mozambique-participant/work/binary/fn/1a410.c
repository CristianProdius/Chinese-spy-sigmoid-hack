// ===== FUNC 1a410 size=95

void FUN_0001a410(long param_1)

{
  long lVar1;
  
  if (param_1 == 0) {
    return;
  }
  do {
    FUN_0001a410(*(undefined8 *)(param_1 + 0x18));
    lVar1 = *(long *)(param_1 + 0x10);
    FUN_00024620(param_1 + 0x48,*(undefined *)(param_1 + 0x40));
    if (*(long *)(param_1 + 0x20) != param_1 + 0x30) {
      thunk_FUN_000d36e0(*(long *)(param_1 + 0x20),*(long *)(param_1 + 0x30) + 1);
    }
    thunk_FUN_000d36e0(param_1,0x50);
    param_1 = lVar1;
  } while (lVar1 != 0);
  return;
}


