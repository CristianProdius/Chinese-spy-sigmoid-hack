// ===== FUNC 191f0 size=1970

undefined8 *
FUN_000191f0(undefined8 *param_1,undefined4 param_2,undefined8 *param_3,undefined8 *param_4)

{
  undefined8 uVar1;
  bool bVar2;
  undefined auVar3 [16];
  undefined auVar4 [16];
  long *plVar5;
  char cVar6;
  long lVar7;
  ulong uVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  ulong uVar13;
  long in_FS_OFFSET;
  undefined *local_e8;
  long local_e0;
  undefined local_d8;
  undefined7 uStack_d7;
  undefined *local_c8;
  ulong local_c0;
  undefined local_b8;
  undefined7 uStack_b7;
  long *local_a8;
  ulong local_a0;
  long local_98 [2];
  long *local_88;
  int local_80;
  undefined4 uStack_7c;
  long local_78 [2];
  long *local_68;
  int local_60;
  undefined4 uStack_5c;
  long local_58 [3];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_00018b10(&local_a8,&DAT_000e3155);
  uVar13 = param_3[1];
  if (uVar13 < 10) {
    iVar10 = 1;
  }
  else if (uVar13 < 100) {
    iVar10 = 2;
  }
  else if (uVar13 < 1000) {
    iVar10 = 3;
  }
  else if (uVar13 < 10000) {
    iVar10 = 4;
  }
  else {
    uVar8 = uVar13;
    iVar10 = 1;
    do {
      iVar9 = iVar10;
      iVar10 = iVar9 + 4;
      if (uVar8 < 100000) goto LAB_000192ca;
      if (uVar8 < 1000000) {
        iVar10 = iVar9 + 5;
        goto LAB_000192ca;
      }
      if (uVar8 < 10000000) {
        iVar10 = iVar9 + 6;
        goto LAB_000192ca;
      }
      bVar2 = 99999999 < uVar8;
      uVar8 = uVar8 / 10000;
    } while (bVar2);
    iVar10 = iVar9 + 7;
  }
LAB_000192ca:
  local_68 = local_58;
                    /* try { // try from 000192ec to 000192f0 has its CatchHandler @ 000199e5 */
  FUN_000b0800(&local_68,iVar10,0);
  plVar5 = local_68;
  uVar11 = local_60 - 1;
  uVar8 = uVar13;
  if (99 < uVar13) {
    do {
      auVar3._8_8_ = 0;
      auVar3._0_8_ = uVar8 >> 2;
      uVar13 = (uVar8 >> 2) / 0x19;
      lVar7 = uVar8 + ((SUB168(auVar3 * ZEXT816(0x28f5c28f5c28f5c3),8) & 0xfffffffffffffffc) +
                      uVar13) * -0x14;
      cVar6 = (&DAT_000e2660)[lVar7 * 2];
      *(char *)((long)local_68 + (ulong)uVar11) =
           "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
           [lVar7 * 2];
      uVar12 = uVar11 - 1;
      uVar11 = uVar11 - 2;
      *(char *)((long)local_68 + (ulong)uVar12) = cVar6;
      bVar2 = 9999 < uVar8;
      uVar8 = uVar13;
    } while (bVar2);
  }
  cVar6 = (char)uVar13 + '0';
  if (9 < uVar13) {
    *(char *)((long)local_68 + 1) =
         "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
         [uVar13 * 2];
    cVar6 = (&DAT_000e2660)[uVar13 * 2];
  }
  *(char *)plVar5 = cVar6;
  uVar13 = param_3[2] + 1;
  if (uVar13 < 10) {
    iVar10 = 1;
  }
  else if (uVar13 < 100) {
    iVar10 = 2;
  }
  else if (uVar13 < 1000) {
    iVar10 = 3;
  }
  else if (uVar13 < 10000) {
    iVar10 = 4;
  }
  else {
    uVar8 = uVar13;
    iVar10 = 1;
    do {
      iVar9 = iVar10;
      iVar10 = iVar9 + 4;
      if (uVar8 < 100000) goto LAB_00019412;
      if (uVar8 < 1000000) {
        iVar10 = iVar9 + 5;
        goto LAB_00019412;
      }
      if (uVar8 < 10000000) {
        iVar10 = iVar9 + 6;
        goto LAB_00019412;
      }
      bVar2 = 99999999 < uVar8;
      uVar8 = uVar8 / 10000;
    } while (bVar2);
    iVar10 = iVar9 + 7;
  }
LAB_00019412:
  local_88 = local_78;
                    /* try { // try from 00019434 to 00019438 has its CatchHandler @ 000199ed */
  FUN_000b0800(&local_88,iVar10,0);
  plVar5 = local_88;
  uVar11 = local_80 - 1;
  uVar8 = uVar13;
  if (99 < uVar13) {
    do {
      auVar4._8_8_ = 0;
      auVar4._0_8_ = uVar8 >> 2;
      uVar13 = (uVar8 >> 2) / 0x19;
      lVar7 = uVar8 + ((SUB168(auVar4 * ZEXT816(0x28f5c28f5c28f5c3),8) & 0xfffffffffffffffc) +
                      uVar13) * -0x14;
      cVar6 = (&DAT_000e2660)[lVar7 * 2];
      *(char *)((long)local_88 + (ulong)uVar11) =
           "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
           [lVar7 * 2];
      uVar12 = uVar11 - 1;
      uVar11 = uVar11 - 2;
      *(char *)((long)local_88 + (ulong)uVar12) = cVar6;
      bVar2 = 9999 < uVar8;
      uVar8 = uVar13;
    } while (bVar2);
  }
  cVar6 = (char)uVar13 + '0';
  if (9 < uVar13) {
    cVar6 = (&DAT_000e2660)[uVar13 * 2];
    *(char *)((long)local_88 + 1) =
         "0010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899"
         [uVar13 * 2];
  }
  *(char *)plVar5 = cVar6;
  local_c0 = 0;
  local_b8 = 0;
  local_c8 = &local_b8;
                    /* try { // try from 00019504 to 000195c2 has its CatchHandler @ 00019a15 */
  FUN_000b1110(&local_c8,CONCAT44(uStack_5c,local_60) + CONCAT44(uStack_7c,local_80) + 0x12);
  if (0x3fffffffffffffff - local_c0 < 9) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(&local_c8," at line ",9);
  if (0x3fffffffffffffff - local_c0 < CONCAT44(uStack_7c,local_80)) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",local_88);
  }
  FUN_000b2500(&local_c8);
  if (0x3fffffffffffffff - local_c0 < 9) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(&local_c8,", column ",9);
  if (0x3fffffffffffffff - local_c0 < CONCAT44(uStack_5c,local_60)) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 000199bc to 000199e4 has its CatchHandler @ 00019a15 */
    FUN_00015e26("basic_string::append",local_68);
  }
  FUN_000b2500(&local_c8);
  if (local_88 != local_78) {
    thunk_FUN_000d36e0(local_88,local_78[0] + 1);
  }
  if (local_68 != local_58) {
    thunk_FUN_000d36e0(local_68,local_58[0] + 1);
  }
                    /* try { // try from 0001960b to 0001960f has its CatchHandler @ 00019a05 */
  FUN_00018b10(&local_88,"parse_error");
                    /* try { // try from 0001961e to 00019622 has its CatchHandler @ 000199f5 */
  FUN_0001bf50(&local_68,&local_88,param_2);
  local_e0 = 0;
  local_d8 = 0;
  local_e8 = &local_d8;
                    /* try { // try from 0001966b to 0001977f has its CatchHandler @ 00019a0d */
  FUN_000b1110(&local_e8,local_c0 + CONCAT44(uStack_5c,local_60) + 0xd + local_a0 + param_4[1]);
  if (0x3fffffffffffffffU - local_e0 < CONCAT44(uStack_5c,local_60)) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",local_68);
  }
  FUN_000b2500(&local_e8);
  if (0x3fffffffffffffffU - local_e0 < 0xb) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(&local_e8,"parse error",0xb);
  if (0x3fffffffffffffffU - local_e0 < local_c0) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",local_c8);
  }
  FUN_000b2500(&local_e8);
  if (0x3fffffffffffffffU - local_e0 < 2) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(&local_e8,&DAT_000e6ddf,2);
  if (0x3fffffffffffffffU - local_e0 < local_a0) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",local_a8);
  }
  FUN_000b2500(&local_e8);
  if (0x3fffffffffffffffU - local_e0 < (ulong)param_4[1]) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00019974 to 000199b4 has its CatchHandler @ 00019a0d */
    FUN_00015e26("basic_string::append",*param_4);
  }
  FUN_000b2500(&local_e8);
  if (local_68 != local_58) {
    thunk_FUN_000d36e0(local_68,local_58[0] + 1);
  }
  if (local_88 != local_78) {
    thunk_FUN_000d36e0(local_88,local_78[0] + 1);
  }
  if (local_c8 != &local_b8) {
    thunk_FUN_000d36e0(local_c8,CONCAT71(uStack_b7,local_b8) + 1);
  }
  if (local_a8 != local_98) {
    thunk_FUN_000d36e0(local_a8,local_98[0] + 1);
  }
  uVar1 = *param_3;
  *param_1 = &PTR_FUN_0011ba70;
  *(undefined4 *)(param_1 + 1) = param_2;
                    /* try { // try from 0001981d to 00019821 has its CatchHandler @ 000199fd */
  FUN_00053220(param_1 + 2,local_e8);
  param_1[4] = uVar1;
  *param_1 = &PTR_FUN_0011ba98;
  if (local_e8 != &local_d8) {
    thunk_FUN_000d36e0(local_e8,CONCAT71(uStack_d7,local_d8) + 1);
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


