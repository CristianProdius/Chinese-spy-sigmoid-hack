// ===== FUNC 39d80 size=629

void FUN_00039d80(long param_1,long param_2,long param_3)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  long local_48;
  
  lVar5 = param_2 - param_1;
  lVar2 = (lVar5 >> 5) * 0x2e8ba2e8ba2e8ba3;
  lVar7 = param_1;
  if (lVar5 < 0x841) {
    FUN_0001ae80(param_1,param_2);
    return;
  }
  do {
    lVar4 = lVar7 + 0x9a0;
    FUN_0001ae80(lVar7,lVar4);
    lVar7 = lVar4;
  } while (0x840 < param_2 - lVar4);
  FUN_0001ae80(lVar4,param_2);
  if (0x9a0 < lVar5) {
    lVar7 = 7;
    do {
      lVar4 = lVar7 * 2;
      lVar6 = lVar2;
      lVar1 = param_3;
      lVar8 = param_1;
      if (SBORROW8(lVar2,lVar4) == lVar2 + lVar7 * -2 < 0) {
        lVar9 = param_1;
        do {
          lVar8 = lVar9 + lVar7 * 0x2c0;
          lVar6 = lVar7 * -0x160 + lVar8;
          lVar1 = FUN_00039820(lVar9,lVar6,lVar6,lVar8,lVar1);
          lVar3 = param_2 - lVar8 >> 5;
          lVar6 = lVar3 * 0x2e8ba2e8ba2e8ba3;
          lVar9 = lVar8;
        } while (lVar4 == lVar6 || SBORROW8(lVar4,lVar6) != lVar4 + lVar3 * -0x2e8ba2e8ba2e8ba3 < 0)
        ;
      }
      local_48 = lVar7 * 4;
      if (lVar7 <= lVar6) {
        lVar6 = lVar7;
      }
      lVar6 = lVar6 * 0x160 + lVar8;
      FUN_00039820(lVar8,lVar6,lVar6,param_2,lVar1);
      lVar6 = lVar2;
      lVar1 = param_1;
      lVar8 = param_3;
      if (local_48 <= lVar2) {
        lVar9 = param_3;
        do {
          lVar8 = lVar9 + lVar7 * 0x580;
          lVar6 = lVar7 * -0x2c0 + lVar8;
          lVar1 = FUN_000392b0(lVar9,lVar6,lVar6,lVar8,lVar1);
          lVar3 = (param_3 + lVar5) - lVar8 >> 5;
          lVar6 = lVar3 * 0x2e8ba2e8ba2e8ba3;
          lVar9 = lVar8;
        } while (local_48 == lVar6 ||
                 SBORROW8(local_48,lVar6) != local_48 + lVar3 * -0x2e8ba2e8ba2e8ba3 < 0);
      }
      if (lVar4 <= lVar6) {
        lVar6 = lVar4;
      }
      lVar7 = lVar6 * 0x160 + lVar8;
      FUN_000392b0(lVar8,lVar7,lVar7,param_3 + lVar5,lVar1);
      lVar7 = local_48;
    } while (local_48 < lVar2);
  }
  return;
}


