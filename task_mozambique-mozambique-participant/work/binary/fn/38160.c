// ===== FUNC 38160 size=1761

void FUN_00038160(long param_1,char param_2,byte *param_3,undefined8 param_4,undefined8 param_5,
                 undefined8 param_6)

{
  long lVar1;
  char *pcVar2;
  char cVar3;
  byte bVar4;
  code *pcVar5;
  ulong *puVar6;
  int iVar7;
  undefined8 uVar8;
  long in_FS_OFFSET;
  byte **ppbVar9;
  undefined8 local_1f8;
  undefined8 uStack_1f0;
  undefined8 local_1e8;
  byte *local_1d8;
  long lStack_1d0;
  undefined8 local_1c8;
  long local_1c0;
  undefined8 local_1b8;
  char local_1b0;
  char local_1af;
  long local_1a8;
  undefined local_198 [32];
  undefined local_178 [32];
  undefined local_158 [32];
  undefined local_138 [16];
  undefined local_128 [2] [16];
  byte *local_108;
  long local_100;
  undefined8 local_f8;
  long local_f0;
  long local_e8;
  undefined4 local_e0;
  ulong *local_d8;
  int local_d0;
  undefined local_c8 [16];
  undefined4 local_b8;
  undefined8 local_b0;
  undefined4 local_a8;
  undefined local_a0 [16];
  char local_90;
  undefined local_88 [16];
  code *local_78;
  undefined8 local_70;
  char local_68;
  undefined local_60;
  undefined local_58 [8];
  long local_50;
  long local_40;
  
  lVar1 = param_1 + 0x28;
  cVar3 = *(char *)(param_1 + 200);
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (*(code **)(param_1 + 0x10) == (code *)0x0) {
    lStack_1d0 = 0;
    local_1c8 = 0;
    local_1c0 = 0;
    local_1b8 = 0;
    local_1b0 = '\0';
    local_1d8 = param_3;
    local_1af = cVar3;
    local_1a8 = lVar1;
                    /* try { // try from 0003849d to 000384a1 has its CatchHandler @ 000388cb */
    FUN_00036b10(param_1,&local_1d8);
    if (param_2 == '\0') {
LAB_000384ab:
      if (local_1b0 != '\0') goto LAB_00038744;
    }
    else {
                    /* try { // try from 00038673 to 0003869a has its CatchHandler @ 000388cb */
      iVar7 = FUN_00034bb0(lVar1);
      *(int *)(param_1 + 0x20) = iVar7;
      if (iVar7 == 0xf) goto LAB_000384ab;
      FUN_00018b10(local_158,"value");
                    /* try { // try from 000386b1 to 000386b5 has its CatchHandler @ 0003892c */
      FUN_000234b0(local_138,param_1,0xf,local_158);
      local_1e8 = *(undefined8 *)(param_1 + 0x58);
      local_1f8 = *(undefined8 *)(param_1 + 0x48);
      uStack_1f0 = *(undefined8 *)(param_1 + 0x50);
      ppbVar9 = &local_108;
                    /* try { // try from 000386e5 to 000386e9 has its CatchHandler @ 00038927 */
      FUN_000191f0(ppbVar9,0x65,&local_1f8,local_138);
                    /* try { // try from 000386fd to 00038701 has its CatchHandler @ 0003891d */
      FUN_00023340(local_178,lVar1);
      local_1b0 = '\x01';
      if (local_1af != '\0') {
                    /* try { // try from 00038918 to 0003891c has its CatchHandler @ 00038922 */
        uVar8 = FUN_00013710(ppbVar9);
        local_108 = (byte *)&PTR_FUN_0011ba98;
        FUN_0001a6b0(ppbVar9);
        FUN_000b07c0(local_138);
        FUN_000b07c0(local_158);
        FUN_00024350(&lStack_1d0);
                    /* WARNING: Subroutine does not return */
        FUN_000ddde0(uVar8);
                    /* catch() { ... } // from try @ 000386fd with catch @ 0003891d */
      }
      FUN_000b07c0(local_178);
      local_108 = (byte *)&PTR_FUN_0011ba98;
      FUN_0001a6b0(ppbVar9);
      FUN_000b07c0(local_138);
      FUN_000b07c0(local_158);
LAB_00038744:
      local_1f8._0_1_ = 9;
                    /* try { // try from 00038756 to 0003875a has its CatchHandler @ 000388cb */
      FUN_000210f0(&uStack_1f0,9);
      bVar4 = *param_3;
      *param_3 = (byte)local_1f8;
      uVar8 = *(undefined8 *)(param_3 + 8);
      *(undefined8 *)(param_3 + 8) = uStack_1f0;
      local_1f8 = CONCAT71(local_1f8._1_7_,bVar4);
      uStack_1f0 = uVar8;
      FUN_00024620(&uStack_1f0);
    }
    if (lStack_1d0 != 0) {
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        thunk_FUN_000d36e0(lStack_1d0,local_1c0 - lStack_1d0);
        return;
      }
      goto LAB_000387f2;
    }
  }
  else {
    local_138 = (undefined  [16])0x0;
    local_128[0] = ZEXT816(0);
                    /* try { // try from 000381db to 000381dc has its CatchHandler @ 000387f7 */
    (**(code **)(param_1 + 0x10))(local_138,param_1,2);
    pcVar5 = *(code **)*(undefined (*) [16])(param_1 + 0x10);
    local_70 = *(undefined8 *)(param_1 + 0x18);
    local_128[0] = *(undefined (*) [16])(param_1 + 0x10);
    local_100 = 0;
    local_f8 = 0;
    local_f0 = 0;
    local_e8 = 0;
    local_e0 = 0;
    local_d8 = (ulong *)0x0;
    local_d0 = 0;
    local_b8 = 0;
    local_b0 = 0;
    local_a8 = 0;
    local_90 = '\0';
    local_78 = (code *)0x0;
    local_c8 = (undefined  [16])0x0;
    local_a0 = (undefined  [16])0x0;
    local_88 = (undefined  [16])0x0;
    if (pcVar5 != (code *)0x0) {
      local_128[0] = (undefined  [16])0x0;
      local_88 = local_138;
      local_78 = pcVar5;
    }
    local_60 = 9;
    local_108 = param_3;
    local_68 = cVar3;
                    /* try { // try from 000382ee to 000382f2 has its CatchHandler @ 0003880e */
    FUN_000210f0(local_58,9);
    iVar7 = local_d0;
    puVar6 = local_d8;
    local_50 = lVar1;
    if (local_d8 == (ulong *)local_c8._0_8_) {
                    /* try { // try from 00038454 to 00038458 has its CatchHandler @ 000388c6 */
      FUN_00018750(&local_e8,local_d8,local_d0,1,param_5,param_6,&local_e8);
    }
    else {
      if (local_d0 == 0x3f) {
        local_d0 = 0;
        local_d8 = local_d8 + 1;
      }
      else {
        local_d0 = local_d0 + 1;
      }
      *puVar6 = *puVar6 | 1L << ((byte)iVar7 & 0x3f);
    }
    if ((code *)local_128[0]._0_8_ != (code *)0x0) {
      (*(code *)local_128[0]._0_8_)(local_138,local_138,3);
    }
    ppbVar9 = &local_108;
                    /* try { // try from 00038364 to 00038368 has its CatchHandler @ 00038804 */
    FUN_000352a0(param_1,ppbVar9);
    if (param_2 == '\0') {
LAB_00038372:
      if (local_90 != '\0') goto LAB_000385f0;
LAB_00038380:
      if (*param_3 == 9) {
        lStack_1d0 = *(long *)(param_3 + 8);
        *param_3 = 0;
        pcVar2 = (char *)(param_3 + 8);
        pcVar2[0] = '\0';
        pcVar2[1] = '\0';
        pcVar2[2] = '\0';
        pcVar2[3] = '\0';
        pcVar2[4] = '\0';
        pcVar2[5] = '\0';
        pcVar2[6] = '\0';
        pcVar2[7] = '\0';
        local_1d8 = Elf64_Ehdr_00000000.e_ident_pad;
        FUN_00024620(&lStack_1d0,9);
      }
      FUN_00024620(local_58,local_60);
      if (local_78 != (code *)0x0) {
        (*local_78)(local_88,local_88,3);
      }
    }
    else {
                    /* try { // try from 00038503 to 0003852f has its CatchHandler @ 00038804 */
      iVar7 = FUN_00034bb0(lVar1);
      *(int *)(param_1 + 0x20) = iVar7;
      if (iVar7 == 0xf) goto LAB_00038372;
      FUN_00018b10(local_178,"value");
                    /* try { // try from 00038548 to 0003854c has its CatchHandler @ 000388c1 */
      FUN_000234b0(local_158,param_1,0xf,local_178);
      local_1d8 = *(byte **)(param_1 + 0x48);
      lStack_1d0 = *(long *)(param_1 + 0x50);
      local_1c8 = *(undefined8 *)(param_1 + 0x58);
                    /* try { // try from 00038570 to 00038574 has its CatchHandler @ 000388bc */
      FUN_000191f0(local_138,0x65,&local_1d8,local_158);
                    /* try { // try from 00038580 to 00038584 has its CatchHandler @ 00038809 */
      FUN_00023340(local_198,lVar1);
      local_90 = '\x01';
      if (local_68 != '\0') {
                    /* try { // try from 000387ff to 00038803 has its CatchHandler @ 0003882f */
        uVar8 = FUN_00013710(local_138);
                    /* catch() { ... } // from try @ 00038364 with catch @ 00038804
                       catch() { ... } // from try @ 00038503 with catch @ 00038804
                       catch() { ... } // from try @ 00038602 with catch @ 00038804 */
        FUN_00024b40(ppbVar9);
                    /* WARNING: Subroutine does not return */
        FUN_000ddde0(uVar8);
      }
      FUN_000b07c0(local_198);
      local_138._0_8_ = &PTR_FUN_0011ba70;
      FUN_00049930(local_128);
      FUN_000411f0(local_138);
      FUN_000b07c0(local_158);
      FUN_000b07c0(local_178);
      if (local_90 == '\0') goto LAB_00038380;
LAB_000385f0:
      local_1d8._0_1_ = 9;
                    /* try { // try from 00038602 to 00038606 has its CatchHandler @ 00038804 */
      FUN_000210f0(&lStack_1d0,9);
      bVar4 = *param_3;
      *param_3 = (byte)local_1d8;
      lVar1 = *(long *)(param_3 + 8);
      *(long *)(param_3 + 8) = lStack_1d0;
      local_1d8 = (byte *)CONCAT71(local_1d8._1_7_,bVar4);
      lStack_1d0 = lVar1;
      FUN_00024620(&lStack_1d0);
      FUN_00024620(local_58,local_60);
      if (local_78 != (code *)0x0) {
        (*local_78)(local_88,local_88,3);
      }
    }
    if (local_c8._8_8_ != 0) {
      thunk_FUN_000d36e0(local_c8._8_8_,local_a0._0_8_ - local_c8._8_8_);
    }
    if (local_e8 != 0) {
      thunk_FUN_000d36e0(local_e8,local_c8._0_8_ - local_e8);
    }
    if (local_100 != 0) {
      thunk_FUN_000d36e0(local_100,local_f0 - local_100);
    }
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_000387f2:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


