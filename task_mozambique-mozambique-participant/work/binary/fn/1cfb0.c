// ===== FUNC 1cfb0 size=1213

void FUN_0001cfb0(undefined8 *param_1,undefined8 *param_2,undefined4 param_3)

{
  int *piVar1;
  char cVar2;
  int iVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  long *plVar8;
  long *plVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  int iVar14;
  int iVar15;
  long *plVar16;
  long lVar17;
  long in_FS_OFFSET;
  double dVar18;
  undefined8 local_188;
  undefined4 local_180;
  undefined local_178 [16];
  long local_168;
  undefined8 local_160;
  undefined8 uStack_158;
  undefined8 local_150;
  undefined8 uStack_148;
  undefined8 local_140;
  undefined8 uStack_138;
  undefined8 local_130;
  undefined8 uStack_128;
  undefined8 local_120;
  undefined8 uStack_118;
  undefined8 local_110;
  undefined8 uStack_108;
  undefined8 local_100;
  undefined8 uStack_f8;
  undefined8 local_f0;
  undefined8 local_e8;
  undefined2 local_e0;
  undefined8 local_dc;
  undefined8 uStack_d4;
  undefined8 local_cc;
  undefined8 uStack_c4;
  undefined8 local_bc;
  undefined8 local_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 local_90;
  undefined8 local_88;
  undefined8 uStack_80;
  undefined8 local_78;
  undefined8 uStack_70;
  int local_68;
  undefined local_64;
  undefined local_60 [16];
  undefined8 local_50;
  undefined4 local_48;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if ((*(char *)(param_2 + 0x28) != '\0') && (*(char *)((long)param_2 + 0x124) != '\0')) {
    iVar3 = *(int *)(param_2 + 0x24);
    piVar1 = (int *)((long)param_2 + (long)*(int *)*param_1 * 0xc + 0x28);
    iVar14 = piVar1[1] + -1;
    if (iVar14 < 0) {
      iVar14 = 0;
    }
    iVar15 = *piVar1 + -2;
    if (iVar15 < 0) {
      iVar15 = 0;
    }
    dVar18 = (double)iVar3 -
             ((double)iVar14 * DAT_000e2de0 + (double)iVar15) * *(double *)param_1[1];
    if (dVar18 < *(double *)param_1[2]) {
      *(double *)param_1[2] = dVar18;
      local_f0 = param_2[0x13];
      local_160 = param_2[5];
      uStack_158 = param_2[6];
      local_150 = param_2[7];
      uStack_148 = param_2[8];
      local_140 = param_2[9];
      uStack_138 = param_2[10];
      uVar10 = *(undefined8 *)*(undefined (*) [16])(param_2 + 2);
      uVar11 = param_2[3];
      local_178 = *(undefined (*) [16])(param_2 + 2);
      lVar17 = param_2[4];
      local_130 = param_2[0xb];
      uStack_128 = param_2[0xc];
      local_120 = param_2[0xd];
      uStack_118 = param_2[0xe];
      local_e8 = param_2[0x14];
      local_110 = param_2[0xf];
      uStack_108 = param_2[0x10];
      local_188 = *param_2;
      local_180 = *(undefined4 *)(param_2 + 1);
      local_100 = param_2[0x11];
      uStack_f8 = param_2[0x12];
      local_dc = *(undefined8 *)((long)param_2 + 0xac);
      uStack_d4 = *(undefined8 *)((long)param_2 + 0xb4);
      local_e0 = *(undefined2 *)(param_2 + 0x15);
      param_2[4] = 0;
      *(undefined (*) [16])(param_2 + 2) = (undefined  [16])0x0;
      local_bc = *(undefined8 *)((long)param_2 + 0xcc);
      puVar4 = (undefined8 *)param_1[3];
      uVar12 = *(undefined8 *)*(undefined (*) [16])(param_2 + 0x25);
      uVar13 = param_2[0x26];
      local_60 = *(undefined (*) [16])(param_2 + 0x25);
      local_cc = *(undefined8 *)((long)param_2 + 0xbc);
      uStack_c4 = *(undefined8 *)((long)param_2 + 0xc4);
      local_90 = param_2[0x1f];
      local_b0 = param_2[0x1b];
      uStack_a8 = param_2[0x1c];
      local_a0 = param_2[0x1d];
      uStack_98 = param_2[0x1e];
      local_64 = 1;
      local_88 = param_2[0x20];
      uStack_80 = param_2[0x21];
      uVar5 = param_2[0x27];
      local_78 = param_2[0x22];
      uStack_70 = param_2[0x23];
      param_2[0x27] = 0;
      cVar2 = *(char *)(puVar4 + 0x29);
      *(undefined (*) [16])(param_2 + 0x25) = (undefined  [16])0x0;
      local_68 = iVar3;
      local_50 = uVar5;
      local_48 = param_3;
      if (cVar2 == '\0') {
        local_168 = lVar17;
        FUN_0001c620(puVar4,&local_188);
        *(undefined4 *)(puVar4 + 0x28) = param_3;
        uVar5 = local_178._0_8_;
        *(undefined *)(puVar4 + 0x29) = 1;
        lVar17 = local_168 - local_178._0_8_;
        FUN_0001cf40(local_60);
        if (uVar5 != 0) {
          if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
            thunk_FUN_000d36e0(uVar5,lVar17);
            return;
          }
          goto LAB_0001d46d;
        }
      }
      else {
        lVar6 = puVar4[2];
        *(undefined4 *)(puVar4 + 1) = local_180;
        *puVar4 = local_188;
        lVar7 = puVar4[4];
        local_168 = 0;
        puVar4[4] = lVar17;
        puVar4[2] = uVar10;
        puVar4[3] = uVar11;
        local_178 = (undefined  [16])0x0;
        if (lVar6 != 0) {
          thunk_FUN_000d36e0(lVar6,lVar7 - lVar6);
        }
        puVar4[5] = local_160;
        puVar4[6] = uStack_158;
        puVar4[0x13] = local_f0;
        puVar4[7] = local_150;
        puVar4[8] = uStack_148;
        puVar4[9] = local_140;
        puVar4[10] = uStack_138;
        puVar4[0x14] = local_e8;
        puVar4[0xb] = local_130;
        puVar4[0xc] = uStack_128;
        *(undefined2 *)(puVar4 + 0x15) = local_e0;
        puVar4[0xd] = local_120;
        puVar4[0xe] = uStack_118;
        *(undefined8 *)((long)puVar4 + 0xcc) = local_bc;
        puVar4[0xf] = local_110;
        puVar4[0x10] = uStack_108;
        *(undefined8 *)((long)puVar4 + 0xac) = local_dc;
        *(undefined8 *)((long)puVar4 + 0xb4) = uStack_d4;
        puVar4[0x1f] = local_90;
        puVar4[0x11] = local_100;
        puVar4[0x12] = uStack_f8;
        *(undefined8 *)((long)puVar4 + 0xbc) = local_cc;
        *(undefined8 *)((long)puVar4 + 0xc4) = uStack_c4;
        puVar4[0x1b] = local_b0;
        puVar4[0x1c] = uStack_a8;
        puVar4[0x1d] = local_a0;
        puVar4[0x1e] = uStack_98;
        plVar8 = (long *)puVar4[0x25];
        plVar9 = (long *)puVar4[0x26];
        *(int *)(puVar4 + 0x24) = iVar3;
        lVar17 = puVar4[0x27];
        *(undefined *)((long)puVar4 + 0x124) = 1;
        puVar4[0x27] = uVar5;
        local_50 = 0;
        puVar4[0x20] = local_88;
        puVar4[0x21] = uStack_80;
        puVar4[0x22] = local_78;
        puVar4[0x23] = uStack_70;
        puVar4[0x25] = uVar12;
        puVar4[0x26] = uVar13;
        local_60 = (undefined  [16])0x0;
        for (plVar16 = plVar8; plVar16 != plVar9; plVar16 = plVar16 + 7) {
          if ((long *)*plVar16 != plVar16 + 2) {
            thunk_FUN_000d36e0((long *)*plVar16,plVar16[2] + 1);
          }
        }
        if (plVar8 != (long *)0x0) {
          thunk_FUN_000d36e0(plVar8,lVar17 - (long)plVar8);
        }
        *(undefined4 *)(puVar4 + 0x28) = param_3;
        FUN_0001cf40(local_60);
      }
    }
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_0001d46d:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


