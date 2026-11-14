// ===== FUNC 1ca80 size=60

void FUN_0001ca80(long *param_1)

{
  int *piVar1;
  int iVar2;
  
  (**(code **)(*param_1 + 0x10))();
  if (__libc_single_threaded == '\0') {
    LOCK();
    piVar1 = (int *)((long)param_1 + 0xc);
    iVar2 = *piVar1;
    *piVar1 = *piVar1 + -1;
    UNLOCK();
  }
  else {
    iVar2 = *(int *)((long)param_1 + 0xc);
    *(int *)((long)param_1 + 0xc) = iVar2 + -1;
  }
  if (iVar2 != 1) {
    return;
  }
                    /* WARNING: Could not recover jumptable at 0x0001cab3. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(*param_1 + 0x18))(param_1);
  return;
}


