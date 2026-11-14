// ===== FUNC 23ae0 size=392

void FUN_00023ae0(long *param_1,byte param_2)

{
  long lVar1;
  long *plVar2;
  undefined8 *puVar3;
  long *plVar4;
  ulong uVar5;
  ulong uVar6;
  ulong uVar7;
  
  if (param_2 == 0) {
    puVar3 = (undefined8 *)*param_1;
    if (*(code **)*puVar3 == FUN_0001ae00) {
      plVar2 = (long *)puVar3[1];
      lVar1 = plVar2[1];
      plVar4 = (long *)*plVar2;
      if (plVar4 == plVar2 + 2) {
        uVar7 = 0xf;
      }
      else {
        uVar7 = plVar2[2];
      }
      if (uVar7 < lVar1 + 1U) {
        FUN_000b0b90(plVar2,lVar1,0,0,1);
        plVar4 = (long *)*plVar2;
      }
      *(undefined *)((long)plVar4 + lVar1) = 0x30;
      plVar2[1] = lVar1 + 1U;
      *(undefined *)(*plVar2 + 1 + lVar1) = 0;
      return;
    }
                    /* WARNING: Could not recover jumptable at 0x00023c61. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)*puVar3)(puVar3,0x30);
    return;
  }
  uVar7 = (ulong)param_2;
  if (param_2 < 10) {
    uVar6 = 1;
  }
  else {
    if (uVar7 < 100) {
      *(char *)((long)param_1 + 0x11) =
           "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
           [uVar7 * 2];
      uVar6 = 2;
      *(undefined *)(param_1 + 2) = (&DAT_000e2580)[uVar7 * 2];
      goto LAB_00023b60;
    }
    uVar5 = (ulong)(param_2 >> 2) / 0x19;
    lVar1 = (uVar7 + uVar5 * -100) * 2;
    *(char *)((long)param_1 + 0x12) =
         "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
         [lVar1];
    uVar6 = 3;
    *(undefined *)((long)param_1 + 0x11) = (&DAT_000e2580)[lVar1];
    uVar7 = uVar5;
  }
  *(char *)(param_1 + 2) = (char)uVar7 + '0';
LAB_00023b60:
  plVar2 = (long *)*param_1;
  if (*(code **)(*plVar2 + 8) != FUN_0001ac60) {
                    /* WARNING: Could not recover jumptable at 0x00023c4f. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*plVar2 + 8))(plVar2,param_1 + 2);
    return;
  }
  if (uVar6 <= 0x3fffffffffffffffU - *(long *)(plVar2[1] + 8)) {
    FUN_000b2500(plVar2[1],param_1 + 2);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append");
}


