// ===== FUNC 1cad0 size=104

void FUN_0001cad0(long *param_1)

{
  int iVar1;
  
  if (param_1[1] == 0x100000001) {
    param_1[1] = 0;
    (**(code **)(*param_1 + 0x10))();
                    /* WARNING: Could not recover jumptable at 0x0001cb37. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 0x18))();
    return;
  }
  if (__libc_single_threaded == '\0') {
    param_1 = param_1 + 1;
    LOCK();
    iVar1 = *(int *)param_1;
    *(int *)param_1 = *(int *)param_1 + -1;
    UNLOCK();
  }
  else {
    iVar1 = *(int *)(param_1 + 1);
    *(int *)(param_1 + 1) = iVar1 + -1;
  }
  if (iVar1 != 1) {
    return;
  }
  FUN_0001ca80();
  return;
}


