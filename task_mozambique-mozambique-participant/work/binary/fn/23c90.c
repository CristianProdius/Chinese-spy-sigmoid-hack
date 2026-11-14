// ===== FUNC 23c90 size=740

void FUN_00023c90(long *param_1,ulong param_2)

{
  long lVar1;
  undefined8 *puVar2;
  long *plVar3;
  bool bVar4;
  long *plVar5;
  undefined *puVar6;
  undefined *puVar7;
  ulong uVar8;
  ulong uVar9;
  uint uVar10;
  uint uVar11;
  ulong uVar12;
  
  if (param_2 == 0) {
    puVar2 = (undefined8 *)*param_1;
    if (*(code **)*puVar2 == FUN_0001ae00) {
      plVar3 = (long *)puVar2[1];
      lVar1 = plVar3[1];
      plVar5 = (long *)*plVar3;
      if (plVar5 == plVar3 + 2) {
        uVar8 = 0xf;
      }
      else {
        uVar8 = plVar3[2];
      }
      if (uVar8 < lVar1 + 1U) {
        FUN_000b0b90(plVar3,lVar1,0,0,1);
        plVar5 = (long *)*plVar3;
      }
      *(undefined *)((long)plVar5 + lVar1) = 0x30;
      plVar3[1] = lVar1 + 1U;
      *(undefined *)(*plVar3 + 1 + lVar1) = 0;
      return;
    }
                    /* WARNING: Could not recover jumptable at 0x00023f29. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)*puVar2)(puVar2,0x30);
    return;
  }
  plVar3 = param_1 + 2;
  puVar7 = (undefined *)((long)param_1 + 0x11);
  uVar12 = 1;
  uVar8 = param_2;
  if (param_2 < 10) {
LAB_00023db6:
    puVar7[-1] = (char)uVar8 + '0';
  }
  else {
    puVar7 = (undefined *)((long)param_1 + 0x12);
    uVar12 = 2;
    if (99 < param_2) {
      if (param_2 < 1000) {
        uVar12 = 3;
        uVar8 = param_2 / 100;
        puVar7 = (undefined *)((long)param_1 + 0x11);
        lVar1 = (param_2 % 100) * 2;
        *(char *)((long)param_1 + 0x12) =
             "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
             [lVar1];
        *(undefined *)((long)param_1 + 0x11) = (&DAT_000e24a0)[lVar1];
        goto LAB_00023db6;
      }
      uVar11 = 1;
      if (param_2 < 10000) {
        uVar12 = 4;
        uVar8 = param_2 / 100;
        puVar7 = (undefined *)((long)param_1 + 0x12);
        lVar1 = (param_2 % 100) * 2;
        *(char *)((long)param_1 + 0x13) =
             "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
             [lVar1];
        *(undefined *)((long)param_1 + 0x12) = (&DAT_000e24a0)[lVar1];
      }
      else {
        do {
          uVar10 = uVar11;
          uVar11 = uVar10 + 4;
          if (uVar8 < 100000) goto LAB_00023d42;
          if (uVar8 < 1000000) {
            uVar11 = uVar10 + 5;
            goto LAB_00023d42;
          }
          if (uVar8 < 10000000) {
            uVar11 = uVar10 + 6;
            goto LAB_00023d42;
          }
          bVar4 = 99999999 < uVar8;
          uVar8 = uVar8 / 10000;
        } while (bVar4);
        uVar11 = uVar10 + 7;
LAB_00023d42:
        uVar12 = (ulong)uVar11;
        puVar6 = (undefined *)((long)plVar3 + uVar12);
        do {
          uVar9 = param_2;
          puVar7 = puVar6 + -2;
          uVar8 = uVar9 / 100;
          lVar1 = (uVar9 % 100) * 2;
          puVar6[-1] = "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
                       [lVar1];
          *puVar7 = (&DAT_000e24a0)[lVar1];
          puVar6 = puVar7;
          param_2 = uVar8;
        } while (9999 < uVar9);
        if (uVar9 < 1000) goto LAB_00023db6;
      }
    }
    puVar7[-1] = "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
                 [uVar8 * 2];
    puVar7[-2] = (&DAT_000e24a0)[uVar8 * 2];
  }
  param_1 = (long *)*param_1;
  if (*(code **)(*param_1 + 8) != FUN_0001ac60) {
                    /* WARNING: Could not recover jumptable at 0x00023f1a. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 8))(param_1,plVar3,uVar12);
    return;
  }
  if (uVar12 <= 0x3fffffffffffffffU - *(long *)(param_1[1] + 8)) {
    FUN_000b2500(param_1[1],plVar3,uVar12);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append");
}


