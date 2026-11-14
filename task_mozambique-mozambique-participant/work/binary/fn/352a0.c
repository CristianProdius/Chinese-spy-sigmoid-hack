// ===== FUNC 352a0 size=5800

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_000352a0(long param_1,undefined8 *param_2)

{
  undefined uVar1;
  undefined uVar2;
  ulong uVar3;
  char cVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  ulong uVar9;
  long lVar10;
  long *plVar11;
  char *pcVar12;
  long lVar13;
  ulong *puVar14;
  ulong *puVar15;
  bool bVar16;
  long **unaff_R12;
  undefined *puVar17;
  undefined *unaff_R15;
  undefined *puVar18;
  long in_FS_OFFSET;
  undefined auVar19 [16];
  long local_160;
  undefined ***local_158;
  undefined *local_150;
  undefined local_144;
  undefined local_143;
  undefined local_142;
  undefined local_141;
  undefined local_140;
  undefined local_13f;
  undefined local_13e;
  undefined local_13d;
  undefined4 local_13c;
  undefined4 local_138;
  undefined4 local_134;
  undefined4 local_130;
  undefined4 local_12c;
  ulong local_128;
  long *plStack_120;
  undefined4 *local_118;
  long *plStack_110;
  undefined8 local_108;
  undefined *local_f8;
  undefined8 local_f0;
  undefined *local_e8;
  ulong local_e0;
  long local_d8;
  undefined local_c8 [32];
  undefined local_a8 [32];
  ulong local_88 [4];
  undefined **local_68 [5];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  local_f8 = (undefined *)0x0;
  local_f0 = 0;
  local_e8 = (undefined *)0x0;
  local_e0 = 0;
  local_d8 = 0;
  do {
    switch(*(undefined4 *)(param_1 + 0x20)) {
    default:
                    /* try { // try from 00035332 to 00035336 has its CatchHandler @ 000369a6 */
      FUN_00018b10(local_a8,"value");
                    /* try { // try from 0003534d to 00035351 has its CatchHandler @ 000369a4 */
      FUN_000234b0(local_88,param_1,0x10,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined4 **)(param_1 + 0x48);
      plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 00035382 to 00035386 has its CatchHandler @ 000369a2 */
      FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00035398 to 0003539c has its CatchHandler @ 0003699e */
      FUN_00023340(local_c8,param_1 + 0x28);
      unaff_R12 = (long **)(ulong)*(byte *)(param_2 + 0x14);
      *(undefined *)(param_2 + 0xf) = 1;
      if (*(byte *)(param_2 + 0x14) == 0) {
LAB_000353b2:
        local_150 = local_c8;
        FUN_000b07c0(local_150);
        local_68[0] = &PTR_FUN_0011ba98;
LAB_000353c3:
        local_158 = local_68;
        FUN_0001a6b0(local_158);
        FUN_000b07c0(local_88);
        FUN_000b07c0(local_a8);
        puVar18 = local_f8;
LAB_000353ea:
        if (puVar18 != (undefined *)0x0) {
          thunk_FUN_000d36e0(puVar18,local_d8 - (long)puVar18);
        }
        if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
          return (ulong)unaff_R12 & 0xffffffff;
        }
LAB_000368e0:
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
                    /* try { // try from 00036999 to 0003699d has its CatchHandler @ 000369a0 */
      param_1 = FUN_00013710(local_68);
                    /* catch() { ... } // from try @ 00035398 with catch @ 0003699e */
LAB_00036945:
                    /* catch() { ... } // from try @ 00036137 with catch @ 00036945 */
      local_158 = local_68;
      local_68[0] = &PTR_FUN_0011ba98;
      FUN_0001a6b0(local_158);
LAB_00036970:
      FUN_000b07c0(local_88);
      FUN_000b07c0(local_a8);
LAB_0003691a:
      FUN_00025b20(&local_f8);
                    /* WARNING: Subroutine does not return */
      FUN_000ddde0(param_1);
    case 1:
      local_143 = 1;
                    /* try { // try from 0003543f to 00035583 has its CatchHandler @ 000369a6 */
      FUN_00024c70(param_2,&local_143,0);
      break;
    case 2:
      local_144 = 0;
      FUN_00024c70(param_2,&local_144,0);
      break;
    case 3:
      lVar13 = (ulong)*(uint *)(param_2 + 7) - 1;
      lVar10 = (ulong)*(uint *)(param_2 + 7) + 0x3e;
      if (-1 < lVar13) {
        lVar10 = lVar13;
      }
      puVar15 = (ulong *)(param_2[6] + (lVar10 >> 6) * 8);
      if (lVar13 % 0x40 == -1) {
        uVar9 = 0x8000000000000000;
        puVar15 = puVar15 + -1;
      }
      else {
        uVar9 = 1L << ((byte)(lVar13 % 0x40) & 0x3f);
      }
      if ((uVar9 & *puVar15) == 0) break;
      local_141 = 5;
      local_128 = 0;
      plStack_120 = (long *)0x0;
      local_138 = (undefined4)((long)(param_2[2] - param_2[1]) >> 3);
      if (param_2[0x12] != 0) {
                    /* try { // try from 00035624 to 00035629 has its CatchHandler @ 000369b6 */
        cVar4 = (*(code *)param_2[0x13])(param_2 + 0x10,&local_138,&local_141,&local_128);
        plVar11 = plStack_120;
        uVar9 = local_128;
        if (cVar4 != '\0') {
          if (param_2[2] == param_2[1]) {
            uVar2 = (undefined)local_128;
            local_128 = local_128 & 0xffffffffffffff00;
            plStack_120 = (long *)0x0;
            puVar17 = (undefined *)*param_2;
            uVar1 = *puVar17;
            *puVar17 = uVar2;
            plStack_110 = *(long **)(puVar17 + 8);
            *(long **)(puVar17 + 8) = plVar11;
            local_118._1_7_ = (undefined7)(uVar9 >> 8);
            local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
            FUN_00024620(&plStack_110);
          }
          else {
            pcVar12 = *(char **)(param_2[2] + -8);
            if (pcVar12 != (char *)0x0) {
              if (*pcVar12 == '\x02') {
                    /* try { // try from 00036549 to 0003654d has its CatchHandler @ 000369b6 */
                FUN_000182f0(*(undefined8 *)(pcVar12 + 8),&local_128);
              }
              else {
                lVar10 = param_2[0xb];
                iVar7 = *(int *)(param_2 + 0xc);
                auVar19 = FUN_00017eb0(lVar10,iVar7);
                plVar11 = plStack_120;
                uVar3 = local_128;
                uVar9 = *auVar19._0_8_;
                if (iVar7 == 0) {
                  *(undefined4 *)(param_2 + 0xc) = 0x3f;
                  param_2[0xb] = lVar10 + -8;
                }
                else {
                  *(int *)(param_2 + 0xc) = iVar7 + -1;
                }
                if ((auVar19._8_8_ & uVar9) != 0) {
                  uVar2 = (undefined)local_128;
                  local_128 = local_128 & 0xffffffffffffff00;
                  plStack_120 = (long *)0x0;
                  puVar17 = (undefined *)param_2[0xe];
                  uVar1 = *puVar17;
                  *puVar17 = uVar2;
                  plStack_110 = *(long **)(puVar17 + 8);
                  *(long **)(puVar17 + 8) = plVar11;
                  local_118._1_7_ = (undefined7)(uVar3 >> 8);
                  local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
                  FUN_00024620(&plStack_110);
                }
              }
            }
          }
        }
        FUN_00024620(&plStack_120,local_128 & 0xff);
        break;
      }
LAB_000368ea:
                    /* try { // try from 000368ea to 000368ee has its CatchHandler @ 000369b6 */
      FUN_00016056();
LAB_000368ef:
                    /* try { // try from 000368ef to 000368f3 has its CatchHandler @ 00036a0c */
      FUN_00016056();
      goto LAB_000368f4;
    case 4:
      if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
        *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
      }
      lVar13 = (ulong)*(uint *)(param_2 + 7) - 1;
      lVar10 = (ulong)*(uint *)(param_2 + 7) + 0x3e;
      if (-1 < lVar13) {
        lVar10 = lVar13;
      }
      puVar15 = (ulong *)(param_2[6] + (lVar10 >> 6) * 8);
      if (lVar13 % 0x40 == -1) {
        uVar9 = 0x8000000000000000;
        puVar15 = puVar15 + -1;
      }
      else {
        uVar9 = 1L << ((byte)(lVar13 % 0x40) & 0x3f);
      }
      if ((uVar9 & *puVar15) == 0) break;
      local_128 = 0;
      unaff_R12 = &plStack_120;
      plStack_120 = (long *)0x0;
                    /* try { // try from 00035718 to 0003572b has its CatchHandler @ 00036908 */
      FUN_00024620(unaff_R12,0);
      local_128 = CONCAT71(local_128._1_7_,3);
      plVar11 = (long *)FUN_00041fe0(0x20);
      local_118 = &local_12c;
      lVar10 = *(long *)(param_1 + 0x78);
      lVar13 = *(long *)(param_1 + 0x80);
      *plVar11 = (long)(plVar11 + 2);
      plStack_110 = plVar11;
                    /* try { // try from 00035757 to 0003575b has its CatchHandler @ 00036903 */
      FUN_00017e00(plVar11,lVar10,lVar13 + lVar10);
      local_13f = 5;
      local_130 = (undefined4)((long)(param_2[2] - param_2[1]) >> 3);
      plStack_120 = plVar11;
      if (param_2[0x12] != 0) {
                    /* try { // try from 0003579d to 000357a2 has its CatchHandler @ 000368fe */
        cVar4 = (*(code *)param_2[0x13])(param_2 + 0x10,&local_130,&local_13f,&local_128);
        plVar11 = plStack_120;
        uVar9 = local_128;
        if (cVar4 != '\0') {
          if (param_2[2] == param_2[1]) {
            uVar2 = (undefined)local_128;
            local_128 = local_128 & 0xffffffffffffff00;
            plStack_120 = (long *)0x0;
            puVar17 = (undefined *)*param_2;
            uVar1 = *puVar17;
            *puVar17 = uVar2;
            plStack_110 = *(long **)(puVar17 + 8);
            *(long **)(puVar17 + 8) = plVar11;
            local_118._1_7_ = (undefined7)(uVar9 >> 8);
            local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
            FUN_00024620(&plStack_110);
          }
          else {
            pcVar12 = *(char **)(param_2[2] + -8);
            if (pcVar12 != (char *)0x0) {
              if (*pcVar12 == '\x02') {
                    /* try { // try from 00036644 to 00036648 has its CatchHandler @ 000368fe */
                FUN_000182f0(*(undefined8 *)(pcVar12 + 8),&local_128);
              }
              else {
                lVar10 = param_2[0xb];
                iVar7 = *(int *)(param_2 + 0xc);
                auVar19 = FUN_00017eb0(lVar10,iVar7);
                plVar11 = plStack_120;
                uVar3 = local_128;
                uVar9 = *auVar19._0_8_;
                if (iVar7 == 0) {
                  *(undefined4 *)(param_2 + 0xc) = 0x3f;
                  param_2[0xb] = lVar10 + -8;
                }
                else {
                  *(int *)(param_2 + 0xc) = iVar7 + -1;
                }
                if ((auVar19._8_8_ & uVar9) != 0) {
                  uVar2 = (undefined)local_128;
                  local_128 = local_128 & 0xffffffffffffff00;
                  plStack_120 = (long *)0x0;
                  puVar17 = (undefined *)param_2[0xe];
                  uVar1 = *puVar17;
                  *puVar17 = uVar2;
                  plStack_110 = *(long **)(puVar17 + 8);
                  *(long **)(puVar17 + 8) = plVar11;
                  local_118._1_7_ = (undefined7)(uVar3 >> 8);
                  local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
                  FUN_00024620(&plStack_110);
                }
              }
            }
          }
        }
        FUN_00024620(unaff_R12,local_128 & 0xff);
        break;
      }
      goto LAB_000368f9;
    case 5:
      lVar13 = (ulong)*(uint *)(param_2 + 7) - 1;
      lVar10 = (ulong)*(uint *)(param_2 + 7) + 0x3e;
      if (-1 < lVar13) {
        lVar10 = lVar13;
      }
      puVar15 = (ulong *)(param_2[6] + (lVar10 >> 6) * 8);
      if (lVar13 % 0x40 == -1) {
        uVar9 = 0x8000000000000000;
        puVar15 = puVar15 + -1;
      }
      else {
        uVar9 = 1L << ((byte)(lVar13 % 0x40) & 0x3f);
      }
      if ((uVar9 & *puVar15) != 0) {
        local_128 = CONCAT71(local_128._1_7_,6);
        local_12c = (undefined4)((long)(param_2[2] - param_2[1]) >> 3);
        local_13e = 5;
        plStack_120 = *(long **)(param_1 + 0xa8);
        if (param_2[0x12] == 0) goto LAB_000368ef;
                    /* try { // try from 000358ab to 000358b0 has its CatchHandler @ 00036a0c */
        cVar4 = (*(code *)param_2[0x13])(param_2 + 0x10,&local_12c,&local_13e,&local_128);
        plVar11 = plStack_120;
        uVar9 = local_128;
        if (cVar4 != '\0') {
          if (param_2[2] == param_2[1]) {
            uVar2 = (undefined)local_128;
            local_128 = local_128 & 0xffffffffffffff00;
            plStack_120 = (long *)0x0;
            puVar17 = (undefined *)*param_2;
            uVar1 = *puVar17;
            *puVar17 = uVar2;
            plStack_110 = *(long **)(puVar17 + 8);
            *(long **)(puVar17 + 8) = plVar11;
            local_118._1_7_ = (undefined7)(uVar9 >> 8);
            local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
            FUN_00024620(&plStack_110);
          }
          else {
            pcVar12 = *(char **)(param_2[2] + -8);
            if (pcVar12 != (char *)0x0) {
              if (*pcVar12 == '\x02') {
                    /* try { // try from 00036538 to 0003653c has its CatchHandler @ 00036a0c */
                FUN_000182f0(*(undefined8 *)(pcVar12 + 8),&local_128);
              }
              else {
                lVar10 = param_2[0xb];
                iVar7 = *(int *)(param_2 + 0xc);
                auVar19 = FUN_00017eb0(lVar10,iVar7);
                plVar11 = plStack_120;
                uVar3 = local_128;
                uVar9 = *auVar19._0_8_;
                if (iVar7 == 0) {
                  *(undefined4 *)(param_2 + 0xc) = 0x3f;
                  param_2[0xb] = lVar10 + -8;
                }
                else {
                  *(int *)(param_2 + 0xc) = iVar7 + -1;
                }
                if ((auVar19._8_8_ & uVar9) != 0) {
                  uVar2 = (undefined)local_128;
                  local_128 = local_128 & 0xffffffffffffff00;
                  plStack_120 = (long *)0x0;
                  puVar17 = (undefined *)param_2[0xe];
                  uVar1 = *puVar17;
                  *puVar17 = uVar2;
                  plStack_110 = *(long **)(puVar17 + 8);
                  *(long **)(puVar17 + 8) = plVar11;
                  local_118._1_7_ = (undefined7)(uVar3 >> 8);
                  local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
                  FUN_00024620(&plStack_110);
                }
              }
            }
          }
        }
        FUN_00024620(&plStack_120,local_128 & 0xff);
      }
      break;
    case 6:
      goto switchD_00035317_caseD_6;
    case 7:
      plVar11 = *(long **)(param_1 + 0xb0);
      if (DAT_000e2e40 < (double)((ulong)plVar11 & _DAT_000e2ea0)) {
        local_118 = (undefined4 *)CONCAT71(local_118._1_7_,0x27);
                    /* try { // try from 00036352 to 00036356 has its CatchHandler @ 000369a6 */
        FUN_00023340(local_a8,param_1 + 0x28);
                    /* try { // try from 00036371 to 00036375 has its CatchHandler @ 00036b05 */
        FUN_000243f0(local_88,"number overflow parsing \'",local_a8,&local_118);
                    /* try { // try from 0003638e to 00036392 has its CatchHandler @ 00036b00 */
        FUN_00018f90(local_68,0x196,local_88);
                    /* try { // try from 000363a6 to 000363aa has its CatchHandler @ 00036ad0 */
        FUN_00023340(local_c8,param_1 + 0x28);
        unaff_R12 = (long **)(ulong)*(byte *)(param_2 + 0x14);
        *(undefined *)(param_2 + 0xf) = 1;
        if (*(byte *)(param_2 + 0x14) == 0) {
          FUN_000b07c0(local_c8);
          local_68[0] = &PTR_FUN_0011bb10;
          goto LAB_000353c3;
        }
                    /* try { // try from 00036acb to 00036acf has its CatchHandler @ 00036ad5 */
        param_1 = FUN_00013768(local_68);
                    /* catch() { ... } // from try @ 000363a6 with catch @ 00036ad0 */
        local_68[0] = &PTR_FUN_0011bb10;
        FUN_0001a6b0(local_68);
        goto LAB_00036970;
      }
      if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
        *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
      }
      lVar13 = (ulong)*(uint *)(param_2 + 7) - 1;
      lVar10 = (ulong)*(uint *)(param_2 + 7) + 0x3e;
      if (-1 < lVar13) {
        lVar10 = lVar13;
      }
      puVar15 = (ulong *)(param_2[6] + (lVar10 >> 6) * 8);
      if (lVar13 % 0x40 == -1) {
        uVar9 = 0x8000000000000000;
        puVar15 = puVar15 + -1;
      }
      else {
        uVar9 = 1L << ((byte)(lVar13 % 0x40) & 0x3f);
      }
      if ((uVar9 & *puVar15) != 0) {
        local_128 = CONCAT71(local_128._1_7_,7);
        local_142 = 5;
        local_13c = (undefined4)((long)(param_2[2] - param_2[1]) >> 3);
        plStack_120 = plVar11;
        if (param_2[0x12] == 0) {
                    /* try { // try from 000368e5 to 000368e9 has its CatchHandler @ 000369bb */
          FUN_00016056();
          goto LAB_000368ea;
        }
                    /* try { // try from 00035c89 to 00035c8e has its CatchHandler @ 000369bb */
        cVar4 = (*(code *)param_2[0x13])(param_2 + 0x10,&local_13c,&local_142,&local_128);
        plVar11 = plStack_120;
        uVar9 = local_128;
        if (cVar4 != '\0') {
          if (param_2[2] == param_2[1]) {
            uVar2 = (undefined)local_128;
            local_128 = local_128 & 0xffffffffffffff00;
            plStack_120 = (long *)0x0;
            puVar17 = (undefined *)*param_2;
            uVar1 = *puVar17;
            *puVar17 = uVar2;
            plStack_110 = *(long **)(puVar17 + 8);
            *(long **)(puVar17 + 8) = plVar11;
            local_118._1_7_ = (undefined7)(uVar9 >> 8);
            local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
            FUN_00024620(&plStack_110);
          }
          else {
            pcVar12 = *(char **)(param_2[2] + -8);
            if (pcVar12 != (char *)0x0) {
              if (*pcVar12 == '\x02') {
                    /* try { // try from 000366b6 to 000366ba has its CatchHandler @ 000369bb */
                FUN_000182f0(*(undefined8 *)(pcVar12 + 8),&local_128);
              }
              else {
                lVar10 = param_2[0xb];
                iVar7 = *(int *)(param_2 + 0xc);
                auVar19 = FUN_00017eb0(lVar10,iVar7);
                plVar11 = plStack_120;
                uVar3 = local_128;
                uVar9 = *auVar19._0_8_;
                if (iVar7 == 0) {
                  *(undefined4 *)(param_2 + 0xc) = 0x3f;
                  param_2[0xb] = lVar10 + -8;
                }
                else {
                  *(int *)(param_2 + 0xc) = iVar7 + -1;
                }
                if ((auVar19._8_8_ & uVar9) != 0) {
                  uVar2 = (undefined)local_128;
                  local_128 = local_128 & 0xffffffffffffff00;
                  plStack_120 = (long *)0x0;
                  puVar17 = (undefined *)param_2[0xe];
                  uVar1 = *puVar17;
                  *puVar17 = uVar2;
                  plStack_110 = *(long **)(puVar17 + 8);
                  *(long **)(puVar17 + 8) = plVar11;
                  local_118._1_7_ = (undefined7)(uVar3 >> 8);
                  local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
                  FUN_00024620(&plStack_110);
                }
              }
            }
          }
        }
        FUN_00024620(&plStack_120,local_128 & 0xff);
      }
      break;
    case 8:
                    /* try { // try from 0003592a to 00035a26 has its CatchHandler @ 000369a6 */
      uVar5 = FUN_0002b4a0(param_2,0xffffffffffffffff);
      unaff_R12 = (long **)(ulong)uVar5;
      puVar18 = local_f8;
      if ((char)uVar5 != '\0') {
        iVar7 = FUN_00034bb0(param_1 + 0x28);
        *(int *)(param_1 + 0x20) = iVar7;
        if (iVar7 != 10) goto LAB_00036160;
        uVar5 = FUN_0002f4e0(param_2);
LAB_00035953:
        unaff_R12 = (long **)(ulong)uVar5;
        puVar18 = local_f8;
        if ((char)uVar5 != '\0') break;
      }
      goto LAB_000353ea;
    case 9:
      uVar5 = FUN_0002b6d0(param_2,0xffffffffffffffff);
      unaff_R12 = (long **)(ulong)uVar5;
      puVar18 = local_f8;
      if ((char)uVar5 == '\0') goto LAB_000353ea;
      unaff_R15 = (undefined *)(param_1 + 0x28);
      iVar7 = FUN_00034bb0(unaff_R15);
      *(int *)(param_1 + 0x20) = iVar7;
      if (iVar7 == 0xb) {
        uVar5 = FUN_0002f650(param_2);
        goto LAB_00035953;
      }
      if (iVar7 == 4) {
        if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
          *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
        }
        uVar5 = FUN_0002f820(param_2,param_1 + 0x78);
        unaff_R12 = (long **)(ulong)uVar5;
        puVar18 = local_f8;
        if ((char)uVar5 != '\0') {
          iVar7 = FUN_00034bb0(unaff_R15);
          *(int *)(param_1 + 0x20) = iVar7;
          if (iVar7 != 0xc) goto LAB_00036478;
          FUN_00024380(&local_f8,0);
          uVar8 = FUN_00034bb0(unaff_R15);
          goto LAB_00035a00;
        }
        goto LAB_000353ea;
      }
                    /* try { // try from 000363e8 to 000363ec has its CatchHandler @ 000369a6 */
      FUN_00018b10(local_a8,"object key");
                    /* try { // try from 00036403 to 00036407 has its CatchHandler @ 00036aa3 */
      FUN_000234b0(local_88,param_1,4,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined4 **)(param_1 + 0x48);
      plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 00036438 to 0003643c has its CatchHandler @ 00036a9e */
      FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00036450 to 00036454 has its CatchHandler @ 00036aa8 */
      FUN_00023340(local_c8,unaff_R15);
      unaff_R12 = (long **)(ulong)*(byte *)(param_2 + 0x14);
      *(undefined *)(param_2 + 0xf) = 1;
      if (*(byte *)(param_2 + 0x14) != 0) {
                    /* try { // try from 0003646f to 00036473 has its CatchHandler @ 00036aad */
        FUN_00013710(local_68);
LAB_00036478:
                    /* try { // try from 0003648a to 0003648e has its CatchHandler @ 000369a6 */
        FUN_00018b10(local_a8,"object separator");
        puVar15 = local_88;
                    /* try { // try from 000364a5 to 000364a9 has its CatchHandler @ 00036992 */
        FUN_000234b0(puVar15,param_1,0xc,local_a8);
        local_108 = *(undefined8 *)(param_1 + 0x58);
        local_118 = *(undefined4 **)(param_1 + 0x48);
        plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 000364da to 000364de has its CatchHandler @ 00036990 */
        FUN_000191f0(local_68,0x65,&local_118,puVar15);
                    /* try { // try from 000364f2 to 000364f6 has its CatchHandler @ 0003698c */
        FUN_00023340(local_c8,unaff_R15);
        unaff_R12 = (long **)(ulong)*(byte *)(param_2 + 0x14);
        *(undefined *)(param_2 + 0xf) = 1;
        if (*(byte *)(param_2 + 0x14) != 0) {
                    /* try { // try from 00036511 to 00036515 has its CatchHandler @ 0003698e */
          pcVar12 = (char *)FUN_00013710(local_68);
          goto LAB_00036520;
        }
      }
      goto LAB_000353b2;
    case 0xe:
      FUN_00018b10(local_a8,"value");
                    /* try { // try from 00035a3a to 00035a3e has its CatchHandler @ 000369b4 */
      FUN_000234b0(local_88,param_1,0,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined4 **)(param_1 + 0x48);
      plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 00035a6f to 00035a73 has its CatchHandler @ 00036a07 */
      FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00035a85 to 00035a89 has its CatchHandler @ 00036a02 */
      FUN_00023340(local_c8,param_1 + 0x28);
      unaff_R12 = (long **)(ulong)*(byte *)(param_2 + 0x14);
      *(undefined *)(param_2 + 0xf) = 1;
      if (*(byte *)(param_2 + 0x14) == 0) goto LAB_000353b2;
                    /* try { // try from 00035aa4 to 00035aa8 has its CatchHandler @ 00036a11 */
      FUN_00013710(local_68);
switchD_00035317_caseD_6:
      lVar13 = (ulong)*(uint *)(param_2 + 7) - 1;
      lVar10 = (ulong)*(uint *)(param_2 + 7) + 0x3e;
      if (-1 < lVar13) {
        lVar10 = lVar13;
      }
      puVar15 = (ulong *)(param_2[6] + (lVar10 >> 6) * 8);
      if (lVar13 % 0x40 == -1) {
        uVar9 = 0x8000000000000000;
        puVar15 = puVar15 + -1;
      }
      else {
        uVar9 = 1L << ((byte)(lVar13 % 0x40) & 0x3f);
      }
      if ((uVar9 & *puVar15) != 0) {
        local_128 = CONCAT71(local_128._1_7_,5);
        local_134 = (undefined4)((long)(param_2[2] - param_2[1]) >> 3);
        local_140 = 5;
        plStack_120 = *(long **)(param_1 + 0xa0);
        if (param_2[0x12] == 0) {
LAB_000368f4:
                    /* try { // try from 000368f4 to 000368f8 has its CatchHandler @ 00036a3e */
          FUN_00016056();
LAB_000368f9:
                    /* try { // try from 000368f9 to 000368fd has its CatchHandler @ 000368fe */
          param_1 = FUN_00016056();
                    /* catch() { ... } // from try @ 0003579d with catch @ 000368fe
                       catch() { ... } // from try @ 00036644 with catch @ 000368fe
                       catch() { ... } // from try @ 000368f9 with catch @ 000368fe */
          FUN_00024620(unaff_R12,local_128 & 0xff);
          goto LAB_0003691a;
        }
        puVar15 = &local_128;
                    /* try { // try from 00035b43 to 00035b48 has its CatchHandler @ 00036a3e */
        cVar4 = (*(code *)param_2[0x13])(param_2 + 0x10,&local_134,&local_140,puVar15);
        plVar11 = plStack_120;
        uVar9 = local_128;
        if (cVar4 != '\0') {
          if (param_2[2] == param_2[1]) {
            uVar2 = (undefined)local_128;
            local_128 = local_128 & 0xffffffffffffff00;
            plStack_120 = (long *)0x0;
            puVar17 = (undefined *)*param_2;
            uVar1 = *puVar17;
            *puVar17 = uVar2;
            plStack_110 = *(long **)(puVar17 + 8);
            *(long **)(puVar17 + 8) = plVar11;
            local_118._1_7_ = (undefined7)(uVar9 >> 8);
            local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
            FUN_00024620(&plStack_110);
          }
          else {
            pcVar12 = *(char **)(param_2[2] + -8);
            if (pcVar12 != (char *)0x0) {
              if (*pcVar12 == '\x02') {
LAB_00036520:
                    /* try { // try from 00036527 to 0003652b has its CatchHandler @ 00036a3e */
                FUN_000182f0(*(undefined8 *)(pcVar12 + 8),puVar15);
              }
              else {
                lVar10 = param_2[0xb];
                iVar7 = *(int *)(param_2 + 0xc);
                auVar19 = FUN_00017eb0(lVar10,iVar7);
                plVar11 = plStack_120;
                uVar3 = local_128;
                uVar9 = *auVar19._0_8_;
                if (iVar7 == 0) {
                  *(undefined4 *)(param_2 + 0xc) = 0x3f;
                  param_2[0xb] = lVar10 + -8;
                }
                else {
                  *(int *)(param_2 + 0xc) = iVar7 + -1;
                }
                if ((auVar19._8_8_ & uVar9) != 0) {
                  uVar2 = (undefined)local_128;
                  local_128 = local_128 & 0xffffffffffffff00;
                  plStack_120 = (long *)0x0;
                  puVar17 = (undefined *)param_2[0xe];
                  uVar1 = *puVar17;
                  *puVar17 = uVar2;
                  plStack_110 = *(long **)(puVar17 + 8);
                  *(long **)(puVar17 + 8) = plVar11;
                  local_118._1_7_ = (undefined7)(uVar3 >> 8);
                  local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
                  FUN_00024620(&plStack_110);
                }
              }
            }
          }
        }
        FUN_00024620(&plStack_120,local_128 & 0xff);
      }
      break;
    case 0xf:
      if (*(long *)(param_1 + 0x48) == 1) goto LAB_00036298;
                    /* try { // try from 00035d1d to 00035d21 has its CatchHandler @ 000369a6 */
      FUN_00018b10(local_a8,"value");
      puVar15 = local_88;
                    /* try { // try from 00035d38 to 00035d3c has its CatchHandler @ 00036a39 */
      FUN_000234b0(puVar15,param_1,0x10,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined4 **)(param_1 + 0x48);
      plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 00035d6d to 00035d71 has its CatchHandler @ 00036a34 */
      FUN_000191f0(local_68,0x65,&local_118,puVar15);
                    /* try { // try from 00035d83 to 00035d87 has its CatchHandler @ 00036a2a */
      FUN_00023340(local_c8,param_1 + 0x28);
      unaff_R12 = (long **)(ulong)*(byte *)(param_2 + 0x14);
      *(undefined *)(param_2 + 0xf) = 1;
      if (*(byte *)(param_2 + 0x14) != 0) {
                    /* try { // try from 00035da2 to 00035da6 has its CatchHandler @ 00036a2f */
        FUN_00013710(local_68);
        puVar17 = local_a8;
        goto LAB_00035db0;
      }
      goto LAB_000353b2;
    }
LAB_00035448:
    while( true ) {
      puVar17 = local_e8;
      unaff_R15 = local_f8;
      iVar7 = (int)local_e0;
      puVar15 = (ulong *)(local_e0 & 0xffffffff);
      bVar16 = local_e8 == local_f8 && (int)local_e0 == 0;
      unaff_R12 = (long **)CONCAT71((int7)((ulong)unaff_R12 >> 8),bVar16);
      puVar18 = local_f8;
      if (bVar16) goto LAB_000353ea;
      lVar13 = (long)puVar15 + -1;
      lVar10 = (long)puVar15 + 0x3e;
      if (-1 < lVar13) {
        lVar10 = lVar13;
      }
      puVar14 = (ulong *)(local_e8 + (lVar10 >> 6) * 8);
      if (lVar13 % 0x40 == -1) {
        uVar9 = 0x8000000000000000;
        puVar14 = puVar14 + -1;
      }
      else {
        uVar9 = 1L << ((byte)(lVar13 % 0x40) & 0x3f);
      }
      local_160 = param_1 + 0x28;
      if ((uVar9 & *puVar14) == 0) break;
      iVar6 = FUN_00034bb0();
      *(int *)(param_1 + 0x20) = iVar6;
      if (iVar6 == 0xd) goto LAB_00035e86;
      if (iVar6 != 10) {
                    /* try { // try from 00035f52 to 00035f56 has its CatchHandler @ 000369a6 */
        FUN_00018b10(local_a8,"array");
                    /* try { // try from 00035f6d to 00035f71 has its CatchHandler @ 000369c0 */
        FUN_000234b0(local_88,param_1,10,local_a8);
        local_108 = *(undefined8 *)(param_1 + 0x58);
        local_118 = *(undefined4 **)(param_1 + 0x48);
        plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 00035fa2 to 00035fa6 has its CatchHandler @ 000369fb */
        FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00035fbc to 00035fc0 has its CatchHandler @ 000369f6 */
        FUN_00023340(local_c8,local_160);
        *(undefined *)(param_2 + 0xf) = 1;
        if (*(char *)(param_2 + 0x14) == '\0') goto LAB_00035fd2;
                    /* try { // try from 000369f1 to 000369f5 has its CatchHandler @ 000369fd */
        param_1 = FUN_00013710(local_68);
                    /* catch() { ... } // from try @ 00035fbc with catch @ 000369f6 */
        goto LAB_00036945;
      }
      lVar10 = param_2[2];
      if (*(long *)(lVar10 + -8) != 0) {
        local_13d = 3;
        local_128 = CONCAT44(local_128._4_4_,(int)(lVar10 - param_2[1] >> 3) + -1);
        if (param_2[0x12] == 0) {
                    /* try { // try from 000368db to 000368df has its CatchHandler @ 000369a6 */
          FUN_00016056();
          goto LAB_000368e0;
        }
        cVar4 = (*(code *)param_2[0x13])(param_2 + 0x10,&local_128,&local_13d);
        if (cVar4 == '\0') {
          FUN_0002f160(&local_118,param_2 + 0x15);
          puVar18 = *(undefined **)(param_2[2] + -8);
          uVar1 = *puVar18;
          *puVar18 = local_118._0_1_;
          plVar11 = *(long **)(puVar18 + 8);
          *(long **)(puVar18 + 8) = plStack_110;
          local_118 = (undefined4 *)CONCAT71(local_118._1_7_,uVar1);
          plStack_110 = plVar11;
          FUN_00024620(&plStack_110);
          iVar6 = *(int *)(param_2 + 7);
          lVar10 = param_2[2] + -8;
          auVar19._8_8_ = param_2[2];
          auVar19._0_8_ = lVar10;
          param_2[2] = lVar10;
          if (iVar6 != 0) goto LAB_000360b0;
          param_2[6] = param_2[6] + -8;
          *(undefined4 *)(param_2 + 7) = 0x3f;
          goto LAB_00035eff;
        }
        lVar10 = param_2[2];
      }
      param_2[2] = lVar10 + -8;
      if (*(int *)(param_2 + 7) == 0) {
        param_2[6] = param_2[6] + -8;
        *(undefined4 *)(param_2 + 7) = 0x3f;
      }
      else {
        *(int *)(param_2 + 7) = *(int *)(param_2 + 7) + -1;
      }
LAB_00035547:
      if (iVar7 == 0) goto LAB_00035550;
LAB_00035de4:
      local_e0 = CONCAT44(local_e0._4_4_,iVar7 + -1);
    }
LAB_00035db0:
    iVar7 = (int)puVar15;
                    /* try { // try from 00035db5 to 00035ea8 has its CatchHandler @ 000369a6 */
    iVar6 = FUN_00034bb0(local_160);
    *(int *)(param_1 + 0x20) = iVar6;
    puVar18 = unaff_R15;
    if (iVar6 != 0xd) {
      if (iVar6 != 0xb) {
        puVar17 = local_a8;
                    /* try { // try from 00036022 to 00036026 has its CatchHandler @ 000369a6 */
        FUN_00018b10(puVar17,"object");
        puVar15 = local_88;
                    /* try { // try from 0003603d to 00036041 has its CatchHandler @ 000369ea */
        FUN_000234b0(puVar15,param_1,0xb,puVar17);
        local_108 = *(undefined8 *)(param_1 + 0x58);
        local_118 = *(undefined4 **)(param_1 + 0x48);
        plStack_110 = *(long **)(param_1 + 0x50);
        puVar14 = puVar15;
                    /* try { // try from 00036072 to 00036076 has its CatchHandler @ 000369b0 */
        FUN_000191f0(local_68,0x65,&local_118);
        iVar6 = (int)puVar14;
                    /* try { // try from 0003608c to 00036090 has its CatchHandler @ 000369ae */
        FUN_00023340(local_c8,local_160);
        *(undefined *)(param_2 + 0xf) = 1;
        if (*(char *)(param_2 + 0x14) != '\0') {
                    /* try { // try from 000360a7 to 000360ab has its CatchHandler @ 000369b2 */
          auVar19 = FUN_00013710(local_68);
LAB_000360b0:
          iVar7 = (int)puVar15;
          *(int *)(param_2 + 7) = iVar6 + -1;
LAB_00035eff:
          if ((param_2[1] != auVar19._0_8_) &&
             (pcVar12 = *(char **)(auVar19._8_8_ + -0x10), *pcVar12 == '\x02')) {
            lVar10 = *(long *)(pcVar12 + 8);
            lVar13 = *(long *)(lVar10 + 8);
            uVar1 = *(undefined *)(lVar13 + -0x10);
            *(long *)(lVar10 + 8) = lVar13 + -0x10;
            FUN_00024620(lVar13 + -8,uVar1);
          }
          goto LAB_00035547;
        }
        goto LAB_00035fd2;
      }
      cVar4 = FUN_0002f650(param_2);
      if (cVar4 == '\0') goto LAB_000353ea;
      if (iVar7 != 0) goto LAB_00035de4;
LAB_00035550:
      local_e0 = CONCAT44(local_e0._4_4_,0x3f);
      local_e8 = puVar17 + -8;
      goto LAB_00035448;
    }
    iVar7 = FUN_00034bb0(local_160);
    *(int *)(param_1 + 0x20) = iVar7;
    if (iVar7 != 4) {
      FUN_00018b10(local_a8,"object key");
                    /* try { // try from 00036225 to 00036229 has its CatchHandler @ 00036ac1 */
      FUN_000234b0(local_88,param_1,4,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined4 **)(param_1 + 0x48);
      plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 0003625a to 0003625e has its CatchHandler @ 00036abc */
      FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00036274 to 00036278 has its CatchHandler @ 00036ab2 */
      FUN_00023340(local_c8,local_160);
      *(undefined *)(param_2 + 0xf) = 1;
      if (*(char *)(param_2 + 0x14) == '\0') {
LAB_00035fd2:
        local_150 = local_c8;
        local_158 = local_68;
        FUN_000b07c0(local_150);
        local_68[0] = &PTR_FUN_0011ba98;
        FUN_0001a6b0(local_158);
        FUN_000b07c0(local_88);
        FUN_000b07c0(local_a8);
        puVar18 = unaff_R15;
        goto LAB_000353ea;
      }
                    /* try { // try from 0003628f to 00036293 has its CatchHandler @ 00036ab7 */
      FUN_00013710(local_68);
LAB_00036298:
                    /* try { // try from 000362aa to 000362ae has its CatchHandler @ 000369a6 */
      FUN_00018b10(local_88,
                   "attempting to parse an empty input; check that your input string or stream contains the expected JSON"
                  );
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined4 **)(param_1 + 0x48);
      plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 000362df to 000362e3 has its CatchHandler @ 00036a6b */
      FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 000362f3 to 000362f7 has its CatchHandler @ 00036a66 */
      FUN_00023340(local_a8,param_1 + 0x28);
      unaff_R12 = (long **)(ulong)*(byte *)(param_2 + 0x14);
      *(undefined *)(param_2 + 0xf) = 1;
      if (*(byte *)(param_2 + 0x14) != 0) {
                    /* try { // try from 00036a48 to 00036a4c has its CatchHandler @ 00036a61 */
        FUN_00013710(local_68);
        FUN_00024620(&plStack_120,local_128 & 0xff);
        goto LAB_0003691a;
      }
      FUN_000b07c0(local_a8);
      local_68[0] = &PTR_FUN_0011ba98;
      FUN_0001a6b0(local_68);
      FUN_000b07c0(local_88);
      puVar18 = local_f8;
      goto LAB_000353ea;
    }
    if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
      *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
    }
    cVar4 = FUN_0002f820(param_2,param_1 + 0x78);
    if (cVar4 == '\0') goto LAB_000353ea;
    iVar7 = FUN_00034bb0(local_160);
    *(int *)(param_1 + 0x20) = iVar7;
    if (iVar7 == 0xc) {
LAB_00035e86:
      uVar8 = FUN_00034bb0(local_160);
LAB_00035a00:
      *(undefined4 *)(param_1 + 0x20) = uVar8;
    }
    else {
                    /* try { // try from 000360cd to 000360d1 has its CatchHandler @ 000369a6 */
      FUN_00018b10(local_a8,"object separator");
                    /* try { // try from 000360e8 to 000360ec has its CatchHandler @ 00036987 */
      FUN_000234b0(local_88,param_1,0xc,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined4 **)(param_1 + 0x48);
      plStack_110 = *(long **)(param_1 + 0x50);
                    /* try { // try from 0003611d to 00036121 has its CatchHandler @ 00036982 */
      FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00036137 to 0003613b has its CatchHandler @ 00036945 */
      FUN_00023340(local_c8,local_160);
      *(undefined *)(param_2 + 0xf) = 1;
      if (*(char *)(param_2 + 0x14) == '\0') goto LAB_00035fd2;
                    /* try { // try from 00036152 to 00036156 has its CatchHandler @ 0003694a */
      FUN_00013710(local_68);
LAB_00036160:
                    /* try { // try from 0003616a to 0003620e has its CatchHandler @ 000369a6 */
      FUN_00024380(&local_f8,1);
    }
  } while( true );
}


