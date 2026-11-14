// ===== FUNC 23340 size=332

long * FUN_00023340(long *param_1,long param_2)

{
  byte bVar1;
  byte *pbVar2;
  long lVar3;
  size_t sVar4;
  long *plVar5;
  ulong uVar6;
  byte *pbVar7;
  long in_FS_OFFSET;
  undefined8 local_49;
  undefined local_41;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  *(undefined *)(param_1 + 2) = 0;
  *param_1 = (long)(param_1 + 2);
  pbVar2 = *(byte **)(param_2 + 0x40);
  pbVar7 = *(byte **)(param_2 + 0x38);
  param_1[1] = 0;
  for (; pbVar2 != pbVar7; pbVar7 = pbVar7 + 1) {
    while (bVar1 = *pbVar7, bVar1 < 0x20) {
      local_49 = 0;
      local_41 = 0;
      __snprintf_chk(&local_49,9,2,9,"<U+%.4X>",(int)(char)bVar1);
      sVar4 = strlen((char *)&local_49);
      if (0x3fffffffffffffffU - param_1[1] < sVar4) {
                    /* WARNING: Subroutine does not return */
        FUN_00015e26("basic_string::append");
      }
                    /* try { // try from 000233ef to 00023492 has its CatchHandler @ 00023498 */
      FUN_000b2500(param_1,&local_49);
      pbVar7 = pbVar7 + 1;
      if (pbVar2 == pbVar7) goto LAB_0002343d;
    }
    lVar3 = param_1[1];
    plVar5 = (long *)*param_1;
    if (param_1 + 2 == plVar5) {
      uVar6 = 0xf;
    }
    else {
      uVar6 = param_1[2];
    }
    if (uVar6 < lVar3 + 1U) {
      FUN_000b0b90(param_1,lVar3,0,0,1);
      plVar5 = (long *)*param_1;
    }
    *(byte *)((long)plVar5 + lVar3) = bVar1;
    param_1[1] = lVar3 + 1U;
    *(undefined *)(*param_1 + 1 + lVar3) = 0;
  }
LAB_0002343d:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


