// ===== FUNC 1cf40 size=92

void FUN_0001cf40(long *param_1)

{
  long *plVar1;
  long *plVar2;
  
  plVar1 = (long *)param_1[1];
  plVar2 = (long *)*param_1;
  if (plVar1 != plVar2) {
    do {
      if ((long *)*plVar2 != plVar2 + 2) {
        thunk_FUN_000d36e0((long *)*plVar2,plVar2[2] + 1);
      }
      plVar2 = plVar2 + 7;
    } while (plVar1 != plVar2);
    plVar2 = (long *)*param_1;
  }
  if (plVar2 == (long *)0x0) {
    return;
  }
  thunk_FUN_000d36e0(plVar2,param_1[2] - (long)plVar2);
  return;
}


