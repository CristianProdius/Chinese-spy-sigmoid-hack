// ===== FUNC 284f0 size=4234

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 * FUN_000284f0(undefined8 *param_1,long param_2,long param_3,undefined4 param_4)

{
  long lVar1;
  undefined8 uVar2;
  long *plVar3;
  undefined8 uVar4;
  long *plVar5;
  long *plVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  int *piVar11;
  int iVar12;
  int iVar13;
  long lVar14;
  int *piVar15;
  long lVar16;
  int *piVar17;
  int iVar18;
  ulong uVar19;
  long *plVar20;
  undefined8 *puVar21;
  long *plVar22;
  long in_FS_OFFSET;
  double dVar23;
  ulong local_720;
  ulong local_718;
  long local_700;
  double local_6d0;
  double *local_6c8;
  undefined8 *local_6c0;
  undefined8 local_6b8;
  undefined8 uStack_6b0;
  undefined8 local_6a8;
  undefined local_698 [16];
  long local_688;
  long local_678;
  int local_5ec [30];
  char local_574;
  long *local_570;
  long *local_568;
  long local_560;
  undefined local_558 [16];
  long local_548 [2];
  long local_538;
  char acStack_4b8 [12];
  int aiStack_4ac [30];
  char local_434;
  undefined local_430 [24];
  undefined local_418 [16];
  long local_408 [2];
  long local_3f8;
  int aiStack_36c [30];
  char local_2f4;
  undefined local_2f0 [24];
  undefined local_2d8 [16];
  undefined local_2c8 [16];
  int local_2b8;
  int iStack_2b4;
  int iStack_2b0;
  undefined4 uStack_2ac;
  undefined4 local_2a8;
  undefined4 uStack_2a4;
  undefined8 local_2a0;
  undefined8 uStack_298;
  undefined8 local_290;
  undefined8 uStack_288;
  undefined8 local_280;
  undefined8 uStack_278;
  undefined8 local_270;
  undefined8 uStack_268;
  undefined8 local_260;
  undefined8 uStack_258;
  undefined8 local_250;
  undefined8 uStack_248;
  undefined8 local_240;
  undefined8 local_238;
  undefined2 local_230;
  undefined8 local_22c;
  undefined8 uStack_224;
  undefined8 local_21c;
  undefined8 uStack_214;
  undefined8 local_20c;
  undefined8 local_200;
  undefined8 uStack_1f8;
  undefined8 local_1f0;
  undefined8 uStack_1e8;
  undefined8 local_1e0;
  undefined8 local_1d8;
  undefined8 uStack_1d0;
  undefined8 local_1c8;
  undefined8 uStack_1c0;
  int local_1b8;
  char local_1b4;
  undefined local_1b0 [16];
  long local_1a0;
  long *local_198 [2];
  long local_188 [2];
  undefined4 local_178;
  undefined4 uStack_174;
  int iStack_170;
  undefined4 uStack_16c;
  undefined4 local_168;
  undefined4 uStack_164;
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
  undefined8 local_f8;
  undefined2 local_f0;
  undefined8 local_ec;
  undefined8 uStack_e4;
  undefined8 local_dc;
  undefined8 uStack_d4;
  undefined8 local_cc;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 local_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 local_98;
  undefined8 uStack_90;
  undefined8 local_88;
  undefined8 uStack_80;
  long *local_70;
  long *local_68;
  long local_60;
  int local_58;
  char local_50;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  puVar21 = param_1;
  for (lVar14 = 0x2a; lVar14 != 0; lVar14 = lVar14 + -1) {
    *puVar21 = 0;
    puVar21 = puVar21 + 1;
  }
  lVar14 = *(long *)(param_3 + 0x10);
  lVar16 = *(long *)(param_3 + 0x18);
  local_6d0 = DAT_000e2e30;
  local_6c8 = &local_6d0;
  local_6c0 = param_1;
  if (0 < (int)(lVar16 - lVar14 >> 3) * -0x55555555) {
    uVar19 = 0;
    do {
      if (*(int *)(lVar14 + 0x14 + uVar19 * 0x18) != 0) {
                    /* try { // try from 000285b0 to 000285b4 has its CatchHandler @ 00029681 */
        FUN_00026a00(local_418,param_3);
        iVar18 = (int)uVar19;
                    /* try { // try from 000285c5 to 000285dc has its CatchHandler @ 00029650 */
        FUN_0001a1c0(param_2,local_418,uVar19 & 0xffffffff,param_4);
        FUN_00026a00(local_2d8,local_418);
        if (local_1b4 != '\0') {
          piVar11 = &iStack_2b0;
          dVar23 = 0.0;
          piVar15 = (int *)&local_238;
          do {
            if (*(char *)piVar15 != '\0') {
              iVar12 = piVar11[1];
              if (2 < iVar12) {
                iVar12 = 2;
              }
              iVar13 = *piVar11;
              if (4 < iVar13) {
                iVar13 = 4;
              }
              dVar23 = dVar23 + (double)iVar12 * DAT_000e2de0 + (double)iVar13;
            }
            piVar11 = piVar11 + 3;
            piVar15 = (int *)((long)piVar15 + 1);
          } while ((int *)&local_238 != piVar11);
          dVar23 = (double)local_1b8 - dVar23 * _DAT_000e2de8;
          if (dVar23 < local_6d0) {
            local_6d0 = dVar23;
            FUN_0001c620(local_198,local_2d8);
            local_58 = iVar18;
            if (*(char *)(param_1 + 0x29) == '\0') {
              FUN_0001c620(param_1);
              *(int *)(param_1 + 0x28) = iVar18;
              *(undefined *)(param_1 + 0x29) = 1;
            }
            else {
              FUN_00018bf0(param_1,local_198);
              *(int *)(param_1 + 0x28) = local_58;
            }
            FUN_0001cf40(&local_70);
            FUN_0001cb50(local_188);
          }
        }
        FUN_0001cf40(local_1b0);
        if (local_2c8._0_8_ != 0) {
          thunk_FUN_000d36e0(local_2c8._0_8_,CONCAT44(iStack_2b4,local_2b8) - local_2c8._0_8_);
        }
        FUN_0001cf40(local_2f0);
        if (local_408[0] != 0) {
          thunk_FUN_000d36e0(local_408[0],local_3f8 - local_408[0]);
        }
        lVar14 = *(long *)(param_3 + 0x10);
        lVar16 = *(long *)(param_3 + 0x18);
      }
      uVar19 = uVar19 + 1;
    } while ((int)uVar19 < (int)(lVar16 - lVar14 >> 3) * -0x55555555);
  }
  local_700 = 0;
  piVar11 = local_5ec;
  do {
    uVar4 = DAT_000e2e80;
    if ((*(int *)(param_3 + 0x30 + local_700 * 0xc) != 0) ||
       (*(int *)(param_3 + 0xac + local_700 * 4) != 0)) {
      local_718 = 0;
      if (0 < (int)(lVar16 - *(long *)(param_3 + 0x10) >> 3) * -0x55555555) {
        do {
                    /* try { // try from 0002878d to 00028791 has its CatchHandler @ 00029681 */
          FUN_00026a00(local_698,param_3);
                    /* try { // try from 0002879f to 0002880a has its CatchHandler @ 00029677 */
          FUN_0001a1c0(param_2,local_698,local_718 & 0xffffffff,(undefined4)local_700);
          lVar14 = local_688;
          plVar22 = local_570;
          plVar20 = local_570;
          plVar3 = local_568;
          if (local_574 != '\0') {
LAB_0002884a:
            if (*piVar11 != 0) goto LAB_000287d0;
            lVar16 = local_688 + local_718 * 0x18;
            lVar14 = local_688;
            plVar22 = local_570;
            plVar20 = local_570;
            plVar3 = local_568;
            if (*(int *)(lVar16 + 0xc) + *(int *)(lVar16 + 0x10) + *(int *)(lVar16 + 0x14) < 3) {
              uStack_164 = 0;
              local_178 = 0;
              uStack_174 = (undefined4)_DAT_000e2e90;
              iStack_170 = (int)((ulong)_DAT_000e2e90 >> 0x20);
              uStack_16c = (undefined4)_UNK_000e2e98;
              local_168 = (undefined4)((ulong)_UNK_000e2e98 >> 0x20);
              local_198[0] = local_188;
                    /* try { // try from 000288cc to 000288d0 has its CatchHandler @ 00029677 */
              FUN_00017bf0(local_198,"load");
              local_178 = (undefined4)local_718;
                    /* try { // try from 000288ea to 000288ee has its CatchHandler @ 000295a0 */
              FUN_00019ec0(param_2,local_698,local_198,0);
              if (local_198[0] != local_188) {
                thunk_FUN_000d36e0(local_198[0],local_188[0] + 1);
              }
                    /* try { // try from 00028921 to 00028935 has its CatchHandler @ 00029677 */
              FUN_0001a1c0(param_2,local_698,local_718 & 0xffffffff,param_4);
              FUN_00026a00(local_2d8,local_698);
              lVar14 = local_1a0;
              iVar18 = local_1b8;
              uVar9 = local_1b0._0_8_;
              uVar10 = local_1b0._8_8_;
              uVar7 = local_2c8._0_8_;
              if (local_1b4 == '\0') goto LAB_000289d6;
              piVar15 = &iStack_2b0;
              dVar23 = 0.0;
              piVar17 = (int *)&local_238;
              do {
                if (*(char *)piVar17 != '\0') {
                  iVar12 = piVar15[1];
                  if (2 < iVar12) {
                    iVar12 = 2;
                  }
                  iVar13 = *piVar15;
                  if (4 < iVar13) {
                    iVar13 = 4;
                  }
                  dVar23 = dVar23 + (double)iVar12 * DAT_000e2de0 + (double)iVar13;
                }
                piVar15 = piVar15 + 3;
                piVar17 = (int *)((long)piVar17 + 1);
              } while (piVar15 != (int *)&local_238);
              dVar23 = (double)local_1b8 - dVar23 * _DAT_000e2de8;
              if (dVar23 < local_6d0) {
                iStack_170 = iStack_2b0;
                uStack_16c = uStack_2ac;
                local_168 = local_2a8;
                uStack_164 = uStack_2a4;
                uVar8 = local_2c8._8_8_;
                local_160 = local_2a0;
                uStack_158 = uStack_298;
                local_2c8 = (undefined  [16])0x0;
                uVar2 = CONCAT44(iStack_2b4,local_2b8);
                local_100 = local_240;
                local_f8 = local_238;
                local_f0 = local_230;
                local_2b8 = 0;
                iStack_2b4 = 0;
                local_150 = local_290;
                uStack_148 = uStack_288;
                local_140 = local_280;
                uStack_138 = uStack_278;
                local_130 = local_270;
                uStack_128 = uStack_268;
                local_120 = local_260;
                uStack_118 = uStack_258;
                local_110 = local_250;
                uStack_108 = uStack_248;
                local_ec = local_22c;
                uStack_e4 = uStack_224;
                local_1a0 = 0;
                local_dc = local_21c;
                uStack_d4 = uStack_214;
                local_cc = local_20c;
                local_a0 = local_1e0;
                local_c0 = local_200;
                uStack_b8 = uStack_1f8;
                local_b0 = local_1f0;
                uStack_a8 = uStack_1e8;
                local_98 = local_1d8;
                uStack_90 = uStack_1d0;
                local_88 = local_1c8;
                uStack_80 = uStack_1c0;
                local_1b0 = (undefined  [16])0x0;
                local_6d0 = dVar23;
                if (*(char *)(param_1 + 0x29) == '\0') {
                  *(undefined8 *)((long)param_1 + 0xcc) = local_20c;
                  *param_1 = local_2d8._0_8_;
                  *(undefined4 *)(param_1 + 1) = local_2d8._8_4_;
                  param_1[4] = uVar2;
                  param_1[0x13] = local_240;
                  param_1[0x14] = local_238;
                  *(undefined2 *)(param_1 + 0x15) = local_230;
                  param_1[0x1f] = local_1e0;
                  *(int *)(param_1 + 0x24) = local_1b8;
                  *(undefined *)((long)param_1 + 0x124) = 1;
                  param_1[0x27] = lVar14;
                  *(undefined4 *)(param_1 + 0x28) = (undefined4)local_718;
                  *(undefined *)(param_1 + 0x29) = 1;
                  param_1[2] = uVar7;
                  param_1[3] = uVar8;
                  param_1[5] = CONCAT44(uStack_2ac,iStack_2b0);
                  param_1[6] = CONCAT44(uStack_2a4,local_2a8);
                  param_1[7] = local_2a0;
                  param_1[8] = uStack_298;
                  param_1[9] = local_290;
                  param_1[10] = uStack_288;
                  param_1[0xb] = local_280;
                  param_1[0xc] = uStack_278;
                  param_1[0xd] = local_270;
                  param_1[0xe] = uStack_268;
                  param_1[0xf] = local_260;
                  param_1[0x10] = uStack_258;
                  param_1[0x11] = local_250;
                  param_1[0x12] = uStack_248;
                  *(undefined8 *)((long)param_1 + 0xac) = local_22c;
                  *(undefined8 *)((long)param_1 + 0xb4) = uStack_224;
                  *(undefined8 *)((long)param_1 + 0xbc) = local_21c;
                  *(undefined8 *)((long)param_1 + 0xc4) = uStack_214;
                  param_1[0x1b] = local_200;
                  param_1[0x1c] = uStack_1f8;
                  param_1[0x1d] = local_1f0;
                  param_1[0x1e] = uStack_1e8;
                  param_1[0x20] = local_1d8;
                  param_1[0x21] = uStack_1d0;
                  param_1[0x22] = local_1c8;
                  param_1[0x23] = uStack_1c0;
                  param_1[0x25] = uVar9;
                  param_1[0x26] = uVar10;
                  plVar22 = local_570;
                  plVar20 = local_570;
                  plVar3 = local_568;
                }
                else {
                  lVar16 = param_1[2];
                  lVar1 = param_1[4];
                  *param_1 = local_2d8._0_8_;
                  *(undefined4 *)(param_1 + 1) = local_2d8._8_4_;
                  param_1[4] = uVar2;
                  param_1[2] = uVar7;
                  param_1[3] = uVar8;
                  if (lVar16 != 0) {
                    thunk_FUN_000d36e0(lVar16,lVar1 - lVar16);
                  }
                  param_1[0x13] = local_100;
                  param_1[5] = CONCAT44(uStack_16c,iStack_170);
                  param_1[6] = CONCAT44(uStack_164,local_168);
                  param_1[7] = local_160;
                  param_1[8] = uStack_158;
                  param_1[0x14] = local_f8;
                  param_1[9] = local_150;
                  param_1[10] = uStack_148;
                  *(undefined2 *)(param_1 + 0x15) = local_f0;
                  param_1[0xb] = local_140;
                  param_1[0xc] = uStack_138;
                  *(undefined8 *)((long)param_1 + 0xcc) = local_cc;
                  param_1[0xd] = local_130;
                  param_1[0xe] = uStack_128;
                  param_1[0xf] = local_120;
                  param_1[0x10] = uStack_118;
                  param_1[0x11] = local_110;
                  param_1[0x12] = uStack_108;
                  *(undefined8 *)((long)param_1 + 0xac) = local_ec;
                  *(undefined8 *)((long)param_1 + 0xb4) = uStack_e4;
                  *(undefined8 *)((long)param_1 + 0xbc) = local_dc;
                  *(undefined8 *)((long)param_1 + 0xc4) = uStack_d4;
                  param_1[0x1b] = local_c0;
                  param_1[0x1c] = uStack_b8;
                  param_1[0x1d] = local_b0;
                  param_1[0x1e] = uStack_a8;
                  param_1[0x1f] = local_a0;
                  local_6a8 = param_1[0x27];
                  *(int *)(param_1 + 0x24) = iVar18;
                  *(undefined *)((long)param_1 + 0x124) = 1;
                  local_6b8 = param_1[0x25];
                  uStack_6b0 = param_1[0x26];
                  param_1[0x27] = lVar14;
                  param_1[0x20] = local_98;
                  param_1[0x21] = uStack_90;
                  param_1[0x22] = local_88;
                  param_1[0x23] = uStack_80;
                  param_1[0x25] = uVar9;
                  param_1[0x26] = uVar10;
                  FUN_0001cf40(&local_6b8);
                  *(undefined4 *)(param_1 + 0x28) = (undefined4)local_718;
                  plVar22 = local_570;
                  plVar20 = local_570;
                  plVar3 = local_568;
                }
              }
              else {
LAB_000289d6:
                lVar16 = CONCAT44(iStack_2b4,local_2b8);
                for (plVar22 = (long *)local_1b0._0_8_; (long *)uVar10 != plVar22;
                    plVar22 = plVar22 + 7) {
                  if ((long *)*plVar22 != plVar22 + 2) {
                    thunk_FUN_000d36e0((long *)*plVar22,plVar22[2] + 1);
                  }
                }
                if ((long *)uVar9 != (long *)0x0) {
                  thunk_FUN_000d36e0(uVar9,lVar14 - uVar9);
                }
                plVar22 = local_570;
                plVar20 = local_570;
                plVar3 = local_568;
                if (uVar7 != 0) {
                  thunk_FUN_000d36e0(uVar7,lVar16 - uVar7);
                  plVar22 = local_570;
                  plVar20 = local_570;
                  plVar3 = local_568;
                }
              }
              for (; plVar6 = local_568, plVar5 = local_570, local_568 != plVar22;
                  plVar22 = plVar22 + 7) {
                local_570 = plVar20;
                local_568 = plVar3;
                if ((long *)*plVar22 != plVar22 + 2) {
                  thunk_FUN_000d36e0((long *)*plVar22,plVar22[2] + 1);
                }
                plVar20 = local_570;
                plVar3 = local_568;
                local_568 = plVar6;
                local_570 = plVar5;
              }
              local_568 = plVar3;
              if (local_570 != (long *)0x0) {
                thunk_FUN_000d36e0(local_570,local_560 - (long)local_570);
                local_570 = plVar20;
                plVar20 = local_570;
              }
              local_570 = plVar20;
              if (local_688 != 0) {
                thunk_FUN_000d36e0(local_688,local_678 - local_688);
              }
              goto LAB_00028acf;
            }
          }
joined_r0x00028b26:
          for (; plVar6 = local_568, plVar5 = local_570, lVar16 = local_688, local_688 = lVar14,
              local_568 != plVar22; plVar22 = plVar22 + 7) {
            local_570 = plVar20;
            local_568 = plVar3;
            if ((long *)*plVar22 != plVar22 + 2) {
              thunk_FUN_000d36e0((long *)*plVar22,plVar22[2] + 1);
            }
            lVar14 = local_688;
            plVar20 = local_570;
            plVar3 = local_568;
            local_568 = plVar6;
            local_570 = plVar5;
            local_688 = lVar16;
          }
          local_568 = plVar3;
          if (local_570 != (long *)0x0) {
            thunk_FUN_000d36e0(local_570,local_560 - (long)local_570);
            local_570 = plVar20;
            plVar20 = local_570;
          }
          local_570 = plVar20;
          if (lVar16 != 0) {
            thunk_FUN_000d36e0(lVar16,local_678 - lVar16);
          }
LAB_00028acf:
          local_718 = local_718 + 1;
          lVar16 = *(long *)(param_3 + 0x18);
        } while ((int)local_718 < (int)(lVar16 - *(long *)(param_3 + 0x10) >> 3) * -0x55555555);
      }
    }
    local_700 = local_700 + 1;
    piVar11 = piVar11 + 1;
  } while (local_700 != 10);
  uVar19 = 0;
  do {
    if (*(int *)(param_2 + 0x18 + uVar19 * 4) == 2) {
                    /* try { // try from 00028fe3 to 00028fe7 has its CatchHandler @ 00029681 */
      FUN_00026a00(local_558,param_3);
      if (acStack_4b8[uVar19] == '\0') {
        FUN_00027250(local_198,param_2,local_558,uVar19 & 0xffffffff);
        if (local_50 != '\0') {
          FUN_00018bf0(local_558,local_198);
          local_2b8 = 0;
          uStack_2ac = 0;
          uStack_2a4 = 0;
          iStack_2b4 = (int)DAT_000e2e80;
          iStack_2b0 = (int)((ulong)DAT_000e2e80 >> 0x20);
          local_2a8 = 0xffffffff;
          local_2d8 = (undefined  [16])0x0;
          local_2c8 = (undefined  [16])0x0;
                    /* try { // try from 00029132 to 00029136 has its CatchHandler @ 0002967c */
          FUN_00018b10(local_2d8,"build_workshop");
          local_2b8 = local_58;
                    /* try { // try from 00029150 to 00029154 has its CatchHandler @ 0002958f */
          FUN_00019ec0(param_2,local_558,local_2d8,0);
          FUN_000b07c0(local_2d8);
          if (local_50 != '\0') {
            local_50 = '\0';
            FUN_0001cf40(&local_70);
            if (local_188[0] != 0) {
              thunk_FUN_000d36e0(local_188[0],CONCAT44(uStack_174,local_178) - local_188[0]);
            }
          }
          goto LAB_00028ffa;
        }
      }
      else {
LAB_00028ffa:
        if ((local_434 != '\0') && (aiStack_4ac[uVar19] == 0)) {
                    /* try { // try from 00029027 to 000290c4 has its CatchHandler @ 0002964b */
          FUN_00027250(local_198,param_2,local_558,uVar19 & 0xffffffff);
          if (local_50 != '\0') {
            FUN_00018bf0(local_558,local_198);
            local_2b8 = 0;
            uStack_2ac = 0;
            uStack_2a4 = 0;
            iStack_2b4 = (int)DAT_000e2e80;
            iVar18 = iStack_2b4;
            iStack_2b0 = (int)((ulong)DAT_000e2e80 >> 0x20);
            iVar12 = iStack_2b0;
            local_2a8 = 0xffffffff;
            local_2d8 = (undefined  [16])0x0;
            local_2c8 = (undefined  [16])0x0;
                    /* try { // try from 00029292 to 00029296 has its CatchHandler @ 00029599 */
            FUN_00018b10(local_2d8,"craft");
            local_2b8 = local_58;
                    /* try { // try from 000292b1 to 000292b5 has its CatchHandler @ 0002959e */
            FUN_00019ec0(param_2,local_558,local_2d8,0);
            FUN_000b07c0(local_2d8);
            local_720 = 0;
            if (0 < (int)(*(long *)(param_3 + 0x18) - *(long *)(param_3 + 0x10) >> 3) * -0x55555555)
            {
              do {
                    /* try { // try from 000292fe to 00029302 has its CatchHandler @ 00029599 */
                FUN_00026a00(local_418,local_558);
                    /* try { // try from 00029312 to 0002936c has its CatchHandler @ 00029594 */
                FUN_0001a1c0(param_2,local_418,local_720 & 0xffffffff,uVar19 & 0xffffffff);
                while (local_2f4 != '\0') {
                  while( true ) {
                    if (aiStack_36c[uVar19] == 0) {
                      lVar14 = local_408[0] + local_720 * 0x18;
                      if (*(int *)(lVar14 + 0x10) + *(int *)(lVar14 + 0xc) + *(int *)(lVar14 + 0x14)
                          < 3) {
                        uStack_2a4 = 0;
                        local_2b8 = 0;
                        local_2d8 = (undefined  [16])0x0;
                        local_2c8 = (undefined  [16])0x0;
                        iStack_2b4 = (int)_DAT_000e2e90;
                        iStack_2b0 = (int)((ulong)_DAT_000e2e90 >> 0x20);
                        uStack_2ac = (undefined4)_UNK_000e2e98;
                        local_2a8 = (undefined4)((ulong)_UNK_000e2e98 >> 0x20);
                    /* try { // try from 0002948c to 00029490 has its CatchHandler @ 00029594 */
                        FUN_00018b10(local_2d8,"load");
                        local_2b8 = (int)local_720;
                    /* try { // try from 000294a8 to 000294ac has its CatchHandler @ 00029641 */
                        FUN_00019ec0(param_2,local_418,local_2d8,0);
                        FUN_000b07c0(local_2d8);
                    /* try { // try from 000294c4 to 000294d3 has its CatchHandler @ 00029594 */
                        FUN_0001a1c0(param_2,local_418,local_720 & 0xffffffff,param_4);
                        FUN_00026a00(local_2d8,local_418);
                        FUN_0001d480(&local_6c8,local_2d8,local_720 & 0xffffffff);
                        FUN_0001cf40(local_1b0);
                        FUN_0001cb50(local_2c8);
                      }
                      goto LAB_000293aa;
                    }
                    iStack_2b0 = -1;
                    uStack_2ac = 0;
                    local_2a8 = 0xffffffff;
                    uStack_2a4 = 0;
                    local_2d8._0_8_ = local_2c8;
                    local_2b8 = iVar18;
                    iStack_2b4 = iVar12;
                    FUN_00017bf0(local_2d8,&DAT_000e0454);
                    /* try { // try from 00029379 to 0002937d has its CatchHandler @ 00029649 */
                    FUN_00019ec0(param_2,local_418,local_2d8,0);
                    if ((undefined *)local_2d8._0_8_ == local_2c8) break;
                    thunk_FUN_000d36e0(local_2d8._0_8_,local_2c8._0_8_ + 1);
                    if (local_2f4 == '\0') goto LAB_000293aa;
                  }
                }
LAB_000293aa:
                FUN_0001cf40(local_2f0);
                FUN_0001cb50(local_408);
                local_720 = local_720 + 1;
              } while ((int)local_720 <
                       (int)(*(long *)(param_3 + 0x18) - *(long *)(param_3 + 0x10) >> 3) *
                       -0x55555555);
            }
            plVar22 = local_68;
            if (local_50 != '\0') {
              local_50 = '\0';
              for (plVar20 = local_70; plVar22 != plVar20; plVar20 = plVar20 + 7) {
                if ((long *)*plVar20 != plVar20 + 2) {
                  thunk_FUN_000d36e0((long *)*plVar20,plVar20[2] + 1);
                }
              }
              if (local_70 != (long *)0x0) {
                thunk_FUN_000d36e0(local_70,local_60 - (long)local_70);
              }
              if (local_188[0] != 0) {
                thunk_FUN_000d36e0(local_188[0],CONCAT44(uStack_174,local_178) - local_188[0]);
              }
            }
            FUN_0001cf40(local_430);
            FUN_0001cb50(local_548);
            goto joined_r0x00029070;
          }
        }
      }
      FUN_0001cf40(local_430);
      if (local_548[0] != 0) {
        thunk_FUN_000d36e0(local_548[0],local_538 - local_548[0]);
      }
    }
joined_r0x00029070:
    uVar19 = uVar19 + 1;
    if (uVar19 == 10) {
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        return param_1;
      }
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
  } while( true );
LAB_000287d0:
  local_178 = (undefined4)uVar4;
  uStack_174 = (undefined4)((ulong)uVar4 >> 0x20);
  iStack_170 = -1;
  uStack_16c = 0;
  local_168 = 0xffffffff;
  uStack_164 = 0;
  local_198[0] = local_188;
  FUN_00017bf0(local_198,&DAT_000e0454,&DAT_000e0458);
                    /* try { // try from 00028819 to 0002881d has its CatchHandler @ 00029672 */
  FUN_00019ec0(param_2,local_698,local_198,0);
  if (local_198[0] != local_188) {
    thunk_FUN_000d36e0(local_198[0],local_188[0] + 1);
  }
  lVar14 = local_688;
  plVar22 = local_570;
  plVar20 = local_570;
  plVar3 = local_568;
  if (local_574 == '\0') goto joined_r0x00028b26;
  goto LAB_0002884a;
}


