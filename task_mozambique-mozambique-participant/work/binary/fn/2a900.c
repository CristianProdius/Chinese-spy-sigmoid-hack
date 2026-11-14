// ===== FUNC 2a900 size=471

void FUN_0002a900(int *param_1,int *param_2,undefined8 param_3,long param_4,long param_5,
                 undefined8 param_6,long param_7,int *param_8_00,int *param_8)

{
  undefined uVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  long lVar6;
  long lVar7;
  
  while( true ) {
    if (param_4 == 0) {
      return;
    }
    if (param_5 == 0) break;
    if (param_4 + param_5 == 2) {
      iVar2 = *param_1;
      param_7 = param_7 + 0x1d8;
      lVar6 = param_7 + (long)*param_8_00 * 0x28;
      if (*(int *)(lVar6 + (long)*param_2 * 4) +
          *(int *)(param_7 + (long)*param_2 * 0x28 + (long)*param_8 * 4) <
          *(int *)(lVar6 + (long)iVar2 * 4) +
          *(int *)(param_7 + (long)iVar2 * 0x28 + (long)*param_8 * 4)) {
        uVar1 = *(undefined *)(param_1 + 1);
        *(undefined8 *)param_1 = *(undefined8 *)param_2;
        *param_2 = iVar2;
        *(undefined *)(param_2 + 1) = uVar1;
      }
      return;
    }
    if (param_5 < param_4) {
      lVar7 = param_4 / 2;
      piVar3 = param_1 + lVar7 * 2;
      piVar5 = (int *)FUN_0002a7e0(param_2,param_3,piVar3);
      lVar6 = (long)piVar5 - (long)param_2 >> 3;
    }
    else {
      lVar6 = param_5 / 2;
      piVar5 = param_2 + lVar6 * 2;
      piVar3 = (int *)FUN_0002a870(param_1,param_2,piVar5);
      lVar7 = (long)piVar3 - (long)param_1 >> 3;
    }
    param_4 = param_4 - lVar7;
    piVar4 = (int *)FUN_00017ff0(piVar3,param_2,piVar5);
    FUN_0002a900(param_1,piVar3,piVar4,lVar7,lVar6);
    param_5 = param_5 - lVar6;
    param_2 = piVar5;
    param_1 = piVar4;
  }
  return;
}


