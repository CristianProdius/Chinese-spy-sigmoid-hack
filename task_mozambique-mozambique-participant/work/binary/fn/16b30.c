// ===== FUNC 16b30 size=2718

undefined8 FUN_00016b30(void)

{
  byte bVar1;
  long lVar2;
  bool bVar3;
  undefined uVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  long *plVar9;
  char *pcVar10;
  undefined8 uVar11;
  byte *pbVar12;
  code ***pppcVar13;
  long lVar15;
  long lVar16;
  long lVar17;
  long in_FS_OFFSET;
  long local_1d8;
  char local_1a2;
  undefined local_1a1;
  ulong local_1a0;
  char local_198 [8];
  long local_190;
  ulong local_188;
  undefined8 local_180;
  undefined local_178 [16];
  long local_168;
  undefined *local_158;
  ulong local_150;
  undefined local_148 [16];
  undefined *local_138;
  undefined8 local_130;
  undefined local_128 [16];
  undefined local_118 [8];
  long *local_110;
  undefined8 local_108;
  undefined local_100;
  undefined8 local_f8;
  undefined8 local_f0;
  undefined local_e8 [8];
  long *local_e0;
  undefined8 local_d8;
  undefined local_d0;
  undefined8 local_c8;
  undefined8 local_c0;
  undefined local_b8 [8];
  long *local_b0;
  undefined8 local_a8;
  undefined local_a0;
  undefined8 local_98;
  undefined8 local_90;
  code **local_88;
  char *pcStack_80;
  code *local_78;
  code *apcStack_70 [2];
  undefined8 local_60;
  undefined local_58 [16];
  undefined8 local_48;
  code **local_40 [2];
  code ***pppcVar14;
  
  local_40[0] = *(code ***)(in_FS_OFFSET + 0x28);
  local_1d8 = 0;
  do {
    local_148[0] = 0;
    bVar3 = false;
    local_150 = 0;
    local_158 = local_148;
                    /* try { // try from 00016bf9 to 00016bfd has its CatchHandler @ 00017604 */
    while ((plVar9 = (long *)FUN_00090640(&DAT_00124220,&local_1a2),
           (*(byte *)((long)plVar9 + *(long *)(*plVar9 + -0x18) + 0x20) & 5) == 0 &&
           (local_1a2 != '\n'))) {
      if (local_150 < 0x8000) {
                    /* try { // try from 00016f58 to 00016f5c has its CatchHandler @ 00017604 */
        FUN_000b1530(&local_158,(int)local_1a2);
      }
      else {
        bVar3 = true;
      }
    }
    if (((DAT_00124250 & 5) != 0) && (local_150 == 0)) {
      if (!bVar3) {
LAB_00016f07:
        FUN_000b07c0(&local_158);
        if (local_1d8 != 0) {
          FUN_00018de0(local_1d8);
        }
        if (local_40[0] == *(code ***)(in_FS_OFFSET + 0x28)) {
          return 0;
        }
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
LAB_00014534:
      uVar11 = FUN_00040f40(0x10);
      FUN_00053220(uVar11,"request too large");
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(uVar11,&PTR_PTR_FUN_0011d470,FUN_00049930);
    }
    if (bVar3) goto LAB_00014534;
    local_168 = 0;
    pcStack_80 = (char *)0x0;
    local_178 = (undefined  [16])0x0;
    local_78 = FUN_00017b60;
    apcStack_70[0] = FUN_00019d10;
    local_88 = (code **)local_178;
                    /* try { // try from 00016c99 to 00016c9d has its CatchHandler @ 0001768a */
    FUN_00038940(local_198,&local_158,&local_88,1,0);
    if (local_78 != (code *)0x0) {
      (*local_78)(&local_88,&local_88,3);
    }
    uVar11 = local_178._8_8_;
    for (lVar15 = local_178._0_8_; uVar11 != lVar15; lVar15 = lVar15 + 0x30) {
      lVar2 = *(long *)(lVar15 + 0x10);
      while (lVar2 != 0) {
        FUN_00018460(*(undefined8 *)(lVar2 + 0x18));
        lVar16 = *(long *)(lVar2 + 0x10);
        if (*(long *)(lVar2 + 0x20) != lVar2 + 0x30) {
          thunk_FUN_000d36e0(*(long *)(lVar2 + 0x20),*(long *)(lVar2 + 0x30) + 1);
        }
        thunk_FUN_000d36e0(lVar2,0x40);
        lVar2 = lVar16;
      }
    }
    if (local_178._0_8_ != 0) {
      thunk_FUN_000d36e0(local_178._0_8_,local_168 - local_178._0_8_);
    }
    if (local_198[0] != '\x01') {
      uVar11 = FUN_000142f8();
      return uVar11;
    }
    lVar15 = local_190 + 8;
    lVar2 = *(long *)(local_190 + 0x10);
    lVar16 = lVar15;
    if (*(long *)(local_190 + 0x10) == 0) {
code_r0x000142f8:
      uVar11 = FUN_00040f40(0x10);
      FUN_00053220(uVar11,"command required");
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(uVar11,&PTR_PTR_FUN_0011d470,FUN_00049930);
    }
    do {
      while( true ) {
        lVar17 = lVar2;
        iVar5 = FUN_000b31e0(lVar17 + 0x20,"command");
        plVar9 = (long *)(lVar17 + 0x18);
        if (-1 < iVar5) break;
        lVar2 = *plVar9;
        lVar17 = lVar16;
        if (*plVar9 == 0) goto LAB_00016d9b;
      }
      lVar2 = *(long *)(lVar17 + 0x10);
      lVar16 = lVar17;
    } while (*(long *)(lVar17 + 0x10) != 0);
LAB_00016d9b:
    if ((lVar15 == lVar17) || (iVar5 = FUN_000b31e0(lVar17 + 0x20,"command"), 0 < iVar5))
    goto code_r0x000142f8;
    local_88 = &local_78;
                    /* try { // try from 00016dd8 to 00016ddc has its CatchHandler @ 000175fa */
    FUN_00017bf0(&local_88,"command","");
                    /* try { // try from 00016de5 to 00016de9 has its CatchHandler @ 00017611 */
    pcVar10 = (char *)FUN_00026330(local_198,&local_88);
    if (local_88 != &local_78) {
      thunk_FUN_000d36e0(local_88,local_78 + 1);
    }
    if (*pcVar10 != '\x03') {
      uVar11 = FUN_000142f8();
      return uVar11;
    }
    local_88 = &local_78;
                    /* try { // try from 00016e2c to 00016e30 has its CatchHandler @ 000175fa */
    FUN_00017bf0(&local_88,"command","");
                    /* try { // try from 00016e39 to 00016e3d has its CatchHandler @ 000175ef */
    pcVar10 = (char *)FUN_00026330(local_198,&local_88);
    if (local_88 != &local_78) {
      thunk_FUN_000d36e0(local_88,local_78 + 1);
    }
    local_128[0] = 0;
    local_138 = local_128;
    local_130 = 0;
    if (*pcVar10 != '\x03') {
      uVar11 = FUN_00014254();
      return uVar11;
    }
                    /* try { // try from 00016e9c to 00016ea0 has its CatchHandler @ 000175e5 */
    FUN_000b0ad0(&local_138,*(undefined8 *)(pcVar10 + 8));
    local_188 = 0;
    local_180 = 0;
    iVar5 = FUN_000b31e0(&local_138,&DAT_000e013c);
    if (iVar5 == 0) {
      local_88 = (code **)0xe01a8;
                    /* try { // try from 00016edf to 00016ee3 has its CatchHandler @ 000175e0 */
      FUN_00017f10(local_198,&local_88,1);
      FUN_00024620(&local_180,0);
      FUN_000b07c0(&local_138);
      FUN_00024620(&local_190,local_198[0]);
      goto LAB_00016f07;
    }
    iVar5 = FUN_000b31e0(&local_138,"hello");
    if (iVar5 == 0) {
      local_88 = (code **)0xe01a8;
                    /* try { // try from 00017285 to 00017289 has its CatchHandler @ 000175e0 */
      FUN_00017f10(local_198,&local_88,1);
      local_118[0] = 0;
      local_110 = (long *)0x0;
                    /* try { // try from 000172ae to 000172c4 has its CatchHandler @ 00017627 */
      FUN_00024620(&local_110,0);
      local_118[0] = 3;
      plVar9 = (long *)FUN_00041fe0(0x20);
      *plVar9 = (long)(plVar9 + 2);
                    /* try { // try from 000172de to 000172e2 has its CatchHandler @ 00017653 */
      FUN_00017bf0(plVar9,"protocol");
      local_108 = 0;
      local_100 = 5;
      local_f8 = 5;
      local_f0 = 0;
      local_110 = plVar9;
                    /* try { // try from 00017330 to 00017334 has its CatchHandler @ 0001763d */
      FUN_0002fd20(&local_88,local_118,2,1,2);
      local_78 = (code *)0x0;
      local_e8[0] = 0;
      local_e0 = (long *)0x0;
                    /* try { // try from 00017364 to 0001737a has its CatchHandler @ 00017648 */
      FUN_00024620(&local_e0,0);
      local_e8[0] = 3;
      plVar9 = (long *)FUN_00041fe0(0x20);
      *plVar9 = (long)(plVar9 + 2);
                    /* try { // try from 00017394 to 00017398 has its CatchHandler @ 00017632 */
      FUN_00017bf0(plVar9,"rounds");
      local_d8 = 0;
      local_d0 = 5;
      local_c8 = 0x50;
      local_c0 = 0;
      local_e0 = plVar9;
                    /* try { // try from 000173eb to 000173ef has its CatchHandler @ 0001767f */
      FUN_0002fd20(apcStack_70,local_e8,2);
      local_60 = 0;
      local_b8[0] = 0;
      local_b0 = (long *)0x0;
                    /* try { // try from 0001741a to 00017430 has its CatchHandler @ 00017674 */
      FUN_00024620(&local_b0,0);
      local_b8[0] = 3;
      plVar9 = (long *)FUN_00041fe0(0x20);
      *plVar9 = (long)(plVar9 + 2);
      local_178._8_8_ = plVar9;
      local_178._0_8_ = &local_1a1;
                    /* try { // try from 00017460 to 00017464 has its CatchHandler @ 00017669 */
      FUN_00017bf0(plVar9);
      local_a8 = 0;
      local_90 = 0;
      local_a0 = 6;
      local_98 = 5;
      local_b0 = plVar9;
                    /* try { // try from 000174b5 to 000174b9 has its CatchHandler @ 0001765e */
      FUN_0002fd20(local_58,local_b8,2,1,2);
      local_48 = 0;
                    /* try { // try from 000174dc to 000174e0 has its CatchHandler @ 00017695 */
      FUN_0002fd20(local_178,&local_88,3,1);
      uVar11 = local_180;
      uVar4 = local_178[0];
      local_178._0_8_ = local_178._1_8_ << 8;
      local_188 = CONCAT71(local_188._1_7_,uVar4);
      local_180 = local_178._8_8_;
      local_178._8_8_ = uVar11;
      FUN_00024620(local_178 + 8,0);
      pppcVar13 = local_40;
      do {
        pppcVar14 = pppcVar13 + -3;
        FUN_00024620(pppcVar13 + -2,*(undefined *)pppcVar14);
        pppcVar13 = pppcVar14;
      } while (pppcVar14 != &local_88);
      FUN_00024620(&local_98,local_a0);
      FUN_00024620(&local_b0,local_b8[0]);
      FUN_00024620(&local_c8,local_d0);
      FUN_00024620(&local_e0,local_e8[0]);
      FUN_00024620(&local_f8,local_100);
      FUN_00024620(&local_110,local_118[0]);
    }
    else {
      iVar5 = FUN_000b31e0(&local_138,"reset");
      if (iVar5 == 0) {
        local_88 = (code **)0xe01a8;
        pcStack_80 = PTR_s_group_0011bb90;
        local_78 = (code *)0xe5bd2;
        apcStack_70[0] = (code *)PTR_DAT_0011bb98;
                    /* try { // try from 00016fdd to 00017083 has its CatchHandler @ 000175e0 */
        FUN_00017f10(local_198,&local_88,4);
        uVar11 = FUN_000266c0(local_198,"group");
        uVar6 = FUN_0001a590(uVar11);
        uVar11 = FUN_000266c0(local_198,"seed");
        uVar7 = FUN_0001a590(uVar11);
        pbVar12 = (byte *)FUN_000266c0(local_198,&DAT_000e016b);
        if (*pbVar12 != 6) {
LAB_00014179:
          uVar11 = FUN_00040f40(0x10);
          FUN_00053220(uVar11,"game must be 0-4");
                    /* WARNING: Subroutine does not return */
          FUN_00041f00(uVar11,&PTR_PTR_FUN_0011d470,FUN_00049930);
        }
        local_1a0 = 0;
        FUN_0002ce30(pbVar12,&local_1a0);
        if (4 < local_1a0) goto LAB_00014179;
        bVar1 = *pbVar12;
        if (bVar1 == 6) {
LAB_0001718c:
          uVar8 = *(uint *)(pbVar12 + 8);
        }
        else if (bVar1 < 7) {
          if (bVar1 != 4) {
            if (bVar1 != 5) {
              uVar11 = FUN_00014566();
              return uVar11;
            }
            goto LAB_0001718c;
          }
          uVar8 = (uint)pbVar12[8];
        }
        else {
          if (bVar1 != 7) {
            uVar11 = FUN_00014566();
            return uVar11;
          }
          uVar8 = (uint)*(double *)(pbVar12 + 8);
        }
        if (7 < uVar6) {
          uVar11 = FUN_000141ab();
          return uVar11;
        }
        lVar15 = FUN_00041fe0(0xf00);
                    /* try { // try from 00017093 to 00017097 has its CatchHandler @ 000175d0 */
        FUN_0001fed0(lVar15,uVar6,uVar7,uVar8);
        if (local_1d8 != 0) {
          FUN_00018de0(local_1d8);
        }
                    /* try { // try from 000170b2 to 000170b6 has its CatchHandler @ 000175c5 */
        FUN_0003fdf0(local_178,lVar15);
        uVar11 = local_180;
        uVar4 = local_178[0];
        local_178._0_8_ = local_178._1_8_ << 8;
        local_188 = CONCAT71(local_188._1_7_,uVar4);
        local_180 = local_178._8_8_;
        local_178._8_8_ = uVar11;
        FUN_00024620(local_178 + 8,0);
        local_1d8 = lVar15;
      }
      else {
        iVar5 = FUN_000b31e0(&local_138,&DAT_000e018f);
        if (iVar5 != 0) {
          uVar11 = FUN_00040f40(0x10);
          FUN_00053220(uVar11,"unknown command");
                    /* WARNING: Subroutine does not return */
          FUN_00041f00(uVar11,&PTR_PTR_FUN_0011d470,FUN_00049930);
        }
        local_88 = (code **)0xe01a8;
        pcStack_80 = "action";
                    /* try { // try from 000171f3 to 0001722d has its CatchHandler @ 000175e0 */
        FUN_00017f10(local_198,&local_88,2);
        if (local_1d8 == 0) {
          uVar11 = FUN_00040f40(0x10);
          FUN_00053220(uVar11,"reset first");
                    /* WARNING: Subroutine does not return */
          FUN_00041f00(uVar11,&PTR_PTR_FUN_0011d470,FUN_00049930);
        }
        uVar11 = FUN_000266c0(local_198,"action");
        FUN_0003d0b0(local_1d8,uVar11);
        FUN_0003fdf0(local_178,local_1d8);
        uVar11 = local_180;
        uVar4 = local_178[0];
        local_178._0_8_ = local_178._1_8_ << 8;
        local_188 = CONCAT71(local_188._1_7_,uVar4);
        local_180 = local_178._8_8_;
        local_178._8_8_ = uVar11;
        FUN_00024620(local_178 + 8,0);
      }
    }
                    /* try { // try from 00017111 to 00017115 has its CatchHandler @ 000175e0 */
    FUN_0002e6f0(&local_88,&local_188,0xffffffff,0x20);
                    /* try { // try from 0001712d to 00017146 has its CatchHandler @ 0001761c */
    uVar11 = FUN_000aa620(&DAT_00124100,local_88,pcStack_80);
    uVar11 = FUN_000aaa60(uVar11,10);
    FUN_000a9b20(uVar11);
    FUN_000b07c0(&local_88);
    FUN_00024620(&local_180,local_188 & 0xff);
    FUN_000b07c0(&local_138);
    FUN_00024620(&local_190,local_198[0]);
    FUN_000b07c0(&local_158);
  } while( true );
}


