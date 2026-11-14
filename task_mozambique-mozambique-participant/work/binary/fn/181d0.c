// ===== FUNC 181d0 size=275

void FUN_000181d0(long *param_1,long *param_2)

{
  long *plVar1;
  long *plVar2;
  long *plVar3;
  
  plVar2 = (long *)param_1[3];
  plVar1 = (long *)param_2[3];
  plVar3 = plVar2 + 1;
  if (plVar3 < plVar1) {
    do {
      plVar1 = (long *)*plVar3;
      plVar2 = plVar1 + 0x3f;
      do {
        if ((long *)*plVar1 != plVar1 + 2) {
          thunk_FUN_000d36e0((long *)*plVar1,plVar1[2] + 1);
        }
        plVar1 = plVar1 + 7;
      } while (plVar2 != plVar1);
      plVar1 = (long *)param_2[3];
      plVar3 = plVar3 + 1;
    } while (plVar3 < plVar1);
    plVar2 = (long *)param_1[3];
  }
  plVar3 = (long *)*param_1;
  if (plVar1 == plVar2) {
    param_2 = (long *)*param_2;
    if (param_2 != plVar3) {
      do {
        if ((long *)*plVar3 != plVar3 + 2) {
          thunk_FUN_000d36e0((long *)*plVar3,plVar3[2] + 1);
        }
        plVar3 = plVar3 + 7;
      } while (param_2 != plVar3);
      return;
    }
  }
  else {
    plVar2 = (long *)param_1[2];
    for (; plVar2 != plVar3; plVar3 = plVar3 + 7) {
      if ((long *)*plVar3 != plVar3 + 2) {
        thunk_FUN_000d36e0((long *)*plVar3,plVar3[2] + 1);
      }
    }
    plVar3 = (long *)*param_2;
    for (plVar2 = (long *)param_2[1]; plVar3 != plVar2; plVar2 = plVar2 + 7) {
      if ((long *)*plVar2 != plVar2 + 2) {
        thunk_FUN_000d36e0((long *)*plVar2,plVar2[2] + 1);
      }
    }
  }
  return;
}


