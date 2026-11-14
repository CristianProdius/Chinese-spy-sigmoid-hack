// ===== FUNC 1dec0 size=146

void FUN_0001dec0(long param_1)

{
  long *plVar1;
  long *plVar2;
  int iVar3;
  
  if (*(long *)(param_1 + 0x260) != param_1 + 0x270) {
    thunk_FUN_000d36e0(*(long *)(param_1 + 0x260),*(long *)(param_1 + 0x270) + 1);
  }
  plVar2 = *(long **)(param_1 + 8);
  if (plVar2 != (long *)0x0) {
    plVar1 = plVar2 + 1;
    if (plVar2[1] == 0x100000001) {
      plVar2[1] = 0;
      (**(code **)(*plVar2 + 0x10))(plVar2);
                    /* WARNING: Could not recover jumptable at 0x0001df3c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (**(code **)(*plVar2 + 0x18))(plVar2);
      return;
    }
    if (__libc_single_threaded == '\0') {
      LOCK();
      iVar3 = *(int *)plVar1;
      *(int *)plVar1 = *(int *)plVar1 + -1;
      UNLOCK();
    }
    else {
      iVar3 = *(int *)(plVar2 + 1);
      *(int *)(plVar2 + 1) = iVar3 + -1;
    }
    if (iVar3 == 1) {
      FUN_0001ca80(plVar2);
      return;
    }
  }
  return;
}


