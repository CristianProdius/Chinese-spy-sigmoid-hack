// ===== FUNC 2cc00 size=379

void FUN_0002cc00(long param_1,long param_2,undefined8 param_3,long param_4,long param_5)

{
  double *pdVar1;
  double dVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  
  while( true ) {
    if (param_4 == 0) {
      return;
    }
    if (param_5 == 0) break;
    if (param_4 + param_5 == 2) {
      dVar2 = *(double *)(param_2 + 0x158);
      pdVar1 = (double *)(param_1 + 0x158);
      if (NAN(dVar2) || NAN(*pdVar1)) {
        return;
      }
      if (dVar2 == *pdVar1) {
        if (*(int *)(param_1 + 0x120) <= *(int *)(param_2 + 0x120)) {
          return;
        }
      }
      else if (dVar2 < *pdVar1 || dVar2 == *pdVar1) {
        return;
      }
      FUN_0002c690(param_1,param_2);
      return;
    }
    if (param_5 < param_4) {
      lVar7 = param_4 / 2;
      lVar3 = lVar7 * 0x160 + param_1;
      lVar8 = FUN_0001a930(param_2,param_3,lVar3);
      lVar4 = (lVar8 - param_2 >> 5) * 0x2e8ba2e8ba2e8ba3;
      lVar5 = param_2;
      lVar6 = param_1;
      param_2 = lVar8;
    }
    else {
      lVar4 = param_5 / 2;
      lVar8 = lVar4 * 0x160 + param_2;
      lVar3 = FUN_0001a9c0(param_1,param_2,lVar8);
      lVar7 = (lVar3 - param_1 >> 5) * 0x2e8ba2e8ba2e8ba3;
      lVar5 = param_2;
      lVar6 = param_1;
      param_2 = lVar8;
    }
    param_1 = FUN_0002ca30(lVar3,lVar5,param_2);
    param_4 = param_4 - lVar7;
    FUN_0002cc00(lVar6,lVar3,param_1,lVar7,lVar4);
    param_5 = param_5 - lVar4;
  }
  return;
}


