// ===== FUNC 29690 size=2170

long FUN_00029690(long param_1,long param_2,long param_3,int param_4)

{
  undefined8 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined auVar4 [16];
  undefined auVar5 [16];
  undefined8 uVar6;
  undefined8 uVar7;
  int iVar8;
  char cVar9;
  long lVar10;
  long lVar11;
  long *plVar12;
  undefined8 *puVar13;
  char cVar14;
  long lVar15;
  long in_FS_OFFSET;
  undefined *local_480;
  int local_46c;
  undefined8 local_468;
  undefined8 uStack_460;
  undefined8 local_458;
  undefined8 local_444;
  undefined4 local_43c;
  undefined local_438 [16];
  undefined local_428 [16];
  undefined local_418 [16];
  undefined8 local_408;
  undefined8 local_400;
  undefined8 uStack_3f8;
  undefined8 local_3f0;
  undefined8 uStack_3e8;
  undefined8 local_3e0;
  undefined8 uStack_3d8;
  undefined8 local_3d0;
  undefined8 uStack_3c8;
  undefined8 local_3c0;
  undefined8 uStack_3b8;
  undefined8 local_3b0;
  undefined8 uStack_3a8;
  undefined8 local_3a0;
  undefined8 local_398;
  undefined2 local_390;
  undefined8 local_38c;
  undefined8 uStack_384;
  undefined8 local_37c;
  undefined8 uStack_374;
  undefined8 local_36c;
  undefined8 local_360;
  undefined8 uStack_358;
  undefined8 local_350;
  undefined8 uStack_348;
  undefined8 local_340;
  undefined8 local_338;
  undefined8 uStack_330;
  undefined8 local_328;
  undefined8 uStack_320;
  int local_318;
  char local_314;
  undefined local_310 [16];
  undefined8 local_300;
  char local_2f8;
  undefined8 local_2e8;
  undefined4 local_2e0;
  long local_2d8;
  undefined8 uStack_2d0;
  long local_2c8;
  ulong local_2c0;
  undefined8 uStack_2b8;
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
  undefined8 local_248;
  undefined2 local_240;
  undefined8 local_23c;
  undefined8 uStack_234;
  undefined8 local_22c;
  undefined8 uStack_224;
  undefined8 local_21c;
  undefined8 local_210;
  undefined8 uStack_208;
  undefined8 local_200;
  undefined8 uStack_1f8;
  undefined8 local_1f0;
  undefined8 local_1e8;
  undefined8 uStack_1e0;
  undefined8 local_1d8;
  undefined8 uStack_1d0;
  int local_1c8;
  undefined8 local_1c0;
  undefined8 uStack_1b8;
  undefined8 local_1b0;
  int local_1a8;
  undefined local_1a0;
  undefined8 local_198;
  undefined4 local_190;
  undefined local_188 [16];
  long local_178;
  ulong local_170;
  undefined8 uStack_168;
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
  int local_78;
  char local_74;
  undefined local_70 [16];
  long local_60;
  int local_58;
  char local_50;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (*(int *)(param_3 + 0x100 + (long)param_4 * 4) != -1) {
    *(undefined *)(param_1 + 0x140) = 0;
    goto LAB_000296de;
  }
  puVar13 = &local_2e8;
  for (lVar11 = 0x2a; lVar11 != 0; lVar11 = lVar11 + -1) {
    *puVar13 = 0;
    puVar13 = puVar13 + 1;
  }
  lVar11 = param_2 + (long)param_4 * 0x14;
  if (*(int *)(lVar11 + 0x4f8) == 2) {
                    /* try { // try from 00029e53 to 00029e57 has its CatchHandler @ 00029f33 */
    FUN_000284f0(&local_198,param_2,param_3,*(undefined4 *)(lVar11 + 0x500));
    if (local_50 != '\0') {
      FUN_0001c620(&local_2e8,&local_198);
      uVar1 = local_70._8_8_;
      local_50 = '\0';
      local_1a0 = 1;
      local_1a8 = local_58;
      plVar12 = (long *)local_70._0_8_;
      if (local_70._8_8_ != local_70._0_8_) {
        do {
          if ((long *)*plVar12 != plVar12 + 2) {
            thunk_FUN_000d36e0((long *)*plVar12,plVar12[2] + 1);
          }
          plVar12 = plVar12 + 7;
        } while ((long *)uVar1 != plVar12);
      }
      if ((long *)local_70._0_8_ != (long *)0x0) {
        thunk_FUN_000d36e0(local_70._0_8_,local_60 - local_70._0_8_);
      }
      if (local_188._0_8_ != 0) {
        thunk_FUN_000d36e0(local_188._0_8_,local_178 - local_188._0_8_);
      }
LAB_00029d52:
      local_480 = local_438;
      FUN_0001c620(&local_198,&local_2e8);
      local_408 = 0;
      auVar5._8_8_ = 0;
      auVar5._0_8_ = DAT_000e2e80;
      local_418 = auVar5 << 0x20;
      local_438 = (undefined  [16])0x0;
      local_428 = (undefined  [16])0x0;
                    /* try { // try from 00029da4 to 00029da8 has its CatchHandler @ 00029f3d */
      FUN_00018b10(local_480,"deliver");
      local_418._0_4_ = local_1a8;
      local_408 = CONCAT44(local_408._4_4_,param_4);
                    /* try { // try from 00029dd3 to 00029dd7 has its CatchHandler @ 00029f38 */
      FUN_00019ec0(param_2,&local_198,local_480,1);
      FUN_000b07c0(local_480);
      if (local_74 == '\0') {
        *(undefined *)(param_1 + 0x140) = 0;
      }
      else {
        FUN_0001c620(param_1,&local_198);
        *(undefined *)(param_1 + 0x140) = 1;
      }
      FUN_0001cf40(local_70);
      FUN_0001cb50(local_188);
      local_1a0 = 0;
      FUN_0001cf40(&local_1c0);
      FUN_0001cb50(&local_2d8);
      goto LAB_000296de;
    }
  }
  else {
    local_444 = 0;
    local_43c = 0;
    *(undefined4 *)((long)&local_444 + (long)*(int *)(lVar11 + 0x4f8) * 4) =
         *(undefined4 *)(lVar11 + 0x4fc);
    if (0 < (int)(*(long *)(param_3 + 0x18) - *(long *)(param_3 + 0x10) >> 3) * -0x55555555) {
      cVar14 = '\0';
      local_46c = 0;
      do {
                    /* try { // try from 000297e3 to 000297e7 has its CatchHandler @ 00029f33 */
        FUN_00026c80(local_438,param_2,param_3,local_46c,&local_444,*(undefined4 *)(lVar11 + 0x500),
                     0);
        lVar10 = local_2c8;
        lVar15 = local_2d8;
        cVar9 = local_2f8;
        uVar1 = local_300;
        iVar8 = local_318;
        if (local_2f8 != '\0') {
          uVar6 = local_428._0_8_;
          uVar7 = local_418._0_8_;
          if ((cVar14 == '\0') || (local_318 < local_1c8)) {
            local_170 = local_418._8_8_;
            auVar4._8_8_ = 0;
            auVar4._0_8_ = local_418._8_8_;
            local_418 = auVar4 << 0x40;
            local_198 = local_438._0_8_;
            local_190 = local_438._8_4_;
            local_100 = local_3a0;
            local_f8 = local_398;
            uStack_168 = local_408;
            local_f0 = local_390;
            local_160 = local_400;
            uStack_158 = uStack_3f8;
            local_2d8 = local_428._0_8_;
            uStack_2d0 = local_428._8_8_;
            local_150 = local_3f0;
            uStack_148 = uStack_3e8;
            local_428 = (undefined  [16])0x0;
            local_140 = local_3e0;
            uStack_138 = uStack_3d8;
            local_130 = local_3d0;
            uStack_128 = uStack_3c8;
            local_120 = local_3c0;
            uStack_118 = uStack_3b8;
            local_110 = local_3b0;
            uStack_108 = uStack_3a8;
            local_ec = local_38c;
            uStack_e4 = uStack_384;
            local_dc = local_37c;
            uStack_d4 = uStack_374;
            uVar2 = local_310._0_8_;
            uVar3 = local_310._8_8_;
            local_78 = local_318;
            local_a0 = local_340;
            local_cc = local_36c;
            local_300 = 0;
            local_60 = uVar1;
            local_74 = local_314;
            local_58 = local_46c;
            local_2e8 = local_438._0_8_;
            local_2e0 = local_438._8_4_;
            local_c0 = local_360;
            uStack_b8 = uStack_358;
            local_b0 = local_350;
            uStack_a8 = uStack_348;
            local_98 = local_338;
            uStack_90 = uStack_330;
            local_88 = local_328;
            uStack_80 = uStack_320;
            local_70 = local_310;
            local_310 = (undefined  [16])0x0;
            if (cVar14 == '\0') {
              local_2c8 = uVar7;
              local_1f0 = local_340;
              local_178 = 0;
              local_60 = 0;
              local_188 = (undefined  [16])0x0;
              local_70 = (undefined  [16])0x0;
              local_1a0 = 1;
              local_2c0 = local_170;
              uStack_2b8 = local_408;
              local_2b0 = local_400;
              uStack_2a8 = uStack_3f8;
              local_2a0 = local_3f0;
              uStack_298 = uStack_3e8;
              local_290 = local_3e0;
              uStack_288 = uStack_3d8;
              local_280 = local_3d0;
              uStack_278 = uStack_3c8;
              local_270 = local_3c0;
              uStack_268 = uStack_3b8;
              local_260 = local_3b0;
              uStack_258 = uStack_3a8;
              local_250 = local_3a0;
              local_248 = local_398;
              local_240 = local_390;
              local_23c = local_38c;
              uStack_234 = uStack_384;
              local_22c = local_37c;
              uStack_224 = uStack_374;
              local_21c = local_36c;
              local_210 = local_360;
              uStack_208 = uStack_358;
              local_200 = local_350;
              uStack_1f8 = uStack_348;
              local_1e8 = local_338;
              uStack_1e0 = uStack_330;
              local_1d8 = local_328;
              uStack_1d0 = uStack_320;
              local_1c8 = local_318;
              local_1c0 = uVar2;
              uStack_1b8 = uVar3;
              local_1b0 = uVar1;
            }
            else {
              local_178 = 0;
              local_2d8 = uVar6;
              local_2c8 = uVar7;
              local_188 = (undefined  [16])0x0;
              if (lVar15 != 0) {
                thunk_FUN_000d36e0(lVar15,lVar10 - lVar15);
              }
              local_458 = local_1b0;
              local_250 = local_100;
              local_2c0 = local_170;
              uStack_2b8 = uStack_168;
              local_248 = local_f8;
              local_2b0 = local_160;
              uStack_2a8 = uStack_158;
              local_240 = local_f0;
              local_2a0 = local_150;
              uStack_298 = uStack_148;
              local_21c = local_cc;
              local_290 = local_140;
              uStack_288 = uStack_138;
              local_280 = local_130;
              uStack_278 = uStack_128;
              local_1f0 = local_a0;
              local_260 = local_110;
              uStack_258 = uStack_108;
              local_23c = local_ec;
              uStack_234 = uStack_e4;
              local_22c = local_dc;
              uStack_224 = uStack_d4;
              local_210 = local_c0;
              uStack_208 = uStack_b8;
              local_200 = local_b0;
              uStack_1f8 = uStack_a8;
              local_270 = local_120;
              uStack_268 = uStack_118;
              local_60 = 0;
              local_468 = local_1c0;
              uStack_460 = uStack_1b8;
              local_70 = (undefined  [16])0x0;
              local_1b0 = uVar1;
              local_1c8 = iVar8;
              local_1e8 = local_98;
              uStack_1e0 = uStack_90;
              local_1d8 = local_88;
              uStack_1d0 = uStack_80;
              local_1c0 = uVar2;
              uStack_1b8 = uVar3;
              FUN_0001cf40(&local_468);
            }
            local_1a8 = local_46c;
            FUN_0001cf40(local_70);
            local_2f8 = '\0';
            FUN_0001cf40(local_310);
            cVar14 = cVar9;
          }
          else {
            local_2f8 = '\0';
            lVar15 = local_418._0_8_ - local_428._0_8_;
            FUN_0001cf40(local_310);
            cVar14 = cVar9;
            if (uVar6 != 0) {
              thunk_FUN_000d36e0(uVar6,lVar15);
            }
          }
        }
        local_46c = local_46c + 1;
      } while (local_46c <
               (int)(*(long *)(param_3 + 0x18) - *(long *)(param_3 + 0x10) >> 3) * -0x55555555);
      if (cVar14 != '\0') goto LAB_00029d52;
    }
  }
  *(undefined *)(param_1 + 0x140) = 0;
LAB_000296de:
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


