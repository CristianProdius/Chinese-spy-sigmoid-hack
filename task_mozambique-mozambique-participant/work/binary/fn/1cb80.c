// ===== FUNC 1cb80 size=904

void FUN_0001cb80(undefined8 *param_1,undefined8 *param_2,undefined4 param_3)

{
  int iVar1;
  long lVar2;
  undefined8 uVar3;
  ulong uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  int iVar7;
  undefined8 *puVar8;
  undefined8 *puVar9;
  long lVar10;
  long lVar11;
  int *piVar12;
  int *piVar13;
  int *piVar14;
  long in_FS_OFFSET;
  byte bVar15;
  undefined8 local_f0;
  undefined8 uStack_e8;
  undefined8 local_e0;
  undefined8 uStack_d8;
  undefined8 local_d0;
  undefined8 uStack_c8;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 local_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 local_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined2 local_70;
  undefined local_6c [16];
  undefined local_5c [16];
  undefined8 local_4c;
  long local_40;
  
  bVar15 = 0;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  puVar8 = param_1;
  for (lVar10 = 0xb0; lVar10 != 0; lVar10 = lVar10 + -1) {
    *puVar8 = *param_2;
    param_2 = param_2 + 1;
    puVar8 = puVar8 + 1;
  }
  *(undefined4 *)puVar8 = *(undefined4 *)param_2;
  *(undefined4 *)((long)param_1 + 0x584) = 0;
  *(undefined4 *)(param_1 + 0xb1) = param_3;
  piVar12 = (int *)(param_1 + 0xb2);
  do {
    piVar12[0] = 0;
    piVar12[1] = 0;
    piVar13 = piVar12 + 0x36;
    piVar12[2] = 0;
    *(undefined (*) [16])(piVar12 + 4) = (undefined  [16])0x0;
    piVar12[8] = 0;
    piVar12[9] = 0;
    piVar14 = piVar12 + 10;
    for (lVar10 = 0xf; lVar10 != 0; lVar10 = lVar10 + -1) {
      piVar14[0] = 0;
      piVar14[1] = 0;
      piVar14 = piVar14 + 2;
    }
    piVar12[0x28] = 0;
    piVar12[0x29] = 0;
    *(undefined2 *)(piVar12 + 0x2a) = 0;
    *(undefined (*) [16])(piVar12 + 0x2b) = (undefined  [16])0x0;
    *(undefined (*) [16])(piVar12 + 0x2f) = (undefined  [16])0x0;
    piVar12[0x33] = 0;
    uVar3 = DAT_000e2db8;
    piVar12[0x34] = 0;
    piVar12 = piVar13;
  } while ((int *)(param_1 + 0xe8) != piVar13);
  param_1[0xec] = 0;
  lVar10 = 0;
  *(undefined (*) [16])(param_1 + 0xe8) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0xea) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0xed) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0xef) = (undefined  [16])0x0;
  piVar12 = (int *)(param_1 + 0xb2);
  while( true ) {
    iVar1 = *(int *)((long)param_1 + lVar10 + 0x2c);
    puVar8 = &local_f0;
    for (lVar11 = 0xf; lVar11 != 0; lVar11 = lVar11 + -1) {
      *puVar8 = 0;
      puVar8 = puVar8 + (ulong)bVar15 * -2 + 1;
    }
    local_6c = (undefined  [16])0x0;
    local_5c = (undefined  [16])0x0;
    local_78 = 0;
    local_70 = 0;
    local_4c = 0;
                    /* try { // try from 0001cced to 0001ccf1 has its CatchHandler @ 0001cf15 */
    puVar8 = (undefined8 *)FUN_00041fe0(0x30);
    lVar11 = *(long *)(piVar12 + 4);
    *piVar12 = iVar1;
    lVar2 = *(long *)(piVar12 + 8);
    puVar8[2] = 0;
    puVar8[5] = 0;
    piVar12[1] = 0;
    *puVar8 = CONCAT44(0xffffffff,iVar1);
    puVar8[1] = 0;
    puVar8[3] = CONCAT44(0xffffffff,iVar1);
    puVar8[4] = 0;
    *(undefined4 *)((long)&uStack_e8 + (long)iVar1 * 0xc) = 0;
    *(undefined8 *)((long)&local_f0 + (long)iVar1 * 0xc) = uVar3;
    piVar12[2] = 0;
    *(undefined8 **)(piVar12 + 4) = puVar8;
    *(undefined8 **)(piVar12 + 6) = puVar8 + 6;
    *(undefined8 **)(piVar12 + 8) = puVar8 + 6;
    if (lVar11 != 0) {
      thunk_FUN_000d36e0(lVar11,lVar2 - lVar11);
    }
    *(undefined8 *)(piVar12 + 0x26) = local_80;
    *(undefined8 *)(piVar12 + 10) = local_f0;
    *(undefined8 *)(piVar12 + 0xc) = uStack_e8;
    *(undefined8 *)(piVar12 + 0xe) = local_e0;
    *(undefined8 *)(piVar12 + 0x10) = uStack_d8;
    *(undefined8 *)(piVar12 + 0x28) = local_78;
    *(undefined8 *)(piVar12 + 0x12) = local_d0;
    *(undefined8 *)(piVar12 + 0x14) = uStack_c8;
    *(undefined8 *)(piVar12 + 0x16) = local_c0;
    *(undefined8 *)(piVar12 + 0x18) = uStack_b8;
    *(undefined2 *)(piVar12 + 0x2a) = local_70;
    *(undefined8 *)(piVar12 + 0x1a) = local_b0;
    *(undefined8 *)(piVar12 + 0x1c) = uStack_a8;
    *(undefined8 *)(piVar12 + 0x1e) = local_a0;
    *(undefined8 *)(piVar12 + 0x20) = uStack_98;
    *(undefined8 *)(piVar12 + 0x22) = local_90;
    *(undefined8 *)(piVar12 + 0x24) = uStack_88;
    *(undefined8 *)(piVar12 + 0x2b) = local_6c._0_8_;
    *(undefined8 *)(piVar12 + 0x2d) = local_6c._8_8_;
    *(undefined8 *)(piVar12 + 0x2f) = local_5c._0_8_;
    *(undefined8 *)(piVar12 + 0x31) = local_5c._8_8_;
    *(undefined8 *)(piVar12 + 0x33) = local_4c;
    uVar6 = DAT_000e2dd8;
    uVar5 = DAT_000e2dd0;
    uVar4 = DAT_000e2dc8;
    if (lVar10 == 4) break;
    lVar10 = 4;
    piVar12 = piVar12 + 0x36;
  }
  puVar8 = (undefined8 *)((long)param_1 + 4);
  do {
    puVar9 = puVar8 + 1;
    *(ulong *)((long)puVar8 + 0x73c) =
         ~CONCAT44(-(uint)((int)((ulong)uVar6 >> 0x20) <
                          (int)((ulong)*puVar8 >> 0x20) - (int)((ulong)uVar5 >> 0x20)),
                   -(uint)((int)uVar6 < (int)*puVar8 - (int)uVar5)) & uVar4;
    puVar8 = puVar9;
  } while (puVar9 != (undefined8 *)((long)param_1 + 0x2c));
  iVar1 = *(int *)(param_1 + 0xb1);
  *(undefined4 *)(param_1 + 0xed) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x76c) = 0xffffffff;
  *(undefined4 *)(param_1 + 0xee) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x774) = 0xffffffff;
  *(undefined4 *)(param_1 + 0xef) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x77c) = 0xffffffff;
  *(undefined4 *)(param_1 + 0xf0) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x784) = 0xffffffff;
  lVar10 = 0;
  do {
    if (iVar1 == 0) goto LAB_0001cef4;
    iVar7 = (int)lVar10;
    while ((iVar7 < 4 && (iVar1 == 1))) {
      *(undefined4 *)((long)param_1 + lVar10 * 4 + 0x768) = 0xfffffffe;
      lVar10 = lVar10 + 1;
      iVar7 = (int)lVar10;
    }
    lVar10 = lVar10 + 1;
  } while (lVar10 != 8);
LAB_0001cec2:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
LAB_0001cef4:
  do {
    for (; (int)lVar10 < 4; lVar10 = lVar10 + 1) {
    }
    *(undefined4 *)((long)param_1 + lVar10 * 4 + 0x768) = 0xfffffffe;
    lVar10 = lVar10 + 1;
  } while (lVar10 != 8);
  goto LAB_0001cec2;
}


