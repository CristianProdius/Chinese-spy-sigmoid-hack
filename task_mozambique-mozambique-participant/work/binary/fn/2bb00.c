// ===== FUNC 2bb00 size=702

void FUN_0002bb00(long param_1,long param_2,long param_3,undefined8 param_4,undefined8 param_5,
                 undefined8 param_6,undefined8 param_7,undefined8 param_8_00,undefined8 param_8)

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
  
  lVar4 = param_2 - param_1;
  lVar1 = lVar4 >> 3;
  lVar5 = param_1;
  if (lVar4 < 0x31) {
    FUN_00025060(param_1);
    return;
  }
  do {
    lVar7 = lVar5 + 0x38;
    FUN_00025060(lVar5,lVar7);
    lVar5 = lVar7;
  } while (0x30 < param_2 - lVar7);
  FUN_00025060(lVar7,param_2);
  if (0x38 < lVar4) {
    lVar5 = 7;
    do {
      lVar7 = lVar5 * 2;
      lVar3 = lVar1;
      lVar2 = param_3;
      lVar8 = param_1;
      if (SBORROW8(lVar1,lVar7) == lVar1 + lVar5 * -2 < 0) {
        lVar6 = param_1;
        do {
          lVar8 = lVar6 + lVar5 * 0x10;
          lVar3 = lVar8 + lVar5 * -8;
          lVar2 = FUN_0002b900(lVar6,lVar3,lVar3,lVar8,lVar2,param_6,param_7,param_8_00,param_8);
          lVar3 = param_2 - lVar8 >> 3;
          lVar6 = lVar8;
        } while (lVar7 <= lVar3);
      }
      if (lVar5 <= lVar3) {
        lVar3 = lVar5;
      }
      lVar6 = lVar5 * 4;
      lVar3 = lVar8 + lVar3 * 8;
      FUN_0002b900(lVar8,lVar3,lVar3,param_2,lVar2,param_6,param_7,param_8_00,param_8);
      lVar3 = lVar1;
      lVar2 = param_1;
      lVar8 = param_3;
      if (lVar6 <= lVar1) {
        lVar9 = param_3;
        do {
          lVar8 = lVar9 + lVar5 * 0x20;
          lVar3 = lVar8 + lVar5 * -0x10;
          lVar2 = FUN_0002ba00(lVar9,lVar3,lVar3,lVar8,lVar2,param_6,param_7,param_8_00,param_8);
          lVar3 = (param_3 + lVar4) - lVar8 >> 3;
          lVar9 = lVar8;
        } while (lVar6 <= lVar3);
      }
      if (lVar3 < lVar7) {
        lVar7 = lVar3;
      }
      lVar5 = lVar8 + lVar7 * 8;
      FUN_0002ba00(lVar8,lVar5,lVar5,param_3 + lVar4,lVar2,param_6,param_7,param_8_00,param_8);
      lVar5 = lVar6;
    } while (lVar6 < lVar1);
  }
  return;
}


