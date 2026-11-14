// ===== FUNC 23fa0 size=891

void FUN_00023fa0(long *param_1,ulong param_2)

{
  long *plVar1;
  long lVar2;
  undefined8 *puVar3;
  bool bVar4;
  uint uVar5;
  undefined *puVar6;
  undefined *puVar7;
  ulong uVar8;
  ulong uVar9;
  uint uVar10;
  long lVar11;
  int iVar12;
  int iVar13;
  ulong uVar14;
  
  if (param_2 == 0) {
    puVar3 = (undefined8 *)*param_1;
    if (*(code **)*puVar3 == FUN_0001ae00) {
      FUN_000b1530(puVar3[1],0x30);
      return;
    }
                    /* WARNING: Could not recover jumptable at 0x000242bd. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)*puVar3)(puVar3,0x30);
    return;
  }
  plVar1 = param_1 + 2;
  if ((long)param_2 < 0) {
    uVar8 = -param_2;
    *(undefined *)(param_1 + 2) = 0x2d;
    puVar7 = (undefined *)((long)param_1 + 0x12);
    uVar14 = 2;
    if (8 < uVar8 && param_2 != 0xfffffffffffffff7) {
      puVar7 = (undefined *)((long)param_1 + 0x13);
      uVar14 = 3;
      if (0x62 < uVar8 && param_2 != 0xffffffffffffff9d) {
        lVar11 = (long)param_1 + 0x14;
        uVar14 = 4;
        uVar9 = uVar8;
        if (uVar8 < 999 || param_2 == 0xfffffffffffffc19) goto LAB_00024217;
        uVar14 = uVar8;
        iVar13 = 1;
        if (0x270e < uVar8 && param_2 != 0xffffffffffffd8f1) {
          do {
            iVar12 = iVar13;
            iVar13 = iVar12 + 4;
            if (uVar14 < 100000) goto LAB_00024124;
            if (uVar14 < 1000000) {
              iVar13 = iVar12 + 5;
              goto LAB_00024124;
            }
            if (uVar14 < 10000000) {
              iVar13 = iVar12 + 6;
              goto LAB_00024124;
            }
            bVar4 = 99999999 < uVar14;
            uVar14 = uVar14 / 10000;
          } while (bVar4);
          iVar13 = iVar12 + 7;
LAB_00024124:
          uVar14 = (ulong)(iVar13 + 1);
          goto LAB_00024128;
        }
        lVar11 = (long)param_1 + 0x15;
        uVar14 = 5;
        param_2 = uVar8;
LAB_000242e5:
        uVar8 = param_2 / 100;
        puVar7 = (undefined *)(lVar11 + -2);
        lVar2 = (param_2 % 100) * 2;
        *(char *)(lVar11 + -1) =
             "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
             [lVar2];
        *(undefined *)(lVar11 + -2) = (&DAT_000e23c0)[lVar2];
      }
LAB_00024196:
      puVar7[-1] = "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
                   [uVar8 * 2];
      puVar7[-2] = (&DAT_000e23c0)[uVar8 * 2];
      goto LAB_000241a7;
    }
  }
  else {
    puVar7 = (undefined *)((long)param_1 + 0x11);
    uVar14 = 1;
    uVar8 = param_2;
    if (9 < param_2) {
      puVar7 = (undefined *)((long)param_1 + 0x12);
      uVar14 = 2;
      if (param_2 < 100) goto LAB_00024196;
      lVar11 = (long)param_1 + 0x13;
      uVar14 = 3;
      uVar9 = param_2;
      if (param_2 < 1000) {
LAB_00024217:
        uVar8 = uVar9 / 100;
        puVar7 = (undefined *)(lVar11 + -2);
        lVar2 = (uVar9 % 100) * 2;
        *(char *)(lVar11 + -1) =
             "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
             [lVar2];
        *(undefined *)(lVar11 + -2) = (&DAT_000e23c0)[lVar2];
      }
      else {
        uVar5 = 1;
        if (param_2 < 10000) {
          lVar11 = (long)param_1 + 0x14;
          uVar14 = 4;
          goto LAB_000242e5;
        }
        do {
          uVar10 = uVar5;
          if (param_2 < 100000) {
            uVar14 = (ulong)(uVar10 + 4);
            goto LAB_00024128;
          }
          if (param_2 < 1000000) {
            uVar14 = (ulong)(uVar10 + 5);
            goto LAB_00024128;
          }
          if (param_2 < 10000000) {
            uVar14 = (ulong)(uVar10 + 6);
            goto LAB_00024128;
          }
          bVar4 = 99999999 < param_2;
          param_2 = param_2 / 10000;
          uVar5 = uVar10 + 4;
        } while (bVar4);
        uVar14 = (ulong)(uVar10 + 7);
LAB_00024128:
        puVar6 = (undefined *)((long)plVar1 + uVar14);
        do {
          uVar9 = uVar8;
          puVar7 = puVar6 + -2;
          uVar8 = uVar9 / 100;
          lVar11 = (uVar9 % 100) * 2;
          puVar6[-1] = "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
                       [lVar11];
          *puVar7 = (&DAT_000e23c0)[lVar11];
          puVar6 = puVar7;
        } while (9999 < uVar9);
        if (999 < uVar9) goto LAB_00024196;
      }
    }
  }
  puVar7[-1] = (char)uVar8 + '0';
LAB_000241a7:
  param_1 = (long *)*param_1;
  if (*(code **)(*param_1 + 8) != FUN_0001ac60) {
                    /* WARNING: Could not recover jumptable at 0x0002427f. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_1 + 8))(param_1,plVar1,uVar14);
    return;
  }
  if (uVar14 <= 0x3fffffffffffffffU - *(long *)(param_1[1] + 8)) {
    FUN_000b2500(param_1[1],plVar1,uVar14);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append");
}


