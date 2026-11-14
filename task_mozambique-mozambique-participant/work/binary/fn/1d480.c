// ===== FUNC 1d480 size=1162

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001d480(undefined8 *param_1,undefined8 *param_2,undefined4 param_3)

{
  char cVar1;
  undefined8 *puVar2;
  undefined8 uVar3;
  long lVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  int *piVar9;
  int iVar10;
  int iVar11;
  int *piVar12;
  long lVar13;
  long in_FS_OFFSET;
  double dVar14;
  undefined8 local_198;
  undefined8 uStack_190;
  undefined8 local_188;
  undefined8 local_178;
  undefined4 local_170;
  undefined local_168 [16];
  long local_158;
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
  undefined8 uStack_e8;
  undefined8 local_e0;
  undefined8 local_d8;
  undefined2 local_d0;
  undefined8 local_cc;
  undefined8 uStack_c4;
  undefined8 local_bc;
  undefined8 uStack_b4;
  undefined8 local_ac;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 local_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined8 uStack_70;
  undefined8 local_68;
  undefined8 uStack_60;
  int local_58;
  undefined local_54;
  undefined local_50 [16];
  undefined8 local_40;
  undefined4 local_38;
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  if (*(char *)((long)param_2 + 0x124) != '\0') {
    piVar9 = (int *)(param_2 + 5);
    dVar14 = 0.0;
    piVar12 = (int *)(param_2 + 0x14);
    do {
      if (*(char *)piVar12 != '\0') {
        iVar10 = piVar9[1];
        if (2 < iVar10) {
          iVar10 = 2;
        }
        iVar11 = *piVar9;
        if (4 < iVar11) {
          iVar11 = 4;
        }
        dVar14 = dVar14 + (double)iVar10 * DAT_000e2de0 + (double)iVar11;
      }
      piVar9 = piVar9 + 3;
      piVar12 = (int *)((long)piVar12 + 1);
    } while (piVar9 != (int *)(param_2 + 0x14));
    iVar10 = *(int *)(param_2 + 0x24);
    dVar14 = (double)iVar10 - dVar14 * _DAT_000e2de8;
    if (dVar14 < *(double *)*param_1) {
      local_e0 = param_2[0x13];
      local_150 = param_2[5];
      uStack_148 = param_2[6];
      *(double *)*param_1 = dVar14;
      local_140 = param_2[7];
      uStack_138 = param_2[8];
      local_130 = param_2[9];
      uStack_128 = param_2[10];
      local_120 = param_2[0xb];
      uStack_118 = param_2[0xc];
      uVar5 = *(undefined8 *)*(undefined (*) [16])(param_2 + 2);
      uVar6 = param_2[3];
      local_168 = *(undefined (*) [16])(param_2 + 2);
      local_d8 = param_2[0x14];
      local_158 = param_2[4];
      local_178 = *param_2;
      local_110 = param_2[0xd];
      uStack_108 = param_2[0xe];
      local_170 = *(undefined4 *)(param_2 + 1);
      local_100 = param_2[0xf];
      uStack_f8 = param_2[0x10];
      local_d0 = *(undefined2 *)(param_2 + 0x15);
      local_f0 = param_2[0x11];
      uStack_e8 = param_2[0x12];
      local_cc = *(undefined8 *)((long)param_2 + 0xac);
      uStack_c4 = *(undefined8 *)((long)param_2 + 0xb4);
      param_2[4] = 0;
      *(undefined (*) [16])(param_2 + 2) = (undefined  [16])0x0;
      local_bc = *(undefined8 *)((long)param_2 + 0xbc);
      uStack_b4 = *(undefined8 *)((long)param_2 + 0xc4);
      local_ac = *(undefined8 *)((long)param_2 + 0xcc);
      puVar2 = (undefined8 *)param_1[1];
      uVar7 = *(undefined8 *)*(undefined (*) [16])(param_2 + 0x25);
      uVar8 = param_2[0x26];
      local_50 = *(undefined (*) [16])(param_2 + 0x25);
      uVar3 = param_2[0x27];
      local_a0 = param_2[0x1b];
      uStack_98 = param_2[0x1c];
      local_90 = param_2[0x1d];
      uStack_88 = param_2[0x1e];
      local_80 = param_2[0x1f];
      local_78 = param_2[0x20];
      uStack_70 = param_2[0x21];
      local_54 = 1;
      local_68 = param_2[0x22];
      uStack_60 = param_2[0x23];
      cVar1 = *(char *)(puVar2 + 0x29);
      param_2[0x27] = 0;
      *(undefined (*) [16])(param_2 + 0x25) = (undefined  [16])0x0;
      local_58 = iVar10;
      local_40 = uVar3;
      local_38 = param_3;
      if (cVar1 == '\0') {
        FUN_0001c620(puVar2,&local_178);
        *(undefined4 *)(puVar2 + 0x28) = param_3;
        *(undefined *)(puVar2 + 0x29) = 1;
        uVar3 = local_168._0_8_;
        lVar13 = local_158 - local_168._0_8_;
        FUN_0001cf40(local_50);
        if (uVar3 != 0) {
          if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
            thunk_FUN_000d36e0(uVar3,lVar13);
            return;
          }
          goto LAB_0001d908;
        }
      }
      else {
        lVar13 = puVar2[2];
        lVar4 = puVar2[4];
        *puVar2 = local_178;
        *(undefined4 *)(puVar2 + 1) = local_170;
        puVar2[4] = local_158;
        local_158 = 0;
        puVar2[2] = uVar5;
        puVar2[3] = uVar6;
        local_168 = (undefined  [16])0x0;
        if (lVar13 != 0) {
          thunk_FUN_000d36e0(lVar13,lVar4 - lVar13);
        }
        puVar2[0x13] = local_e0;
        puVar2[5] = local_150;
        puVar2[6] = uStack_148;
        puVar2[7] = local_140;
        puVar2[8] = uStack_138;
        puVar2[0x14] = local_d8;
        puVar2[9] = local_130;
        puVar2[10] = uStack_128;
        *(undefined2 *)(puVar2 + 0x15) = local_d0;
        puVar2[0xb] = local_120;
        puVar2[0xc] = uStack_118;
        *(undefined8 *)((long)puVar2 + 0xcc) = local_ac;
        puVar2[0xd] = local_110;
        puVar2[0xe] = uStack_108;
        puVar2[0xf] = local_100;
        puVar2[0x10] = uStack_f8;
        puVar2[0x11] = local_f0;
        puVar2[0x12] = uStack_e8;
        puVar2[0x1f] = local_80;
        *(undefined8 *)((long)puVar2 + 0xbc) = local_bc;
        *(undefined8 *)((long)puVar2 + 0xc4) = uStack_b4;
        puVar2[0x1b] = local_a0;
        puVar2[0x1c] = uStack_98;
        puVar2[0x1d] = local_90;
        puVar2[0x1e] = uStack_88;
        *(undefined8 *)((long)puVar2 + 0xac) = local_cc;
        *(undefined8 *)((long)puVar2 + 0xb4) = uStack_c4;
        local_198 = puVar2[0x25];
        uStack_190 = puVar2[0x26];
        local_188 = puVar2[0x27];
        *(int *)(puVar2 + 0x24) = iVar10;
        *(undefined *)((long)puVar2 + 0x124) = 1;
        puVar2[0x27] = uVar3;
        puVar2[0x20] = local_78;
        puVar2[0x21] = uStack_70;
        puVar2[0x22] = local_68;
        puVar2[0x23] = uStack_60;
        puVar2[0x25] = uVar7;
        puVar2[0x26] = uVar8;
        local_40 = 0;
        local_50 = (undefined  [16])0x0;
        FUN_0001cf40(&local_198);
        *(undefined4 *)(puVar2 + 0x28) = param_3;
        FUN_0001cf40(local_50);
      }
    }
  }
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_0001d908:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


