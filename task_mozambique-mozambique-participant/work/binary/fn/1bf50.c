// ===== FUNC 1bf50 size=980

long * FUN_0001bf50(long *param_1,undefined8 *param_2,uint param_3)

{
  long lVar1;
  uint uVar2;
  long lVar3;
  char *pcVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  char cVar9;
  ulong uVar10;
  long in_FS_OFFSET;
  uint local_74;
  long *local_68;
  ulong local_60;
  long local_58 [3];
  long local_40;
  ulong uVar8;
  
  uVar7 = -((int)param_3 >> 0x1f);
  uVar8 = (ulong)uVar7;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  uVar10 = (ulong)-param_3;
  if (0 < (int)param_3) {
    uVar10 = (ulong)param_3;
  }
  uVar5 = (uint)uVar10;
  if (uVar5 < 10) {
    local_68 = local_58;
    FUN_000b0800(&local_68,uVar7 + 1,0x2d);
    pcVar4 = (char *)((uVar8 & 0xff) + (long)local_68);
LAB_0001c230:
    cVar9 = (char)uVar5 + '0';
  }
  else {
    if (uVar5 < 100) {
      local_68 = local_58;
      FUN_000b0800(&local_68,uVar7 + 2,0x2d);
      pcVar4 = (char *)((uVar8 & 0xff) + (long)local_68);
    }
    else {
      if (uVar5 < 1000) {
        local_74 = 2;
        iVar6 = 3;
      }
      else if (uVar5 < 10000) {
        local_74 = 3;
        iVar6 = 4;
      }
      else {
        iVar6 = 5;
        if (uVar10 < 100000) {
LAB_0001c245:
          local_74 = iVar6 - 1;
        }
        else if (uVar10 < 1000000) {
          local_74 = 5;
LAB_0001c00b:
          iVar6 = local_74 + 1;
        }
        else {
          local_74 = 6;
          iVar6 = 7;
          if (9999999 < uVar10) {
            if (99999999 < uVar10) {
              if (uVar10 < 1000000000) {
                iVar6 = 9;
                goto LAB_0001c245;
              }
              local_74 = 9;
              goto LAB_0001c00b;
            }
            local_74 = 7;
            iVar6 = 8;
          }
        }
      }
      local_68 = local_58;
      FUN_000b0800(&local_68,iVar6 + uVar7,0x2d);
      pcVar4 = (char *)((uVar8 & 0xff) + (long)local_68);
      do {
        uVar5 = (uint)(uVar10 / 100);
        uVar2 = (uint)uVar10;
        uVar7 = (uVar2 + uVar5 * -100) * 2;
        cVar9 = "00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
                [uVar7];
        pcVar4[local_74] =
             "00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
             [uVar7 + 1];
        uVar7 = local_74 - 1;
        local_74 = local_74 - 2;
        pcVar4[uVar7] = cVar9;
        uVar10 = uVar10 / 100;
      } while (9999 < uVar2);
      if (uVar2 < 1000) goto LAB_0001c230;
    }
    cVar9 = "00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
            [uVar5 * 2];
    pcVar4[1] = "00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
                [uVar5 * 2 + 1];
  }
  *pcVar4 = cVar9;
  param_1[1] = 0;
  *(undefined *)(param_1 + 2) = 0;
  lVar1 = param_2[1];
  *param_1 = (long)(param_1 + 2);
                    /* try { // try from 0001c0dc to 0001c1bc has its CatchHandler @ 0001c341 */
  FUN_000b1110(param_1,local_60 + 0x13 + lVar1);
  if (0x3fffffffffffffffU - param_1[1] < 0x10) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0001c313 to 0001c340 has its CatchHandler @ 0001c341 */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(param_1,"[json.exception.",0x10);
  if (0x3fffffffffffffffU - param_1[1] < (ulong)param_2[1]) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",*param_2);
  }
  FUN_000b2500(param_1);
  lVar1 = param_1[1];
  lVar3 = *param_1;
  if (param_1 + 2 == (long *)lVar3) {
    uVar10 = 0xf;
  }
  else {
    uVar10 = param_1[2];
  }
  if (uVar10 < lVar1 + 1U) {
                    /* try { // try from 0001c280 to 0001c284 has its CatchHandler @ 0001c341 */
    FUN_000b0b90(param_1,lVar1,0,0,1);
    lVar3 = *param_1;
  }
  *(undefined *)(lVar3 + lVar1) = 0x2e;
  param_1[1] = lVar1 + 1U;
  *(undefined *)(*param_1 + 1 + lVar1) = 0;
  if (0x3fffffffffffffffU - param_1[1] < local_60) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",local_68);
  }
  FUN_000b2500(param_1);
  if (0x3fffffffffffffffU - param_1[1] < 2) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(param_1,"] ",2);
  if (local_68 != local_58) {
    thunk_FUN_000d36e0(local_68,local_58[0] + 1);
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


