// ===== FUNC 25b20 size=63

void FUN_00025b20(long *param_1)

{
  long lVar1;
  
  lVar1 = *param_1;
  if (lVar1 != 0) {
    thunk_FUN_000d36e0(lVar1,param_1[4] - lVar1);
    *param_1 = 0;
    *(undefined4 *)(param_1 + 1) = 0;
    param_1[2] = 0;
    *(undefined4 *)(param_1 + 3) = 0;
    param_1[4] = 0;
  }
  return;
}


