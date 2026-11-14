// ===== FUNC 26c80 size=1330

long FUN_00026c80(long param_1,undefined8 param_2,undefined8 param_3,int param_4,int *param_5,
                 undefined4 param_6,undefined param_7)

{
  int *piVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  undefined8 *puVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  int iVar10;
  long lVar11;
  int *piVar12;
  long lVar13;
  long in_FS_OFFSET;
  byte bVar14;
  undefined local_354 [4];
  undefined4 local_350;
  int local_34c [3];
  ulong local_340;
  undefined local_338 [16];
  int *local_328;
  int local_314 [3];
  undefined8 local_308;
  undefined8 uStack_300;
  undefined8 local_2f8;
  undefined local_2e8 [16];
  code *local_2d8;
  code *pcStack_2d0;
  undefined local_2c8 [16];
  long local_2b8;
  long local_2a8;
  char local_1a4;
  undefined local_1a0 [24];
  undefined local_188 [16];
  undefined local_178 [16];
  undefined local_168 [16];
  undefined8 local_158;
  undefined local_60 [24];
  char local_48;
  long local_40;
  
  bVar14 = 0;
  local_354[0] = param_7;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  local_350 = param_6;
  local_34c[0] = param_4;
  FUN_00026a00(local_2c8,param_3);
  puVar6 = (undefined8 *)(local_2b8 + (long)local_34c[0] * 0x18);
  local_308 = *puVar6;
  uVar3 = puVar6[1];
  local_2f8 = puVar6[2];
  uStack_300._4_4_ = (int)((ulong)uVar3 >> 0x20);
  iVar5 = *param_5;
  if (*param_5 < uStack_300._4_4_) {
    iVar5 = uStack_300._4_4_;
  }
  iVar10 = param_5[1];
  if (param_5[1] < (int)local_2f8) {
    iVar10 = (int)local_2f8;
  }
  iVar4 = (int)((ulong)local_2f8 >> 0x20);
  if (iVar4 < param_5[2]) {
    iVar4 = param_5[2];
  }
  lVar13 = local_2b8;
  uStack_300 = uVar3;
  if (3 < iVar4 + iVar5 + iVar10) {
    uVar2 = *(undefined4 *)puVar6;
    if (*(int *)(puVar6 + 1) != 0) {
      uVar2 = *(undefined4 *)((long)puVar6 + 4);
    }
                    /* try { // try from 00026d5b to 00026d5f has its CatchHandler @ 000271e5 */
    FUN_0001a1c0(param_2,local_2c8,local_34c[0],uVar2);
    lVar11 = 0;
    do {
      iVar5 = *(int *)((long)&uStack_300 + lVar11 * 4 + 4);
      if (param_5[lVar11] < iVar5) {
        local_158 = 0xffffffff;
        local_168 = ZEXT816(0xffffffff00000000);
        local_188 = (undefined  [16])0x0;
        local_178 = (undefined  [16])0x0;
                    /* try { // try from 00027114 to 00027118 has its CatchHandler @ 000271e5 */
        FUN_00018b10(local_188,"unload");
        local_168._8_4_ = (int)lVar11;
        local_168._0_4_ = local_34c[0];
        local_168._12_4_ = iVar5 - param_5[lVar11];
                    /* try { // try from 00027146 to 0002714a has its CatchHandler @ 00027234 */
        FUN_00019ec0(param_2,local_2c8,local_188,0);
        if ((undefined *)local_188._0_8_ != local_178) {
          thunk_FUN_000d36e0(local_188._0_8_,local_178._0_8_ + 1);
        }
      }
      lVar11 = lVar11 + 1;
      lVar13 = local_2b8;
    } while (lVar11 != 3);
  }
  if (local_1a4 == '\0') {
    *(undefined *)(param_1 + 0x140) = 0;
  }
  else {
    lVar11 = 0;
    local_314[0] = 0;
    local_314[1] = 0;
    local_314[2] = 0;
    local_328 = (int *)0x0;
    local_340 = local_340 & 0xffffffff00000000;
    local_338 = (undefined  [16])0x0;
    do {
      iVar10 = (int)lVar11;
      iVar5 = param_5[lVar11] - *(int *)(lVar13 + (long)local_34c[0] * 0x18 + 0xc + lVar11 * 4);
      if (iVar5 < 1) {
        local_314[lVar11] = 0;
      }
      else {
        local_314[lVar11] = iVar5;
        if ((int *)local_338._8_8_ == local_328) {
                    /* try { // try from 00027184 to 00027188 has its CatchHandler @ 000271e0 */
          FUN_0001e040(local_338,local_338._8_8_,&local_340);
        }
        else {
          *(int *)local_338._8_8_ = iVar10;
          local_338._8_8_ = (int *)(local_338._8_8_ + 4);
        }
      }
      lVar11 = lVar11 + 1;
      local_340 = CONCAT44(local_340._4_4_,iVar10 + 1);
    } while (lVar11 != 3);
    puVar6 = (undefined8 *)local_188;
    for (lVar11 = 0x29; lVar11 != 0; lVar11 = lVar11 + -1) {
      *puVar6 = 0;
      puVar6 = puVar6 + (ulong)bVar14 * -2 + 1;
    }
    while( true ) {
      local_2d8 = (code *)0x0;
      pcStack_2d0 = (code *)0x0;
      local_2e8 = (undefined  [16])0x0;
                    /* try { // try from 00026f08 to 00026f0c has its CatchHandler @ 000271d9 */
      puVar6 = (undefined8 *)FUN_00041fe0(0x48);
      puVar6[4] = param_2;
      puVar6[6] = param_5;
      puVar6[5] = local_354;
      *puVar6 = local_188;
      puVar6[1] = local_338;
      puVar6[7] = local_314;
      puVar6[8] = local_2e8;
      puVar6[2] = local_34c;
      puVar6[3] = &local_350;
      local_2e8._0_8_ = puVar6;
      local_340 = 0;
      local_2d8 = FUN_0001a6f0;
      pcStack_2d0 = FUN_0002c680;
                    /* try { // try from 00026f7b to 00026f7f has its CatchHandler @ 000271de */
      FUN_0002c680(local_2e8,local_2c8,&local_340);
      if (local_2d8 != (code *)0x0) {
        (*local_2d8)(local_2e8,local_2e8,3);
      }
      if ((local_338._0_8_ == local_338._8_8_) ||
         ((int *)local_338._8_8_ == (int *)(local_338._0_8_ + 4))) break;
      piVar9 = (int *)(local_338._8_8_ + -4);
      piVar7 = piVar9;
      iVar5 = *(int *)(local_338._8_8_ + -4);
      while( true ) {
        piVar8 = piVar7 + -1;
        iVar10 = *piVar8;
        piVar12 = (int *)local_338._8_8_;
        if (iVar10 < iVar5) break;
        piVar7 = piVar8;
        iVar5 = iVar10;
        if ((int *)local_338._0_8_ == piVar8) {
          piVar7 = (int *)local_338._0_8_;
          if ((ulong)local_338._0_8_ < piVar9) {
            do {
              iVar5 = *piVar7;
              piVar8 = piVar7 + 1;
              piVar12 = piVar9 + -1;
              *piVar7 = *piVar9;
              *piVar9 = iVar5;
              piVar9 = piVar12;
              piVar7 = piVar8;
            } while (piVar8 < piVar12);
          }
          *(undefined *)(param_1 + 0x140) = 0;
          piVar9 = (int *)local_338._0_8_;
          if (local_48 != '\0') goto LAB_00027190;
          goto LAB_000270a9;
        }
      }
      do {
        piVar1 = piVar12 + -1;
        piVar12 = piVar12 + -1;
      } while (*piVar1 <= iVar10);
      *piVar8 = *piVar1;
      *piVar12 = iVar10;
      if (((int *)local_338._8_8_ != piVar7) && (piVar7 < piVar9)) {
        do {
          iVar5 = *piVar7;
          piVar8 = piVar7 + 1;
          piVar12 = piVar9 + -1;
          *piVar7 = *piVar9;
          *piVar9 = iVar5;
          piVar9 = piVar12;
          piVar7 = piVar8;
        } while (piVar8 < piVar12);
      }
    }
    *(undefined *)(param_1 + 0x140) = 0;
    if (local_48 != '\0') {
LAB_00027190:
      FUN_0001c620(param_1,local_188);
      *(undefined *)(param_1 + 0x140) = 1;
      local_48 = '\0';
      FUN_0001cf40(local_60);
      FUN_0001cb50(local_178);
    }
    piVar9 = (int *)local_338._0_8_;
    if ((int *)local_338._0_8_ != (int *)0x0) {
LAB_000270a9:
      thunk_FUN_000d36e0(piVar9,(long)local_328 - (long)piVar9);
    }
  }
  FUN_0001cf40(local_1a0);
  if (lVar13 != 0) {
    thunk_FUN_000d36e0(lVar13,local_2a8 - lVar13);
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


