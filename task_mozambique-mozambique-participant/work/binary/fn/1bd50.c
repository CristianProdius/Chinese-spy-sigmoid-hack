// ===== FUNC 1bd50 size=430

long * FUN_0001bd50(long *param_1,ulong param_2)

{
  char cVar1;
  bool bVar2;
  undefined auVar3 [16];
  uint uVar4;
  ulong uVar5;
  long lVar6;
  int iVar7;
  int iVar8;
  char *pcVar9;
  uint uVar10;
  
  if (9 < param_2) {
    if (param_2 < 100) {
      *param_1 = (long)(param_1 + 2);
      FUN_000b0800(param_1,2,0);
      pcVar9 = (char *)*param_1;
    }
    else {
      if (param_2 < 1000) {
        iVar8 = 3;
      }
      else if (param_2 < 10000) {
        iVar8 = 4;
      }
      else {
        uVar5 = param_2;
        iVar8 = 1;
        do {
          iVar7 = iVar8;
          iVar8 = iVar7 + 4;
          if (uVar5 < 100000) goto LAB_0001bde2;
          if (uVar5 < 1000000) {
            iVar8 = iVar7 + 5;
            *param_1 = (long)(param_1 + 2);
            goto LAB_0001bdea;
          }
          if (uVar5 < 10000000) {
            iVar8 = iVar7 + 6;
            goto LAB_0001bde2;
          }
          bVar2 = 99999999 < uVar5;
          uVar5 = uVar5 / 10000;
        } while (bVar2);
        iVar8 = iVar7 + 7;
      }
LAB_0001bde2:
      *param_1 = (long)(param_1 + 2);
LAB_0001bdea:
      FUN_000b0800(param_1,iVar8,0);
      pcVar9 = (char *)*param_1;
      uVar4 = *(int *)(param_1 + 1) - 1;
      do {
        uVar5 = param_2;
        auVar3._8_8_ = 0;
        auVar3._0_8_ = uVar5 >> 2;
        param_2 = (uVar5 >> 2) / 0x19;
        lVar6 = uVar5 + ((SUB168(auVar3 * ZEXT816(0x28f5c28f5c28f5c3),8) & 0xfffffffffffffffc) +
                        param_2) * -0x14;
        cVar1 = (&DAT_000e2660)[lVar6 * 2];
        pcVar9[uVar4] =
             "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
             [lVar6 * 2];
        uVar10 = uVar4 - 1;
        uVar4 = uVar4 - 2;
        pcVar9[uVar10] = cVar1;
      } while (9999 < uVar5);
      if (uVar5 < 1000) goto LAB_0001be9a;
    }
    cVar1 = (&DAT_000e2660)[param_2 * 2];
    pcVar9[1] = "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
                [param_2 * 2];
    *pcVar9 = cVar1;
    return param_1;
  }
  *param_1 = (long)(param_1 + 2);
  FUN_000b0800(param_1,1,0);
  pcVar9 = (char *)*param_1;
LAB_0001be9a:
  *pcVar9 = (char)param_2 + '0';
  return param_1;
}


