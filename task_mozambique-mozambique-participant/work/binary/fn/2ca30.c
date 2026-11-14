// ===== FUNC 2ca30 size=464

long FUN_0002ca30(long param_1,long param_2,long param_3)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  long local_48;
  
  lVar2 = param_3;
  if ((param_1 != param_2) && (lVar2 = param_1, param_2 != param_3)) {
    lVar2 = param_1 + (param_3 - param_2);
    lVar5 = param_3 - param_1 >> 5;
    lVar3 = param_2 - param_1 >> 5;
    lVar6 = lVar5 * 0x2e8ba2e8ba2e8ba3;
    lVar4 = lVar3 * 0x2e8ba2e8ba2e8ba3;
    lVar1 = param_2;
    if (lVar5 * -0x2e8ba2e8ba2e8ba3 + lVar3 * 0x5d1745d1745d1746 == 0) {
      do {
        lVar2 = param_1 + 0x160;
        FUN_0002c690(param_1,lVar1);
        param_1 = lVar2;
        lVar1 = lVar1 + 0x160;
      } while (param_2 != lVar2);
      return param_2;
    }
    lVar3 = lVar6 + lVar3 * -0x2e8ba2e8ba2e8ba3;
    lVar1 = lVar4;
    lVar5 = lVar6;
    local_48 = param_1;
    if (lVar3 <= lVar4) goto LAB_0002cb27;
    while( true ) {
      lVar4 = lVar1 * 0x160 + local_48;
      if (0 < lVar3) {
        lVar7 = 0;
        lVar5 = local_48;
        do {
          lVar7 = lVar7 + 1;
          FUN_0002c690(lVar5,lVar4);
          lVar4 = lVar4 + 0x160;
          lVar5 = lVar5 + 0x160;
        } while (lVar3 != lVar7);
        local_48 = local_48 + lVar3 * 0x160;
      }
      if (lVar6 % lVar1 == 0) break;
      lVar4 = lVar1 - lVar6 % lVar1;
      lVar6 = lVar1;
      while (lVar3 = lVar6 - lVar4, lVar1 = lVar4, lVar5 = lVar6, lVar3 <= lVar4) {
LAB_0002cb27:
        lVar6 = lVar3;
        lVar1 = local_48 + lVar5 * 0x160;
        local_48 = lVar1 + lVar6 * -0x160;
        if (0 < lVar4) {
          lVar7 = 0;
          lVar3 = local_48;
          do {
            lVar3 = lVar3 + -0x160;
            lVar1 = lVar1 + -0x160;
            lVar7 = lVar7 + 1;
            FUN_0002c690(lVar3,lVar1);
          } while (lVar4 != lVar7);
          local_48 = local_48 + lVar4 * -0x160;
        }
        lVar4 = lVar5 % lVar6;
        if (lVar4 == 0) {
          return lVar2;
        }
      }
    }
  }
  return lVar2;
}


