// ===== FUNC 36b10 size=5381

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_00036b10(long param_1,undefined8 *param_2)

{
  long lVar1;
  undefined uVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined *puVar7;
  ulong uVar8;
  char *pcVar9;
  undefined8 *puVar10;
  undefined8 *puVar11;
  ulong uVar12;
  ulong uVar13;
  ulong uVar14;
  word *pwVar15;
  undefined8 *puVar16;
  undefined8 *puVar17;
  undefined8 uVar18;
  undefined *puVar19;
  undefined8 *puVar20;
  undefined8 *puVar21;
  ulong *puVar22;
  undefined *puVar23;
  bool bVar24;
  undefined8 *unaff_RBP;
  undefined8 *puVar25;
  long lVar26;
  undefined8 *puVar27;
  undefined *puVar28;
  undefined *unaff_R15;
  long in_FS_OFFSET;
  undefined ***local_160;
  undefined *local_158;
  undefined local_13c;
  undefined local_13b;
  undefined local_13a;
  undefined local_139;
  undefined8 local_138;
  undefined8 local_130;
  undefined local_128 [8];
  undefined8 local_120;
  undefined8 local_118;
  undefined8 uStack_110;
  undefined8 local_108;
  undefined *local_f8;
  undefined8 local_f0;
  undefined *local_e8;
  ulong local_e0;
  long local_d8;
  undefined local_c8 [32];
  undefined local_a8 [32];
  undefined local_88 [32];
  undefined **local_68 [5];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  lVar1 = param_1 + 0x28;
  local_f8 = (undefined *)0x0;
  local_f0 = 0;
  local_e8 = (undefined *)0x0;
  local_e0 = 0;
  local_d8 = 0;
LAB_00036b78:
  switch(*(undefined4 *)(param_1 + 0x20)) {
  default:
                    /* try { // try from 00036baa to 00036bae has its CatchHandler @ 0003803d */
    FUN_00018b10(local_a8,"value");
                    /* try { // try from 00036bc5 to 00036bc9 has its CatchHandler @ 0003803b */
    FUN_000234b0(local_88,param_1,0x10,local_a8);
    local_108 = *(undefined8 *)(param_1 + 0x58);
    local_118 = *(undefined8 *)(param_1 + 0x48);
    uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 00036bfa to 00036bfe has its CatchHandler @ 00038039 */
    FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00036c10 to 00036c14 has its CatchHandler @ 00038037 */
    FUN_00023340(local_c8,param_1 + 0x28);
    unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
    *(undefined *)(param_2 + 5) = 1;
    if (*(byte *)((long)param_2 + 0x29) == 0) {
LAB_00036c28:
      local_158 = local_c8;
      FUN_000b07c0(local_158);
      local_68[0] = &PTR_FUN_0011ba98;
LAB_00036c39:
      local_160 = local_68;
      FUN_0001a6b0(local_160);
      FUN_000b07c0(local_88);
      FUN_000b07c0(local_a8);
      unaff_R15 = local_f8;
LAB_00036c60:
      if (unaff_R15 != (undefined *)0x0) {
        thunk_FUN_000d36e0(unaff_R15,local_d8 - (long)unaff_R15);
      }
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        return (ulong)unaff_RBP & 0xffffffff;
      }
LAB_00037e6c:
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
                    /* try { // try from 0003809a to 0003809e has its CatchHandler @ 000380a4 */
    uVar18 = FUN_00013710(local_68);
                    /* catch() { ... } // from try @ 00037e67 with catch @ 00037fe5 */
    FUN_000b07c0(local_c8);
                    /* catch() { ... } // from try @ 00037280 with catch @ 0003809f */
LAB_00037ff2:
    local_160 = local_68;
    local_68[0] = &PTR_FUN_0011ba98;
    FUN_0001a6b0(local_160);
LAB_0003800b:
    FUN_000b07c0(local_88);
LAB_00038013:
    FUN_000b07c0(local_a8);
    FUN_00025b20(&local_f8);
                    /* WARNING: Subroutine does not return */
    FUN_000ddde0(uVar18);
  case 1:
    local_13b = 1;
    if (param_2[2] == param_2[1]) {
      puVar23 = (undefined *)*param_2;
      uVar2 = *puVar23;
      uStack_110 = *(undefined8 *)(puVar23 + 8);
      *puVar23 = 4;
      *(undefined8 *)(puVar23 + 8) = 1;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      FUN_00024620(&uStack_110);
    }
    else {
      pcVar9 = *(char **)(param_2[2] + -8);
      if (*pcVar9 == '\x02') {
        FUN_0001ac90(*(undefined8 *)(pcVar9 + 8),&local_13b);
      }
      else {
        puVar23 = (undefined *)param_2[4];
        uVar2 = *puVar23;
        uStack_110 = *(undefined8 *)(puVar23 + 8);
        *puVar23 = 4;
        *(undefined8 *)(puVar23 + 8) = 1;
        local_118 = CONCAT71(local_118._1_7_,uVar2);
        FUN_00024620(&uStack_110);
      }
    }
    break;
  case 2:
    local_13c = 0;
    if (param_2[2] == param_2[1]) {
      puVar23 = (undefined *)*param_2;
      uVar2 = *puVar23;
      uStack_110 = *(undefined8 *)(puVar23 + 8);
      *puVar23 = 4;
      *(undefined8 *)(puVar23 + 8) = 0;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      FUN_00024620(&uStack_110);
    }
    else {
      pcVar9 = *(char **)(param_2[2] + -8);
      if (*pcVar9 == '\x02') {
        FUN_0001ac90(*(undefined8 *)(pcVar9 + 8),&local_13c);
      }
      else {
        puVar23 = (undefined *)param_2[4];
        uVar2 = *puVar23;
        uStack_110 = *(undefined8 *)(puVar23 + 8);
        *puVar23 = 4;
        *(undefined8 *)(puVar23 + 8) = 0;
        local_118 = CONCAT71(local_118._1_7_,uVar2);
        FUN_00024620(&uStack_110);
      }
    }
    break;
  case 3:
    if (param_2[2] == param_2[1]) {
      puVar23 = (undefined *)*param_2;
      uVar2 = *puVar23;
      uStack_110 = *(undefined8 *)(puVar23 + 8);
      *puVar23 = 0;
      *(undefined8 *)(puVar23 + 8) = 0;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      FUN_00024620(&uStack_110);
    }
    else {
      pcVar9 = *(char **)(param_2[2] + -8);
      if (*pcVar9 == '\x02') {
        unaff_RBP = *(undefined8 **)(pcVar9 + 8);
        puVar27 = (undefined8 *)unaff_RBP[1];
        puVar25 = (undefined8 *)unaff_RBP[2];
        if (puVar27 == puVar25) {
          puVar20 = (undefined8 *)*unaff_RBP;
          uVar8 = (long)puVar27 - (long)puVar20 >> 4;
          if (uVar8 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
            FUN_00015e26("vector::_M_realloc_insert");
          }
          uVar13 = 1;
          if (puVar27 != puVar20) {
            uVar13 = uVar8;
          }
          uVar12 = uVar8 + uVar13;
          if (CARRY8(uVar8,uVar13)) {
            local_160 = (undefined ***)0x7ffffffffffffff0;
LAB_00037f05:
            puVar16 = (undefined8 *)FUN_00041fe0(local_160);
            puVar25 = (undefined8 *)unaff_RBP[2];
            pwVar15 = (word *)(puVar16 + 2);
            lVar26 = (long)local_160 + (long)puVar16;
          }
          else {
            if (uVar12 != 0) {
              if (0x7ffffffffffffff < uVar12) {
                uVar12 = 0x7ffffffffffffff;
              }
              local_160 = (undefined ***)(uVar12 << 4);
              goto LAB_00037f05;
            }
            pwVar15 = &Elf64_Ehdr_00000000.e_type;
            lVar26 = 0;
            puVar16 = (undefined8 *)0x0;
          }
          puVar23 = (undefined *)(((long)puVar27 - (long)puVar20) + (long)puVar16);
          *puVar23 = 0;
          *(undefined8 *)(puVar23 + 8) = 0;
          if (puVar27 != puVar20) {
            puVar27 = (undefined8 *)((long)puVar16 + ((long)puVar27 - (long)puVar20));
            puVar17 = puVar16;
            puVar10 = puVar20;
            do {
              uVar18 = *puVar10;
              uVar3 = puVar10[1];
              puVar21 = puVar17 + 2;
              puVar10 = puVar10 + 2;
              *puVar17 = uVar18;
              puVar17[1] = uVar3;
              puVar17 = puVar21;
            } while (puVar27 != puVar21);
            pwVar15 = (word *)(puVar27 + 2);
          }
          if (puVar20 != (undefined8 *)0x0) {
            thunk_FUN_000d36e0(puVar20,(long)puVar25 - (long)puVar20);
          }
          *unaff_RBP = puVar16;
          unaff_RBP[1] = pwVar15;
          unaff_RBP[2] = lVar26;
        }
        else {
          *(undefined *)puVar27 = 0;
          puVar27[1] = 0;
          unaff_RBP[1] = puVar27 + 2;
        }
      }
      else {
        puVar23 = (undefined *)param_2[4];
        uVar2 = *puVar23;
        uStack_110 = *(undefined8 *)(puVar23 + 8);
        *puVar23 = 0;
        *(undefined8 *)(puVar23 + 8) = 0;
        local_118 = CONCAT71(local_118._1_7_,uVar2);
        FUN_00024620(&uStack_110);
      }
    }
    break;
  case 4:
    if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
      *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
    }
    if (param_2[2] == param_2[1]) {
                    /* try { // try from 000378c5 to 000378c9 has its CatchHandler @ 0003803d */
      FUN_00025fe0(&local_118);
      puVar23 = (undefined *)*param_2;
      uVar2 = *puVar23;
      *puVar23 = (undefined)local_118;
      uVar18 = *(undefined8 *)(puVar23 + 8);
      *(undefined8 *)(puVar23 + 8) = uStack_110;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      uStack_110 = uVar18;
      FUN_00024620(&uStack_110);
    }
    else {
      pcVar9 = *(char **)(param_2[2] + -8);
      if (*pcVar9 == '\x02') {
        unaff_RBP = *(undefined8 **)(pcVar9 + 8);
        if (unaff_RBP[1] == unaff_RBP[2]) {
                    /* try { // try from 00037b57 to 00037b5b has its CatchHandler @ 0003803d */
          FUN_0002ef00(unaff_RBP,unaff_RBP[1],param_1 + 0x78);
        }
        else {
                    /* try { // try from 000375c2 to 000376a3 has its CatchHandler @ 0003803d */
          FUN_00025fe0();
          unaff_RBP[1] = unaff_RBP[1] + 0x10;
        }
      }
      else {
                    /* try { // try from 00036ea2 to 00036ea6 has its CatchHandler @ 0003803d */
        FUN_00025fe0(local_128);
        puVar23 = (undefined *)param_2[4];
        uVar2 = *puVar23;
        *puVar23 = local_128[0];
        uVar18 = *(undefined8 *)(puVar23 + 8);
        *(undefined8 *)(puVar23 + 8) = local_120;
        local_128[0] = uVar2;
        local_120 = uVar18;
        FUN_00024620(&local_120);
      }
    }
    break;
  case 5:
    unaff_RBP = *(undefined8 **)(param_1 + 0xa8);
    if (param_2[2] == param_2[1]) {
      puVar23 = (undefined *)*param_2;
      uVar2 = *puVar23;
      uStack_110 = *(undefined8 *)(puVar23 + 8);
      *puVar23 = 6;
      *(undefined8 **)(puVar23 + 8) = unaff_RBP;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      FUN_00024620(&uStack_110);
    }
    else {
      pcVar9 = *(char **)(param_2[2] + -8);
      if (*pcVar9 == '\x02') {
        puVar27 = *(undefined8 **)(pcVar9 + 8);
        puVar25 = (undefined8 *)puVar27[1];
        puVar20 = (undefined8 *)puVar27[2];
        if (puVar25 == puVar20) {
          puVar16 = (undefined8 *)*puVar27;
          uVar8 = (long)puVar25 - (long)puVar16 >> 4;
          if (uVar8 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
            FUN_00015e26("vector::_M_realloc_insert");
          }
          uVar13 = 1;
          if (puVar25 != puVar16) {
            uVar13 = uVar8;
          }
          uVar12 = uVar8 + uVar13;
          if (CARRY8(uVar8,uVar13)) {
            local_160 = (undefined ***)0x7ffffffffffffff0;
LAB_00037ec9:
            puVar17 = (undefined8 *)FUN_00041fe0(local_160);
            puVar20 = (undefined8 *)puVar27[2];
            pwVar15 = (word *)(puVar17 + 2);
            lVar26 = (long)local_160 + (long)puVar17;
          }
          else {
            if (uVar12 != 0) {
              if (0x7ffffffffffffff < uVar12) {
                uVar12 = 0x7ffffffffffffff;
              }
              local_160 = (undefined ***)(uVar12 << 4);
              goto LAB_00037ec9;
            }
            pwVar15 = &Elf64_Ehdr_00000000.e_type;
            lVar26 = 0;
            puVar17 = (undefined8 *)0x0;
          }
          puVar23 = (undefined *)(((long)puVar25 - (long)puVar16) + (long)puVar17);
          *puVar23 = 6;
          *(undefined8 **)(puVar23 + 8) = unaff_RBP;
          puVar10 = puVar16;
          puVar21 = puVar17;
          if (puVar25 != puVar16) {
            do {
              uVar18 = puVar10[1];
              puVar11 = puVar10 + 2;
              *puVar21 = *puVar10;
              puVar21[1] = uVar18;
              puVar10 = puVar11;
              puVar21 = puVar21 + 2;
            } while (puVar25 != puVar11);
            pwVar15 = (word *)((long)puVar17 + (long)((long)puVar25 + (0x10 - (long)puVar16)));
          }
          if (puVar16 != (undefined8 *)0x0) {
            thunk_FUN_000d36e0(puVar16,(long)puVar20 - (long)puVar16);
          }
          *puVar27 = puVar17;
          puVar27[1] = pwVar15;
          puVar27[2] = lVar26;
        }
        else {
          *(undefined *)puVar25 = 6;
          puVar25[1] = unaff_RBP;
          puVar27[1] = puVar25 + 2;
        }
      }
      else {
        puVar23 = (undefined *)param_2[4];
        uVar2 = *puVar23;
        uStack_110 = *(undefined8 *)(puVar23 + 8);
        *puVar23 = 6;
        *(undefined8 **)(puVar23 + 8) = unaff_RBP;
        local_118 = CONCAT71(local_118._1_7_,uVar2);
        FUN_00024620(&uStack_110);
      }
    }
    break;
  case 6:
    unaff_RBP = *(undefined8 **)(param_1 + 0xa0);
    if (param_2[2] == param_2[1]) {
      puVar23 = (undefined *)*param_2;
      uVar2 = *puVar23;
      uStack_110 = *(undefined8 *)(puVar23 + 8);
      *puVar23 = 5;
      *(undefined8 **)(puVar23 + 8) = unaff_RBP;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      FUN_00024620(&uStack_110);
    }
    else {
      pcVar9 = *(char **)(param_2[2] + -8);
      if (*pcVar9 == '\x02') goto LAB_00037550;
      puVar23 = (undefined *)param_2[4];
      uVar2 = *puVar23;
      uStack_110 = *(undefined8 *)(puVar23 + 8);
      *puVar23 = 5;
      *(undefined8 **)(puVar23 + 8) = unaff_RBP;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      FUN_00024620(&uStack_110);
    }
    break;
  case 7:
    uVar8 = *(ulong *)(param_1 + 0xb0);
    if (DAT_000e2e40 < (double)(uVar8 & _DAT_000e2ea0)) {
      local_118 = CONCAT71(local_118._1_7_,0x27);
      FUN_00023340(local_a8,param_1 + 0x28);
                    /* try { // try from 0003778c to 00037790 has its CatchHandler @ 0003814c */
      FUN_000243f0(local_88,"number overflow parsing \'",local_a8,&local_118);
                    /* try { // try from 000377a9 to 000377ad has its CatchHandler @ 00038147 */
      FUN_00018f90(local_68,0x196,local_88);
                    /* try { // try from 000377c1 to 000377c5 has its CatchHandler @ 00038117 */
      FUN_00023340(local_c8,param_1 + 0x28);
      unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
      *(undefined *)(param_2 + 5) = 1;
      if (*(byte *)((long)param_2 + 0x29) == 0) {
        FUN_000b07c0(local_c8);
        local_68[0] = &PTR_FUN_0011bb10;
        goto LAB_00036c39;
      }
                    /* try { // try from 00038112 to 00038116 has its CatchHandler @ 0003811c */
      uVar18 = FUN_00013768(local_68);
                    /* catch() { ... } // from try @ 000377c1 with catch @ 00038117 */
      local_68[0] = &PTR_FUN_0011bb10;
      FUN_0001a6b0(local_68);
      goto LAB_0003800b;
    }
    if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
      *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
    }
    if (param_2[2] == param_2[1]) {
      puVar23 = (undefined *)*param_2;
      uVar2 = *puVar23;
      uStack_110 = *(undefined8 *)(puVar23 + 8);
      *puVar23 = 7;
      *(ulong *)(puVar23 + 8) = uVar8;
      local_118 = CONCAT71(local_118._1_7_,uVar2);
      FUN_00024620(&uStack_110);
    }
    else {
      pcVar9 = *(char **)(param_2[2] + -8);
      if (*pcVar9 == '\x02') {
        puVar27 = *(undefined8 **)(pcVar9 + 8);
        puVar25 = (undefined8 *)puVar27[1];
        puVar20 = (undefined8 *)puVar27[2];
        if (puVar25 == puVar20) {
          puVar16 = (undefined8 *)*puVar27;
          unaff_RBP = (undefined8 *)((long)puVar25 - (long)puVar16);
          uVar13 = (long)unaff_RBP >> 4;
          if (uVar13 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
            FUN_00015e26("vector::_M_realloc_insert");
          }
          uVar12 = 1;
          if (puVar25 != puVar16) {
            uVar12 = uVar13;
          }
          uVar14 = uVar13 + uVar12;
          if (CARRY8(uVar13,uVar12)) {
            local_158 = (undefined *)0x7ffffffffffffff0;
          }
          else {
            if (uVar14 == 0) {
              pwVar15 = &Elf64_Ehdr_00000000.e_type;
              lVar26 = 0;
              puVar17 = (undefined8 *)0x0;
              goto LAB_00037cbb;
            }
            if (0x7ffffffffffffff < uVar14) {
              uVar14 = 0x7ffffffffffffff;
            }
            local_158 = (undefined *)(uVar14 << 4);
          }
                    /* try { // try from 00037e85 to 00037fdf has its CatchHandler @ 0003803d */
          puVar17 = (undefined8 *)FUN_00041fe0(local_158);
          puVar20 = (undefined8 *)puVar27[2];
          lVar26 = (long)local_158 + (long)puVar17;
          pwVar15 = (word *)(puVar17 + 2);
LAB_00037cbb:
          *(undefined *)((long)puVar17 + (long)unaff_RBP) = 7;
          *(ulong *)((undefined *)((long)puVar17 + (long)unaff_RBP) + 8) = uVar8;
          if (puVar25 != puVar16) {
            puVar10 = puVar17;
            puVar21 = puVar16;
            do {
              puVar11 = puVar10;
              uVar18 = *puVar21;
              uVar3 = puVar21[1];
              puVar21 = puVar21 + 2;
              *puVar11 = uVar18;
              puVar11[1] = uVar3;
              puVar10 = puVar11 + 2;
            } while (puVar11 + 2 != (undefined8 *)((long)puVar17 + ((long)puVar25 - (long)puVar16)))
            ;
            pwVar15 = (word *)(puVar11 + 4);
          }
          if (puVar16 == (undefined8 *)0x0) goto LAB_00037c1f;
          thunk_FUN_000d36e0(puVar16,(long)puVar20 - (long)puVar16);
          goto LAB_00037c1f;
        }
        *(undefined *)puVar25 = 7;
        puVar25[1] = uVar8;
        puVar27[1] = puVar25 + 2;
      }
      else {
        puVar23 = (undefined *)param_2[4];
        uVar2 = *puVar23;
        uStack_110 = *(undefined8 *)(puVar23 + 8);
        *puVar23 = 7;
        *(ulong *)(puVar23 + 8) = uVar8;
        local_118 = CONCAT71(local_118._1_7_,uVar2);
        FUN_00024620(&uStack_110);
      }
    }
    break;
  case 8:
    goto switchD_00036b8f_caseD_8;
  case 9:
    local_13a = 1;
    local_138 = FUN_0002edc0(param_2,&local_13a);
    puVar27 = (undefined8 *)param_2[2];
    if (puVar27 == (undefined8 *)param_2[3]) goto LAB_00037730;
    *puVar27 = local_138;
    param_2[2] = puVar27 + 1;
    goto LAB_000370b0;
  case 0xe:
    FUN_00018b10(local_a8,"value");
                    /* try { // try from 0003716a to 0003716e has its CatchHandler @ 00038108 */
    FUN_000234b0(local_88,param_1,0,local_a8);
    local_108 = *(undefined8 *)(param_1 + 0x58);
    local_118 = *(undefined8 *)(param_1 + 0x48);
    uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 0003719f to 000371a3 has its CatchHandler @ 00038103 */
    FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 000371b5 to 000371b9 has its CatchHandler @ 000380f9 */
    FUN_00023340(local_c8,param_1 + 0x28);
    unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
    *(undefined *)(param_2 + 5) = 1;
    if (*(byte *)((long)param_2 + 0x29) != 0) {
                    /* try { // try from 000371d2 to 000371d6 has its CatchHandler @ 000380fe */
      FUN_00013710(local_68);
      goto switchD_00036b8f_caseD_f;
    }
    goto LAB_00036c28;
  case 0xf:
switchD_00036b8f_caseD_f:
    if (*(long *)(param_1 + 0x48) != 1) {
                    /* try { // try from 000371fd to 00037201 has its CatchHandler @ 0003803d */
      FUN_00018b10(local_a8,"value");
      puVar23 = local_88;
                    /* try { // try from 00037218 to 0003721c has its CatchHandler @ 000380c7 */
      FUN_000234b0(puVar23,param_1,0x10,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined8 *)(param_1 + 0x48);
      uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 0003724d to 00037251 has its CatchHandler @ 0003804c */
      FUN_000191f0(local_68,0x65,&local_118,puVar23);
                    /* try { // try from 00037263 to 00037267 has its CatchHandler @ 0003804a */
      FUN_00023340(local_c8,param_1 + 0x28);
      unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
      *(undefined *)(param_2 + 5) = 1;
      if (*(byte *)((long)param_2 + 0x29) != 0) {
                    /* try { // try from 00037280 to 00037284 has its CatchHandler @ 0003809f */
        FUN_00013710(local_68);
        puVar28 = local_a8;
        goto LAB_00037288;
      }
      goto LAB_00036c28;
    }
                    /* try { // try from 00037801 to 00037805 has its CatchHandler @ 0003803d */
    FUN_00018b10(local_88,
                 "attempting to parse an empty input; check that your input string or stream contains the expected JSON"
                );
    local_108 = *(undefined8 *)(param_1 + 0x58);
    local_118 = *(undefined8 *)(param_1 + 0x48);
    uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 00037836 to 0003783a has its CatchHandler @ 00038053 */
    FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 0003784a to 0003784e has its CatchHandler @ 0003804e */
    FUN_00023340(local_a8,param_1 + 0x28);
    unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
    *(undefined *)(param_2 + 5) = 1;
    if (*(byte *)((long)param_2 + 0x29) == 0) {
      FUN_000b07c0(local_a8);
      local_68[0] = &PTR_FUN_0011ba98;
      FUN_0001a6b0(local_68);
      FUN_000b07c0(local_88);
      unaff_R15 = local_f8;
      goto LAB_00036c60;
    }
                    /* try { // try from 000380c2 to 000380c6 has its CatchHandler @ 000380cc */
    uVar18 = FUN_00013710(local_68);
                    /* catch() { ... } // from try @ 00037dfd with catch @ 00038032 */
                    /* catch() { ... } // from try @ 00037218 with catch @ 000380c7 */
    goto LAB_00038013;
  }
LAB_00036cf8:
  puVar28 = local_e8;
  unaff_R15 = local_f8;
  iVar5 = (int)local_e0;
  puVar23 = (undefined *)(local_e0 & 0xffffffff);
  bVar24 = (int)local_e0 == 0 && local_e8 == local_f8;
  unaff_RBP = (undefined8 *)CONCAT71((int7)((ulong)unaff_RBP >> 8),bVar24);
  if (bVar24) goto LAB_00036c60;
  puVar19 = puVar23 + -1;
  puVar7 = puVar23 + 0x3e;
  if (-1 < (long)puVar19) {
    puVar7 = puVar19;
  }
  puVar22 = (ulong *)(local_e8 + ((long)puVar7 >> 6) * 8);
  if ((long)puVar19 % 0x40 == -1) {
    uVar8 = 0x8000000000000000;
    puVar22 = puVar22 + -1;
  }
  else {
    uVar8 = 1L << ((byte)((long)puVar19 % 0x40) & 0x3f);
  }
  if ((uVar8 & *puVar22) != 0) {
                    /* try { // try from 00036d6d to 00036d71 has its CatchHandler @ 0003803d */
    iVar4 = FUN_00034bb0(lVar1);
    *(int *)(param_1 + 0x20) = iVar4;
    if (iVar4 == 0xd) {
LAB_00037401:
      uVar6 = FUN_00034bb0(lVar1);
      goto LAB_00037130;
    }
    if (iVar4 == 10) goto LAB_00036d87;
    FUN_00018b10(local_a8,"array");
                    /* try { // try from 0003743d to 00037441 has its CatchHandler @ 00038048 */
    FUN_000234b0(local_88,param_1,10,local_a8);
    local_108 = *(undefined8 *)(param_1 + 0x58);
    local_118 = *(undefined8 *)(param_1 + 0x48);
    uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 00037472 to 00037476 has its CatchHandler @ 00038046 */
    FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 0003748b to 0003748f has its CatchHandler @ 00038042 */
    FUN_00023340(local_c8,lVar1);
    *(undefined *)(param_2 + 5) = 1;
    if (*(char *)((long)param_2 + 0x29) != '\0') {
                    /* try { // try from 000374a5 to 000374a9 has its CatchHandler @ 00038044 */
      FUN_00013710(local_68);
      goto LAB_000374b0;
    }
LAB_00037335:
    local_158 = local_c8;
    local_160 = local_68;
    FUN_000b07c0(local_158);
    local_68[0] = &PTR_FUN_0011ba98;
    FUN_0001a6b0(local_160);
    FUN_000b07c0(local_88);
    FUN_000b07c0(local_a8);
    goto LAB_00036c60;
  }
LAB_00037288:
  iVar5 = (int)puVar23;
                    /* try { // try from 00037288 to 000372b8 has its CatchHandler @ 0003803d */
  iVar4 = FUN_00034bb0();
  *(int *)(param_1 + 0x20) = iVar4;
  if (iVar4 != 0xd) {
    if (iVar4 != 0xb) {
      FUN_00018b10(local_a8,"object");
                    /* try { // try from 000372cf to 000372d3 has its CatchHandler @ 00038093 */
      FUN_000234b0(local_88,param_1,0xb,local_a8);
      local_108 = *(undefined8 *)(param_1 + 0x58);
      local_118 = *(undefined8 *)(param_1 + 0x48);
      uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 00037304 to 00037308 has its CatchHandler @ 00038091 */
      FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 0003731d to 00037321 has its CatchHandler @ 000380db */
      FUN_00023340(local_c8,lVar1);
      unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
      *(undefined *)(param_2 + 5) = 1;
      if (*(byte *)((long)param_2 + 0x29) == 0) goto LAB_00037335;
                    /* try { // try from 000380d6 to 000380da has its CatchHandler @ 000380e0 */
      uVar18 = FUN_00013710(local_68);
                    /* catch() { ... } // from try @ 00037e4a with catch @ 00037fe0 */
                    /* catch() { ... } // from try @ 0003731d with catch @ 000380db */
      goto LAB_00037ff2;
    }
LAB_00036d87:
    param_2[2] = param_2[2] + -8;
    if (iVar5 == 0) {
      local_e0 = CONCAT44(local_e0._4_4_,0x3f);
      local_e8 = puVar28 + -8;
    }
    else {
      local_e0 = CONCAT44(local_e0._4_4_,iVar5 + -1);
    }
    goto LAB_00036cf8;
  }
                    /* try { // try from 000373a4 to 00037426 has its CatchHandler @ 0003803d */
  iVar5 = FUN_00034bb0(lVar1);
  *(int *)(param_1 + 0x20) = iVar5;
  if (iVar5 == 4) {
    if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
      *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
    }
    uVar18 = FUN_00026770(*(undefined8 *)(*(long *)(param_2[2] + -8) + 8),param_1 + 0x78);
    param_2[4] = uVar18;
    iVar5 = FUN_00034bb0(lVar1);
    *(int *)(param_1 + 0x20) = iVar5;
    if (iVar5 == 0xc) goto LAB_00037401;
LAB_000374b0:
                    /* try { // try from 000374c2 to 000374c6 has its CatchHandler @ 0003803d */
    FUN_00018b10(local_a8,"object separator");
                    /* try { // try from 000374dd to 000374e1 has its CatchHandler @ 0003808f */
    FUN_000234b0(local_88,param_1,0xc,local_a8);
    local_108 = *(undefined8 *)(param_1 + 0x58);
    local_118 = *(undefined8 *)(param_1 + 0x48);
    uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 00037512 to 00037516 has its CatchHandler @ 0003808d */
    FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 0003752b to 0003752f has its CatchHandler @ 00038083 */
    FUN_00023340(local_c8,lVar1);
    unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
    *(undefined *)(param_2 + 5) = 1;
    if (*(byte *)((long)param_2 + 0x29) == 0) goto LAB_00037335;
                    /* try { // try from 00037548 to 0003754c has its CatchHandler @ 00038088 */
    pcVar9 = (char *)FUN_00013710(local_68);
LAB_00037550:
    puVar27 = *(undefined8 **)(pcVar9 + 8);
    puVar25 = (undefined8 *)puVar27[1];
    puVar20 = (undefined8 *)puVar27[2];
    if (puVar25 == puVar20) {
      puVar16 = (undefined8 *)*puVar27;
      uVar8 = (long)puVar25 - (long)puVar16 >> 4;
      if (uVar8 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
        FUN_00015e26("vector::_M_realloc_insert");
      }
      uVar13 = 1;
      if (puVar25 != puVar16) {
        uVar13 = uVar8;
      }
      uVar12 = uVar8 + uVar13;
      if (CARRY8(uVar8,uVar13)) {
        local_158 = (undefined *)0x7ffffffffffffff0;
LAB_00037f41:
        puVar17 = (undefined8 *)FUN_00041fe0(local_158);
        puVar20 = (undefined8 *)puVar27[2];
        lVar26 = (long)local_158 + (long)puVar17;
        pwVar15 = (word *)(puVar17 + 2);
      }
      else {
        if (uVar12 != 0) {
          if (0x7ffffffffffffff < uVar12) {
            uVar12 = 0x7ffffffffffffff;
          }
          local_158 = (undefined *)(uVar12 << 4);
          goto LAB_00037f41;
        }
        pwVar15 = &Elf64_Ehdr_00000000.e_type;
        lVar26 = 0;
        puVar17 = (undefined8 *)0x0;
      }
      puVar23 = (undefined *)(((long)puVar25 - (long)puVar16) + (long)puVar17);
      *puVar23 = 5;
      *(undefined8 **)(puVar23 + 8) = unaff_RBP;
      if (puVar25 != puVar16) {
        puVar10 = puVar17;
        puVar21 = puVar16;
        do {
          puVar11 = puVar10;
          uVar18 = *puVar21;
          uVar3 = puVar21[1];
          puVar21 = puVar21 + 2;
          *puVar11 = uVar18;
          puVar11[1] = uVar3;
          puVar10 = puVar11 + 2;
        } while (puVar11 + 2 != (undefined8 *)((long)puVar17 + ((long)puVar25 - (long)puVar16)));
        pwVar15 = (word *)(puVar11 + 4);
      }
      if (puVar16 != (undefined8 *)0x0) {
        thunk_FUN_000d36e0(puVar16,(long)puVar20 - (long)puVar16);
      }
LAB_00037c1f:
      *puVar27 = puVar17;
      puVar27[1] = pwVar15;
      puVar27[2] = lVar26;
    }
    else {
      *(undefined *)puVar25 = 5;
      puVar25[1] = unaff_RBP;
      puVar27[1] = puVar25 + 2;
    }
    goto LAB_00036cf8;
  }
  FUN_00018b10(local_a8,"object key");
                    /* try { // try from 000376ba to 000376be has its CatchHandler @ 000380b8 */
  FUN_000234b0(local_88,param_1,4,local_a8);
  local_108 = *(undefined8 *)(param_1 + 0x58);
  local_118 = *(undefined8 *)(param_1 + 0x48);
  uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 000376ef to 000376f3 has its CatchHandler @ 000380b3 */
  FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00037708 to 0003770c has its CatchHandler @ 000380a9 */
  FUN_00023340(local_c8,lVar1);
  *(undefined *)(param_2 + 5) = 1;
  if (*(char *)((long)param_2 + 0x29) == '\0') goto LAB_00037335;
                    /* try { // try from 00037722 to 00037726 has its CatchHandler @ 000380ae */
  FUN_00013710(local_68);
LAB_00037730:
                    /* try { // try from 00037739 to 00037771 has its CatchHandler @ 0003803d */
  FUN_0002ea40(param_2 + 1);
LAB_000370b0:
  unaff_RBP = (undefined8 *)(param_1 + 0x28);
  iVar5 = FUN_00034bb0(unaff_RBP);
  *(int *)(param_1 + 0x20) = iVar5;
  if (iVar5 == 0xb) {
LAB_0003706d:
    param_2[2] = param_2[2] + -8;
    goto LAB_00036cf8;
  }
  if (iVar5 == 4) {
    if ((*(int *)(param_1 + 0xb8) != 0x2e) && (*(long *)(param_1 + 0xc0) != -1)) {
      *(undefined *)(*(long *)(param_1 + 0x78) + *(long *)(param_1 + 0xc0)) = 0x2e;
    }
    uVar18 = FUN_00026770(*(undefined8 *)(*(long *)(param_2[2] + -8) + 8),param_1 + 0x78);
    param_2[4] = uVar18;
    iVar5 = FUN_00034bb0(unaff_RBP);
    *(int *)(param_1 + 0x20) = iVar5;
    if (iVar5 == 0xc) {
      FUN_00024380(&local_f8,0);
      uVar6 = FUN_00034bb0(unaff_RBP);
LAB_00037130:
      *(undefined4 *)(param_1 + 0x20) = uVar6;
      goto LAB_00036b78;
    }
  }
  else {
                    /* try { // try from 00037d42 to 00037d46 has its CatchHandler @ 0003803d */
    FUN_00018b10(local_a8,"object key");
                    /* try { // try from 00037d5d to 00037d61 has its CatchHandler @ 000380f4 */
    FUN_000234b0(local_88,param_1,4,local_a8);
    local_108 = *(undefined8 *)(param_1 + 0x58);
    local_118 = *(undefined8 *)(param_1 + 0x48);
    uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 00037d92 to 00037d96 has its CatchHandler @ 000380ef */
    FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00037daa to 00037dae has its CatchHandler @ 000380e5 */
    FUN_00023340(local_c8,unaff_RBP);
    unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
    *(undefined *)(param_2 + 5) = 1;
    if (*(byte *)((long)param_2 + 0x29) == 0) goto LAB_00036c28;
                    /* try { // try from 00037dc7 to 00037dcb has its CatchHandler @ 000380ea */
    FUN_00013710(local_68);
  }
                    /* try { // try from 00037de2 to 00037de6 has its CatchHandler @ 0003803d */
  FUN_00018b10(local_a8,"object separator");
                    /* try { // try from 00037dfd to 00037e01 has its CatchHandler @ 00038032 */
  FUN_000234b0(local_88,param_1,0xc,local_a8);
  local_108 = *(undefined8 *)(param_1 + 0x58);
  local_118 = *(undefined8 *)(param_1 + 0x48);
  uStack_110 = *(undefined8 *)(param_1 + 0x50);
                    /* try { // try from 00037e32 to 00037e36 has its CatchHandler @ 0003802d */
  FUN_000191f0(local_68,0x65,&local_118,local_88);
                    /* try { // try from 00037e4a to 00037e4e has its CatchHandler @ 00037fe0 */
  FUN_00023340(local_c8,unaff_RBP);
  unaff_RBP = (undefined8 *)(ulong)*(byte *)((long)param_2 + 0x29);
  *(undefined *)(param_2 + 5) = 1;
  if (*(byte *)((long)param_2 + 0x29) == 0) goto LAB_00036c28;
                    /* try { // try from 00037e67 to 00037e6b has its CatchHandler @ 00037fe5 */
  FUN_00013710(local_68);
  goto LAB_00037e6c;
switchD_00036b8f_caseD_8:
  local_139 = 2;
                    /* try { // try from 00037035 to 00037156 has its CatchHandler @ 0003803d */
  local_130 = FUN_0002edc0(param_2,&local_139);
  puVar27 = (undefined8 *)param_2[2];
  if (puVar27 == (undefined8 *)param_2[3]) {
    FUN_0002ea40(param_2 + 1,puVar27,&local_130);
  }
  else {
    *puVar27 = local_130;
    param_2[2] = puVar27 + 1;
  }
  iVar5 = FUN_00034bb0(param_1 + 0x28);
  *(int *)(param_1 + 0x20) = iVar5;
  if (iVar5 == 10) goto LAB_0003706d;
  FUN_00024380(&local_f8,1);
  goto LAB_00036b78;
}


