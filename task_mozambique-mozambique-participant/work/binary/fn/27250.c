// ===== FUNC 27250 size=4652

undefined8 * FUN_00027250(undefined8 *param_1,double *param_2,long param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  long lVar3;
  long *plVar4;
  long *plVar5;
  long lVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  int iVar12;
  int iVar13;
  long lVar14;
  uint uVar15;
  long *plVar16;
  undefined8 *puVar17;
  long in_FS_OFFSET;
  double dVar18;
  undefined8 uStack_500;
  undefined8 *local_4e8;
  undefined4 *local_4d8;
  long *local_498;
  int local_48c [3];
  double local_480;
  int *local_478;
  double *local_470;
  double *local_468;
  undefined8 *local_460;
  int local_44c;
  int local_448 [2];
  undefined local_440 [8];
  undefined4 local_438;
  undefined8 local_434;
  undefined4 local_42c;
  undefined local_428 [16];
  long local_418 [2];
  long local_408;
  long *local_300;
  long *local_2f8;
  long local_2f0;
  char local_2e8;
  undefined8 local_2d8;
  undefined4 local_2d0;
  undefined local_2c8 [16];
  long local_2b8;
  undefined8 local_2b0;
  undefined8 uStack_2a8;
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
  undefined8 local_1a0;
  char local_198;
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
  uint local_48;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  lVar14 = 0x2a;
  local_448[1] = 0;
  piVar1 = (int *)(param_3 + 0x28 + (long)param_4 * 0xc);
  local_44c = 2 - *piVar1;
  if (local_44c < 0) {
    local_44c = 0;
  }
  local_448[0] = 1 - piVar1[1];
  puVar17 = param_1;
  if (local_448[0] < 0) {
    local_448[0] = 0;
  }
  for (; lVar14 != 0; lVar14 = lVar14 + -1) {
    *puVar17 = 0;
    puVar17 = puVar17 + 1;
  }
  local_480 = DAT_000e2e30;
  local_478 = local_48c;
  local_468 = &local_480;
  local_48c[0] = param_4;
  local_470 = param_2;
  local_460 = param_1;
  if (local_448[0] + local_44c == 0) {
    if (0 < (int)(*(long *)(param_3 + 0x18) - *(long *)(param_3 + 0x10) >> 3) * -0x55555555) {
      uVar15 = 0;
      do {
        FUN_00026a00(local_428,param_3);
                    /* try { // try from 00027804 to 00027817 has its CatchHandler @ 000284a9 */
        FUN_0001a1c0(param_2,local_428,uVar15,local_48c[0]);
        FUN_00026a00(&local_2d8,local_428);
        uVar8 = local_1a0;
        iVar2 = local_1b8;
        lVar14 = local_2b8;
        local_198 = 1;
        uVar7 = local_2c8._0_8_;
        if (local_1b4 == '\0') {
LAB_000278be:
          local_198 = '\0';
          lVar14 = local_2b8 - local_2c8._0_8_;
          FUN_0001cf40(local_1b0);
          if (uVar7 != 0) {
            thunk_FUN_000d36e0(uVar7,lVar14);
          }
        }
        else {
          iVar12 = *(int *)((long)&local_2b0 + (long)local_48c[0] * 0xc + 4) + -1;
          if (iVar12 < 0) {
            iVar12 = 0;
          }
          iVar13 = *(int *)((long)&local_2b0 + (long)local_48c[0] * 0xc) + -2;
          if (iVar13 < 0) {
            iVar13 = 0;
          }
          dVar18 = (double)local_1b8 - ((double)iVar12 * DAT_000e2de0 + (double)iVar13) * *param_2;
          if (local_480 <= dVar18) goto LAB_000278be;
          uVar9 = local_2c8._8_8_;
          local_f0 = local_240;
          local_160 = local_2b0;
          uStack_158 = uStack_2a8;
          local_150 = local_2a0;
          uStack_148 = uStack_298;
          local_e8 = local_238;
          local_140 = local_290;
          uStack_138 = uStack_288;
          local_130 = local_280;
          uStack_128 = uStack_278;
          local_e0 = local_230;
          local_110 = local_260;
          uStack_108 = uStack_258;
          local_100 = local_250;
          uStack_f8 = uStack_248;
          local_dc = local_22c;
          uStack_d4 = uStack_224;
          local_188 = local_2d8;
          local_180 = local_2d0;
          local_168 = local_2b8;
          local_2b8 = 0;
          local_178 = local_2c8;
          local_2c8 = (undefined  [16])0x0;
          local_120 = local_270;
          uStack_118 = uStack_268;
          uVar10 = local_1b0._0_8_;
          uVar11 = local_1b0._8_8_;
          local_68 = local_1b8;
          local_bc = local_20c;
          local_64 = 1;
          local_90 = local_1e0;
          local_cc = local_21c;
          uStack_c4 = uStack_214;
          local_50 = local_1a0;
          local_1a0 = 0;
          local_b0 = local_200;
          uStack_a8 = uStack_1f8;
          local_a0 = local_1f0;
          uStack_98 = uStack_1e8;
          local_88 = local_1d8;
          uStack_80 = uStack_1d0;
          local_78 = local_1c8;
          uStack_70 = uStack_1c0;
          local_60 = local_1b0;
          local_1b0 = (undefined  [16])0x0;
          local_480 = dVar18;
          local_48 = uVar15;
          if (*(char *)(param_1 + 0x29) == '\0') {
            FUN_0001c620(param_1,&local_188);
            *(uint *)(param_1 + 0x28) = uVar15;
            *(undefined *)(param_1 + 0x29) = 1;
          }
          else {
            lVar6 = param_1[2];
            *param_1 = local_2d8;
            *(undefined4 *)(param_1 + 1) = local_2d0;
            lVar3 = param_1[4];
            local_168 = 0;
            param_1[4] = lVar14;
            param_1[2] = uVar7;
            param_1[3] = uVar9;
            local_178 = (undefined  [16])0x0;
            if (lVar6 != 0) {
              thunk_FUN_000d36e0(lVar6,lVar3 - lVar6);
            }
            param_1[5] = local_160;
            param_1[6] = uStack_158;
            param_1[0x13] = local_f0;
            param_1[7] = local_150;
            param_1[8] = uStack_148;
            param_1[0x14] = local_e8;
            param_1[9] = local_140;
            param_1[10] = uStack_138;
            *(undefined2 *)(param_1 + 0x15) = local_e0;
            param_1[0xb] = local_130;
            param_1[0xc] = uStack_128;
            *(undefined8 *)((long)param_1 + 0xcc) = local_bc;
            param_1[0xd] = local_120;
            param_1[0xe] = uStack_118;
            param_1[0x1f] = local_90;
            param_1[0xf] = local_110;
            param_1[0x10] = uStack_108;
            param_1[0x1b] = local_b0;
            param_1[0x1c] = uStack_a8;
            param_1[0x11] = local_100;
            param_1[0x12] = uStack_f8;
            *(undefined8 *)((long)param_1 + 0xbc) = local_cc;
            *(undefined8 *)((long)param_1 + 0xc4) = uStack_c4;
            *(undefined8 *)((long)param_1 + 0xac) = local_dc;
            *(undefined8 *)((long)param_1 + 0xb4) = uStack_d4;
            param_1[0x1d] = local_a0;
            param_1[0x1e] = uStack_98;
            lVar14 = param_1[0x27];
            *(int *)(param_1 + 0x24) = iVar2;
            plVar5 = (long *)param_1[0x25];
            plVar16 = (long *)param_1[0x26];
            *(undefined *)((long)param_1 + 0x124) = 1;
            param_1[0x27] = uVar8;
            local_50 = 0;
            param_1[0x20] = local_88;
            param_1[0x21] = uStack_80;
            param_1[0x22] = local_78;
            param_1[0x23] = uStack_70;
            param_1[0x25] = uVar10;
            param_1[0x26] = uVar11;
            local_60 = (undefined  [16])0x0;
            for (plVar4 = plVar5; plVar4 != plVar16; plVar4 = plVar4 + 7) {
              if ((long *)*plVar4 != plVar4 + 2) {
                thunk_FUN_000d36e0((long *)*plVar4,plVar4[2] + 1);
              }
            }
            if (plVar5 != (long *)0x0) {
              thunk_FUN_000d36e0(plVar5,lVar14 - (long)plVar5);
            }
            *(uint *)(param_1 + 0x28) = uVar15;
          }
          FUN_0001cf40(local_60);
          FUN_0001cb50(local_178);
          local_198 = '\0';
          FUN_0001cf40(local_1b0);
        }
        plVar5 = local_2f8;
        plVar4 = local_300;
        if (local_2f8 != local_300) {
          local_498 = local_300;
          do {
            if ((long *)*local_498 != local_498 + 2) {
              thunk_FUN_000d36e0((long *)*local_498,local_498[2] + 1);
            }
            local_498 = local_498 + 7;
          } while (plVar5 != local_498);
        }
        if (plVar4 != (long *)0x0) {
          thunk_FUN_000d36e0(plVar4,local_2f0 - (long)plVar4);
        }
        if (local_418[0] != 0) {
          thunk_FUN_000d36e0(local_418[0],local_408 - local_418[0]);
        }
        uVar15 = uVar15 + 1;
      } while ((int)uVar15 <
               (int)(*(long *)(param_3 + 0x18) - *(long *)(param_3 + 0x10) >> 3) * -0x55555555);
    }
  }
  else {
    lVar14 = *(long *)(param_3 + 0x18);
    uVar15 = 0;
    if (0 < (int)(lVar14 - *(long *)(param_3 + 0x10) >> 3) * -0x55555555) {
      do {
                    /* try { // try from 00027384 to 000277f1 has its CatchHandler @ 000284a4 */
        FUN_00026c80(&local_2d8,param_2,param_3,uVar15,&local_44c,local_48c[0],1);
        uVar7 = local_1a0;
        iVar2 = local_1b8;
        lVar14 = local_2b8;
        if (local_198 != '\0') {
          uVar8 = local_2c8._0_8_;
          if (local_1b4 != '\0') {
            iVar12 = *(int *)((long)&local_2b0 + (long)local_48c[0] * 0xc + 4) + -1;
            if (iVar12 < 0) {
              iVar12 = 0;
            }
            iVar13 = *(int *)((long)&local_2b0 + (long)local_48c[0] * 0xc) + -2;
            if (iVar13 < 0) {
              iVar13 = 0;
            }
            dVar18 = (double)local_1b8 - ((double)iVar12 * DAT_000e2de0 + (double)iVar13) * *param_2
            ;
            if (dVar18 < local_480) {
              uVar9 = local_2c8._8_8_;
              local_f0 = local_240;
              local_160 = local_2b0;
              uStack_158 = uStack_2a8;
              local_e8 = local_238;
              local_150 = local_2a0;
              uStack_148 = uStack_298;
              local_140 = local_290;
              uStack_138 = uStack_288;
              local_e0 = local_230;
              local_120 = local_270;
              uStack_118 = uStack_268;
              local_110 = local_260;
              uStack_108 = uStack_258;
              local_100 = local_250;
              uStack_f8 = uStack_248;
              local_dc = local_22c;
              uStack_d4 = uStack_224;
              local_188 = local_2d8;
              local_180 = local_2d0;
              local_168 = local_2b8;
              local_2b8 = 0;
              local_178 = local_2c8;
              local_2c8 = (undefined  [16])0x0;
              local_130 = local_280;
              uStack_128 = uStack_278;
              uVar10 = local_1b0._0_8_;
              uVar11 = local_1b0._8_8_;
              local_68 = local_1b8;
              local_bc = local_20c;
              local_64 = 1;
              local_90 = local_1e0;
              local_50 = local_1a0;
              local_cc = local_21c;
              uStack_c4 = uStack_214;
              local_1a0 = 0;
              local_b0 = local_200;
              uStack_a8 = uStack_1f8;
              local_a0 = local_1f0;
              uStack_98 = uStack_1e8;
              local_88 = local_1d8;
              uStack_80 = uStack_1d0;
              local_78 = local_1c8;
              uStack_70 = uStack_1c0;
              local_60 = local_1b0;
              local_1b0 = (undefined  [16])0x0;
              local_480 = dVar18;
              local_48 = uVar15;
              if (*(char *)(param_1 + 0x29) == '\0') {
                FUN_0001c620(param_1,&local_188);
                *(undefined *)(param_1 + 0x29) = 1;
                *(uint *)(param_1 + 0x28) = uVar15;
              }
              else {
                *param_1 = local_2d8;
                lVar6 = param_1[2];
                *(undefined4 *)(param_1 + 1) = local_2d0;
                lVar3 = param_1[4];
                local_168 = 0;
                param_1[4] = lVar14;
                param_1[2] = uVar8;
                param_1[3] = uVar9;
                local_178 = (undefined  [16])0x0;
                if (lVar6 != 0) {
                  thunk_FUN_000d36e0(lVar6,lVar3 - lVar6);
                }
                param_1[0x13] = local_f0;
                param_1[5] = local_160;
                param_1[6] = uStack_158;
                param_1[0x14] = local_e8;
                param_1[7] = local_150;
                param_1[8] = uStack_148;
                *(undefined2 *)(param_1 + 0x15) = local_e0;
                param_1[9] = local_140;
                param_1[10] = uStack_138;
                *(undefined8 *)((long)param_1 + 0xcc) = local_bc;
                param_1[0xb] = local_130;
                param_1[0xc] = uStack_128;
                param_1[0xd] = local_120;
                param_1[0xe] = uStack_118;
                param_1[0xf] = local_110;
                param_1[0x10] = uStack_108;
                *(undefined8 *)((long)param_1 + 0xac) = local_dc;
                *(undefined8 *)((long)param_1 + 0xb4) = uStack_d4;
                param_1[0x1f] = local_90;
                param_1[0x11] = local_100;
                param_1[0x12] = uStack_f8;
                *(undefined8 *)((long)param_1 + 0xbc) = local_cc;
                *(undefined8 *)((long)param_1 + 0xc4) = uStack_c4;
                param_1[0x1b] = local_b0;
                param_1[0x1c] = uStack_a8;
                param_1[0x1d] = local_a0;
                param_1[0x1e] = uStack_98;
                plVar4 = (long *)param_1[0x25];
                *(int *)(param_1 + 0x24) = iVar2;
                plVar5 = (long *)param_1[0x26];
                lVar14 = param_1[0x27];
                *(undefined *)((long)param_1 + 0x124) = 1;
                param_1[0x27] = uVar7;
                local_50 = 0;
                param_1[0x20] = local_88;
                param_1[0x21] = uStack_80;
                param_1[0x22] = local_78;
                param_1[0x23] = uStack_70;
                param_1[0x25] = uVar10;
                param_1[0x26] = uVar11;
                local_60 = (undefined  [16])0x0;
                for (plVar16 = plVar4; plVar16 != plVar5; plVar16 = plVar16 + 7) {
                  if ((long *)*plVar16 != plVar16 + 2) {
                    thunk_FUN_000d36e0((long *)*plVar16,plVar16[2] + 1);
                  }
                }
                if (plVar4 != (long *)0x0) {
                  thunk_FUN_000d36e0(plVar4,lVar14 - (long)plVar4);
                }
                *(uint *)(param_1 + 0x28) = uVar15;
              }
              FUN_0001cf40(local_60);
              FUN_0001cb50(local_178);
              local_198 = '\0';
              uStack_500 = 0x27788;
              FUN_0001cf40(local_1b0);
              goto LAB_00027456;
            }
          }
          local_198 = '\0';
          lVar14 = local_2b8 - local_2c8._0_8_;
          uStack_500 = 0x27442;
          FUN_0001cf40(local_1b0);
          if (uVar8 != 0) {
            uStack_500 = 0x27456;
            thunk_FUN_000d36e0(uVar8,lVar14);
          }
        }
LAB_00027456:
        lVar14 = 0;
        iVar2 = local_44c;
        while( true ) {
          if ((iVar2 != 0) && (*(int *)((long)local_448 - lVar14) == 0)) {
            local_2d8 = 0;
            local_2d0 = 0;
            *(undefined4 *)((long)&local_2d8 + lVar14) = 3;
            FUN_00026c80(&local_188,param_2,param_3,uVar15,&local_2d8,local_48c[0]);
            uStack_500 = 0x27578;
            FUN_0001cfb0(&local_478,&local_188,uVar15);
            if ((char)local_48 != '\0') {
              local_48 = local_48 & 0xffffff00;
              FUN_0001cf40(local_60);
              uStack_500 = 0x2759b;
              FUN_0001cb50(local_178);
            }
          }
          if (lVar14 == 4) break;
          lVar14 = 4;
          iVar2 = local_448[0];
        }
        lVar14 = *(long *)(param_3 + 0x18);
        uVar15 = uVar15 + 1;
      } while ((int)uVar15 < (int)(lVar14 - *(long *)(param_3 + 0x10) >> 3) * -0x55555555);
    }
    if (((local_44c != 0) && (local_448[0] != 0)) && (*(int *)(param_3 + 0x120) < 0x32)) {
      local_4e8 = &local_434;
      local_4d8 = (undefined4 *)local_440;
      do {
        iVar2 = 0;
        if (0 < (int)(lVar14 - *(long *)(param_3 + 0x10) >> 3) * -0x55555555) {
          do {
            local_440 = (undefined  [8])0x0;
            local_438 = 0;
            *local_4d8 = 3;
                    /* try { // try from 00027cd3 to 00027cd7 has its CatchHandler @ 000284a4 */
            FUN_00026c80(local_428,param_2,param_3,iVar2,local_440,local_48c[0],1);
            lVar14 = *(long *)(param_3 + 0x18);
            lVar6 = *(long *)(param_3 + 0x10);
            if (local_2e8 != '\0') {
              local_434 = 0;
              local_42c = 0;
              *(undefined4 *)((long)local_4e8 + 4) = 3;
              uVar15 = 0;
              if (0 < (int)(lVar14 - lVar6 >> 3) * -0x55555555) {
                do {
                  uVar7 = uStack_500;
                    /* try { // try from 00027dbd to 00027dc1 has its CatchHandler @ 0002849f */
                  FUN_00026c80(&local_2d8,param_2,local_428,uVar15,&local_434,local_48c[0],1);
                  if (local_198 != '\0') {
                    uVar8 = local_2c8._0_8_;
                    if (local_1b4 != '\0') {
                      iVar12 = *(int *)((long)&local_2b0 + (long)local_48c[0] * 0xc + 4) + -1;
                      if (iVar12 < 0) {
                        iVar12 = 0;
                      }
                      iVar13 = *(int *)((long)&local_2b0 + (long)local_48c[0] * 0xc) + -2;
                      if (iVar13 < 0) {
                        iVar13 = 0;
                      }
                      dVar18 = (double)local_1b8 -
                               ((double)iVar12 * DAT_000e2de0 + (double)iVar13) * *param_2;
                      if (dVar18 < local_480) {
                        local_168 = local_2b8;
                        local_188 = local_2d8;
                        local_160 = local_2b0;
                        uStack_158 = uStack_2a8;
                        local_180 = local_2d0;
                        local_150 = local_2a0;
                        uStack_148 = uStack_298;
                        local_f0 = local_240;
                        local_140 = local_290;
                        uStack_138 = uStack_288;
                        local_e8 = local_238;
                        local_130 = local_280;
                        uStack_128 = uStack_278;
                        local_e0 = local_230;
                        local_110 = local_260;
                        uStack_108 = uStack_258;
                        local_100 = local_250;
                        uStack_f8 = uStack_248;
                        local_dc = local_22c;
                        uStack_d4 = uStack_224;
                        local_2b8 = 0;
                        local_178 = local_2c8;
                        local_2c8 = (undefined  [16])0x0;
                        local_120 = local_270;
                        uStack_118 = uStack_268;
                        local_68 = local_1b8;
                        local_bc = local_20c;
                        local_cc = local_21c;
                        uStack_c4 = uStack_214;
                        local_90 = local_1e0;
                        local_b0 = local_200;
                        uStack_a8 = uStack_1f8;
                        local_64 = 1;
                        local_50 = local_1a0;
                        local_1a0 = 0;
                        local_a0 = local_1f0;
                        uStack_98 = uStack_1e8;
                        local_88 = local_1d8;
                        uStack_80 = uStack_1d0;
                        local_78 = local_1c8;
                        uStack_70 = uStack_1c0;
                        local_60 = local_1b0;
                        local_1b0 = (undefined  [16])0x0;
                        local_480 = dVar18;
                        local_48 = uVar15;
                        if (*(char *)(param_1 + 0x29) == '\0') {
                          FUN_0001c620(param_1,&local_188);
                          *(uint *)(param_1 + 0x28) = uVar15;
                          *(undefined *)(param_1 + 0x29) = 1;
                        }
                        else {
                          FUN_00018bf0();
                          *(uint *)(param_1 + 0x28) = local_48;
                        }
                        FUN_0001cf40(local_60);
                        FUN_0001cb50(local_178);
                        local_198 = '\0';
                        uStack_500 = 0x28037;
                        FUN_0001cf40(local_1b0);
                        goto LAB_00027d71;
                      }
                    }
                    local_198 = '\0';
                    lVar14 = local_2b8 - local_2c8._0_8_;
                    uStack_500 = 0x27d5d;
                    FUN_0001cf40(local_1b0,lVar14,uVar7);
                    if (uVar8 != 0) {
                      uStack_500 = 0x27d71;
                      thunk_FUN_000d36e0(uVar8,lVar14);
                    }
                  }
LAB_00027d71:
                  uVar15 = uVar15 + 1;
                } while ((int)uVar15 <
                         (int)(*(long *)(param_3 + 0x18) - *(long *)(param_3 + 0x10) >> 3) *
                         -0x55555555);
              }
              local_2e8 = '\0';
              FUN_0001cf40(&local_300);
              uStack_500 = 0x2844f;
              FUN_0001cb50(local_418);
              lVar14 = *(long *)(param_3 + 0x18);
            }
            iVar2 = iVar2 + 1;
          } while (iVar2 < (int)(lVar14 - *(long *)(param_3 + 0x10) >> 3) * -0x55555555);
        }
        local_4e8 = (undefined8 *)((long)local_4e8 + -4);
        local_4d8 = local_4d8 + 1;
      } while ((undefined8 *)(local_440 + 4) != local_4e8);
    }
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


