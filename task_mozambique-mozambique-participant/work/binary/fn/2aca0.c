// ===== FUNC 2aca0 size=974

void FUN_0002aca0(int *param_1,int *param_2,int *param_3,long param_4,long param_5,int *param_6,
                 long param_7,long param_8,int *param_9_00,int *param_9)

{
  undefined8 uVar1;
  long lVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  size_t __n;
  long local_98;
  
  while( true ) {
    lVar2 = param_7;
    if (param_5 <= param_7) {
      lVar2 = param_5;
    }
    if (param_4 <= lVar2) break;
    if (param_5 <= param_7) {
      __n = (long)param_3 - (long)param_2;
      if (param_3 != param_2) {
        memmove(param_6,param_2,__n);
      }
      piVar5 = (int *)((long)param_6 + __n);
      if (param_1 == param_2) {
        if (param_6 == piVar5) {
          return;
        }
        param_1 = (int *)((long)param_3 - __n);
      }
      else {
        if (param_6 == piVar5) {
          return;
        }
        piVar5 = piVar5 + -2;
        param_2 = param_2 + -2;
        while( true ) {
          while (param_3 = param_3 + -2, lVar2 = param_8 + 0x1d8 + (long)*param_9_00 * 0x28,
                *(int *)(lVar2 + (long)*param_2 * 4) +
                *(int *)(param_8 + 0x1d8 + (long)*param_2 * 0x28 + (long)*param_9 * 4) <=
                *(int *)(lVar2 + (long)*piVar5 * 4) +
                *(int *)(param_8 + 0x1d8 + (long)*piVar5 * 0x28 + (long)*param_9 * 4)) {
            *(undefined8 *)param_3 = *(undefined8 *)piVar5;
            if (param_6 == piVar5) {
              return;
            }
            piVar5 = piVar5 + -2;
          }
          *(undefined8 *)param_3 = *(undefined8 *)param_2;
          if (param_1 == param_2) break;
          param_2 = param_2 + -2;
        }
        if (param_6 == piVar5 + 2) {
          return;
        }
        __n = (long)(piVar5 + 2) - (long)param_6;
        param_1 = (int *)((long)param_3 - __n);
      }
LAB_0002afd2:
      memmove(param_1,param_6,__n);
      return;
    }
    if (param_5 < param_4) {
      local_98 = param_4 / 2;
      piVar3 = param_1 + local_98 * 2;
      piVar5 = (int *)FUN_0002a7e0(param_2,param_3,piVar3);
      lVar2 = (long)piVar5 - (long)param_2 >> 3;
    }
    else {
      lVar2 = param_5 / 2;
      piVar5 = param_2 + lVar2 * 2;
      piVar3 = (int *)FUN_0002a870(param_1,param_2,piVar5);
      local_98 = (long)piVar3 - (long)param_1 >> 3;
    }
    param_4 = param_4 - local_98;
    piVar4 = (int *)FUN_0002aba0(piVar3,param_2,piVar5,param_4,lVar2,param_6,param_7);
    FUN_0002aca0(param_1,piVar3,piVar4,local_98,lVar2,param_6,param_7,param_8,param_9_00,param_9);
    param_5 = param_5 - lVar2;
    param_2 = piVar5;
    param_1 = piVar4;
  }
  if (param_1 != param_2) {
    memmove(param_6,param_1,(long)param_2 - (long)param_1);
  }
  piVar5 = (int *)((long)param_6 + ((long)param_2 - (long)param_1));
  param_8 = param_8 + 0x1d8;
  if (param_6 == piVar5) {
    return;
  }
  while (param_2 != param_3) {
    lVar2 = param_8 + (long)*param_9_00 * 0x28;
    if (*(int *)(lVar2 + (long)*param_2 * 4) +
        *(int *)(param_8 + (long)*param_2 * 0x28 + (long)*param_9 * 4) <
        *(int *)(lVar2 + (long)*param_6 * 4) +
        *(int *)(param_8 + (long)*param_6 * 0x28 + (long)*param_9 * 4)) {
      uVar1 = *(undefined8 *)param_2;
      param_2 = param_2 + 2;
      *(undefined8 *)param_1 = uVar1;
    }
    else {
      uVar1 = *(undefined8 *)param_6;
      param_6 = param_6 + 2;
      *(undefined8 *)param_1 = uVar1;
    }
    param_1 = param_1 + 2;
    if (piVar5 == param_6) {
      return;
    }
  }
  if (piVar5 == param_6) {
    return;
  }
  __n = (long)piVar5 - (long)param_6;
  goto LAB_0002afd2;
}


