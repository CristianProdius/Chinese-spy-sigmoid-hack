// ===== FUNC 29f80 size=1944

long FUN_00029f80(long param_1,long param_2,undefined8 *param_3,int param_4)

{
  undefined4 uVar1;
  long *plVar2;
  long lVar3;
  undefined *puVar4;
  long lVar5;
  int iVar6;
  int iVar7;
  long lVar8;
  long *plVar9;
  long *plVar10;
  int *piVar11;
  undefined8 *puVar12;
  undefined8 *puVar13;
  int iVar14;
  ulong uVar15;
  int iVar16;
  long lVar17;
  long in_FS_OFFSET;
  bool bVar18;
  ulong local_2f8;
  long lStack_2f0;
  long local_2e8;
  long lStack_2e0;
  long *local_2d8;
  long *plStack_2d0;
  long local_2c8;
  long lStack_2c0;
  ulong *local_2b8;
  ulong local_2b0;
  ulong auStack_2a8 [2];
  undefined8 local_298;
  undefined8 uStack_290;
  undefined8 local_288;
  long local_278 [30];
  long local_188 [2];
  long local_178;
  long local_170;
  long local_168;
  int local_dc [10];
  int local_b4;
  undefined local_b0 [40];
  undefined local_88 [32];
  int local_68;
  char local_64;
  undefined local_60 [32];
  long local_40;
  
  lVar17 = 2;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_00026a00(local_188,param_2 + 0x598);
  plVar10 = local_278;
  do {
    *plVar10 = 0;
    plVar10[1] = 0;
    *(undefined (*) [16])(plVar10 + 2) = (undefined  [16])0x0;
    *(undefined (*) [16])(plVar10 + 4) = (undefined  [16])0x0;
    *(undefined (*) [16])(plVar10 + 6) = (undefined  [16])0x0;
    *(undefined (*) [16])(plVar10 + 8) = (undefined  [16])0x0;
                    /* try { // try from 0002a00f to 0002a013 has its CatchHandler @ 0002a74b */
    FUN_0001fd50(plVar10,0);
    plVar10 = plVar10 + 10;
    bVar18 = lVar17 != 0;
    lVar17 = lVar17 + -1;
  } while (bVar18);
  puVar13 = (undefined8 *)param_3[1];
  puVar12 = (undefined8 *)*param_3;
joined_r0x0002a029:
  if (puVar12 != puVar13) {
    do {
      iVar16 = FUN_000b31e0(puVar12,&DAT_000e0454);
      if (iVar16 != 0) {
        iVar16 = 0;
        if (-1 < *(int *)(puVar12 + 4)) {
          iVar16 = *(int *)(puVar12 + 4);
        }
        lVar17 = (long)iVar16;
        plVar10 = (long *)local_278[lVar17 * 10 + 6];
        if (plVar10 != (long *)(local_278[lVar17 * 10 + 8] + -0x38)) goto code_r0x0002a08b;
                    /* try { // try from 0002a6b1 to 0002a6e1 has its CatchHandler @ 0002a7d5 */
        FUN_000203d0(local_278 + lVar17 * 10,puVar12);
      }
      puVar12 = puVar12 + 7;
      if (puVar13 == puVar12) break;
    } while( true );
  }
  while (plVar10 = local_278, local_68 < 0x50) {
    bVar18 = false;
    do {
      plVar9 = plVar10 + 6;
      plVar2 = plVar10 + 2;
      plVar10 = plVar10 + 10;
      bVar18 = (bool)(bVar18 | *plVar2 != *plVar9);
    } while (local_188 != plVar10);
    if (!bVar18) goto LAB_0002a40d;
                    /* try { // try from 0002a16d to 0002a171 has its CatchHandler @ 0002a7d5 */
    FUN_00021660(&local_2d8,param_2 + 0x14,local_188,local_b0,local_88);
    lVar5 = local_170;
    lVar17 = local_178;
    uVar15 = 0xffffffff;
    iVar6 = (int)(local_170 - local_178 >> 3) * -0x55555555;
    iVar16 = param_4;
    if (iVar6 < 1) {
LAB_0002a528:
      bVar18 = false;
      for (; lVar5 != lVar17; lVar17 = lVar17 + 0x18) {
        bVar18 = (bool)(bVar18 | 0 < *(int *)(lVar17 + 8));
      }
      piVar11 = local_dc;
      do {
        iVar16 = *piVar11;
        piVar11 = piVar11 + 1;
        bVar18 = (bool)(bVar18 | 0 < iVar16);
      } while (&local_b4 != piVar11);
      if (bVar18) {
        local_2b8 = auStack_2a8;
        local_298 = DAT_000e2e80;
        uStack_290 = 0xffffffff;
        local_288 = 0xffffffff;
                    /* try { // try from 0002a5c2 to 0002a5c6 has its CatchHandler @ 0002a746 */
        FUN_00017bf0(&local_2b8,&DAT_000e0454);
                    /* try { // try from 0002a5d6 to 0002a5da has its CatchHandler @ 0002a73f */
        FUN_00019ec0(param_2,local_188,&local_2b8,0);
        goto LAB_0002a35f;
      }
LAB_0002a70e:
      *(undefined *)(param_1 + 0x140) = 0;
      FUN_0001cf40(&local_2d8);
      goto LAB_0002a426;
    }
    do {
      plVar10 = plStack_2d0;
      lVar8 = (long)(int)((long)iVar16 % (long)iVar6);
      lVar3 = local_278[lVar8 * 10 + 2];
      if ((local_278[lVar8 * 10 + 6] != lVar3) &&
         (plVar9 = (long *)FUN_00019a20(local_2d8,plStack_2d0,lVar3), plVar10 != plVar9)) {
        if (((int)uVar15 < 0) || (iVar7 = FUN_000b31e0(lVar3,"deliver"), iVar7 == 0)) {
          uVar15 = (long)iVar16 % (long)iVar6 & 0xffffffff;
        }
        iVar14 = (int)uVar15;
        iVar7 = FUN_000b31e0(lVar3,"deliver");
        if (iVar7 == 0) break;
      }
      iVar14 = (int)uVar15;
      iVar16 = iVar16 + 1;
    } while (param_4 + iVar6 != iVar16);
    if (iVar14 < 0) goto LAB_0002a528;
    lVar17 = (long)iVar14;
    local_2b8 = auStack_2a8;
    puVar13 = (undefined8 *)local_278[lVar17 * 10 + 2];
    uVar15 = puVar13[1];
    puVar4 = (undefined *)*puVar13;
    local_2f8 = uVar15;
    if (uVar15 < 0x10) {
      if (uVar15 == 1) {
        auStack_2a8[0] = CONCAT71(auStack_2a8[0]._1_7_,*puVar4);
      }
      else if (uVar15 != 0) goto LAB_0002a617;
    }
    else {
                    /* try { // try from 0002a5fa to 0002a5fe has its CatchHandler @ 0002a746 */
      local_2b8 = (ulong *)FUN_000b0760(&local_2b8,&local_2f8,0);
      auStack_2a8[0] = local_2f8;
LAB_0002a617:
      memcpy(local_2b8,puVar4,uVar15);
    }
    *(undefined *)((long)local_2b8 + local_2f8) = 0;
    local_298 = puVar13[4];
    uStack_290 = puVar13[5];
    local_288 = CONCAT44(local_288._4_4_,*(undefined4 *)(puVar13 + 6));
    plVar9 = (long *)local_278[lVar17 * 10 + 2];
    plVar10 = (long *)*plVar9;
    local_2b0 = local_2f8;
    if (plVar9 == (long *)(local_278[lVar17 * 10 + 4] + -0x38)) {
      if (plVar10 != plVar9 + 2) {
        thunk_FUN_000d36e0(plVar10,plVar9[2] + 1);
      }
      thunk_FUN_000d36e0(local_278[lVar17 * 10 + 3],0x1f8);
      plVar9 = *(long **)(local_278[lVar17 * 10 + 5] + 8);
      local_278[lVar17 * 10 + 5] = local_278[lVar17 * 10 + 5] + 8;
      local_278[lVar17 * 10 + 3] = (long)plVar9;
      local_278[lVar17 * 10 + 4] = (long)(plVar9 + 0x3f);
    }
    else {
      if (plVar10 != plVar9 + 2) {
        thunk_FUN_000d36e0(plVar10,plVar9[2] + 1);
      }
      plVar9 = plVar9 + 7;
    }
    local_278[lVar17 * 10 + 2] = (long)plVar9;
                    /* try { // try from 0002a35a to 0002a35e has its CatchHandler @ 0002a744 */
    FUN_00019ec0(param_2,local_188,&local_2b8,0);
LAB_0002a35f:
    if (local_2b8 != auStack_2a8) {
      thunk_FUN_000d36e0(local_2b8,auStack_2a8[0] + 1);
    }
    plVar2 = plStack_2d0;
    plVar9 = local_2d8;
    plVar10 = local_2d8;
    if (local_64 == '\0') goto LAB_0002a70e;
    for (; plVar2 != plVar10; plVar10 = plVar10 + 7) {
      if ((long *)*plVar10 != plVar10 + 2) {
        thunk_FUN_000d36e0((long *)*plVar10,plVar10[2] + 1);
      }
    }
    if (plVar9 != (long *)0x0) {
      thunk_FUN_000d36e0(plVar9,local_2c8 - (long)plVar9);
    }
  }
  do {
    if (plVar10[6] != plVar10[2]) {
      *(undefined *)(param_1 + 0x140) = 0;
      goto LAB_0002a426;
    }
    plVar10 = plVar10 + 10;
  } while (local_188 != plVar10);
LAB_0002a40d:
  FUN_0001c620(param_1,local_188);
  *(undefined *)(param_1 + 0x140) = 1;
LAB_0002a426:
  plVar10 = local_188;
  do {
    local_2f8 = plVar10[-4];
    lStack_2f0 = plVar10[-3];
    local_2e8 = plVar10[-2];
    lStack_2e0 = plVar10[-1];
    plVar9 = plVar10 + -10;
    local_2d8 = (long *)plVar10[-8];
    plStack_2d0 = (long *)plVar10[-7];
    local_2c8 = plVar10[-6];
    lStack_2c0 = plVar10[-5];
    lVar17 = plVar10[-1];
    puVar13 = (undefined8 *)plVar10[-5];
    FUN_000181d0(&local_2d8,&local_2f8);
    lVar5 = *plVar9;
    if (lVar5 != 0) {
      for (; puVar13 < (undefined8 *)(lVar17 + 8); puVar13 = puVar13 + 1) {
        thunk_FUN_000d36e0(*puVar13,0x1f8);
      }
      thunk_FUN_000d36e0(lVar5,plVar10[-9] * 8);
    }
    plVar10 = plVar9;
  } while (plVar9 != local_278);
  FUN_0001cf40(local_60);
  if (local_178 != 0) {
    thunk_FUN_000d36e0(local_178,local_168 - local_178);
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
code_r0x0002a08b:
  plVar9 = plVar10 + 2;
  plVar2 = (long *)puVar12[1];
  *plVar10 = (long)plVar9;
  puVar4 = (undefined *)*puVar12;
  local_2d8 = plVar2;
  if (Elf64_Ehdr_00000000.e_ident_pad + 6 < plVar2) {
    plVar9 = (long *)FUN_000b0760(plVar10,&local_2d8,0);
    *plVar10 = (long)plVar9;
    plVar10[2] = (long)local_2d8;
  }
  else {
    if (plVar2 == (long *)Elf64_Ehdr_00000000.e_ident_magic_str) {
      *(undefined *)(plVar10 + 2) = *puVar4;
      goto LAB_0002a0c6;
    }
    if (plVar2 == (long *)0x0) goto LAB_0002a0c6;
  }
  memcpy(plVar9,puVar4,(size_t)plVar2);
  plVar9 = (long *)*plVar10;
LAB_0002a0c6:
  plVar10[1] = (long)local_2d8;
  *(undefined *)((long)plVar9 + (long)local_2d8) = 0;
  lVar5 = puVar12[5];
  uVar1 = *(undefined4 *)(puVar12 + 6);
  plVar10[4] = puVar12[4];
  plVar10[5] = lVar5;
  *(undefined4 *)(plVar10 + 6) = uVar1;
  local_278[lVar17 * 10 + 6] = (long)(plVar10 + 7);
  puVar12 = puVar12 + 7;
  goto joined_r0x0002a029;
}


