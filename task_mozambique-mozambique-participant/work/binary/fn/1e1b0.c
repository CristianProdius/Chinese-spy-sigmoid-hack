// ===== FUNC 1e1b0 size=5398

undefined8 * FUN_0001e1b0(undefined8 *param_1,int param_2,ulong *param_3)

{
  uint *puVar1;
  int iVar2;
  bool bVar3;
  undefined auVar4 [16];
  undefined auVar5 [16];
  undefined auVar6 [16];
  undefined auVar7 [16];
  undefined auVar8 [16];
  undefined auVar9 [16];
  undefined auVar10 [16];
  undefined auVar11 [16];
  uint uVar12;
  undefined auVar13 [16];
  undefined8 uVar14;
  undefined auVar15 [8];
  undefined4 uVar16;
  undefined4 uVar17;
  int iVar18;
  uint uVar19;
  uint uVar20;
  long *plVar21;
  long *plVar22;
  long lVar23;
  int *piVar24;
  long lVar25;
  undefined8 uVar26;
  char cVar27;
  long lVar28;
  int *piVar29;
  ulong uVar30;
  int iVar31;
  undefined *puVar32;
  undefined *puVar33;
  ulong uVar34;
  int *piVar35;
  int *piVar36;
  undefined8 *puVar37;
  undefined8 *puVar38;
  uint uVar39;
  undefined *puVar40;
  long **pplVar41;
  long *in_FS_OFFSET;
  byte bVar42;
  uint uVar43;
  uint uVar45;
  undefined auVar44 [16];
  undefined auVar46 [16];
  uint uVar47;
  uint uVar49;
  undefined auVar48 [16];
  uint uVar50;
  uint uVar51;
  uint uVar52;
  int *local_688;
  int local_680;
  uint *local_670;
  uint local_668;
  uint local_664;
  int local_64c;
  int local_62c;
  undefined local_628 [16];
  int *local_618;
  undefined local_608 [8];
  int *piStack_600;
  int *local_5f8;
  long *local_5f0;
  long *local_5e8 [2];
  long local_5d8 [2];
  int local_5c8;
  uint auStack_5c4 [8];
  undefined8 local_5a4;
  undefined8 local_59c;
  int local_594 [5];
  int local_580;
  int local_528 [4];
  undefined local_518 [44];
  int local_4ec [8];
  int local_4cc;
  int local_474;
  int local_404 [100];
  int local_274 [100];
  uint local_e4;
  undefined4 local_e0;
  long local_d8;
  long local_cc [16];
  undefined8 local_4c;
  long local_40 [2];
  
  bVar42 = 0;
  local_40[0] = in_FS_OFFSET[5];
  local_64c = 0x1000;
LAB_0001e210:
  local_688 = &local_5c8;
  for (lVar28 = 0xb0; lVar28 != 0; lVar28 = lVar28 + -1) {
    local_688[0] = 0;
    local_688[1] = 0;
    local_688 = local_688 + ((ulong)bVar42 * -2 + 1) * 2;
  }
  local_e0 = 2;
  local_d8 = DAT_000e2df8;
  *local_688 = 0;
  plVar21 = local_cc;
  do {
    *(undefined4 *)plVar21 = 2;
    plVar22 = (long *)((long)plVar21 + 0x14);
    plVar21[1] = DAT_000e2df8;
    plVar21 = plVar22;
  } while (local_40 != plVar22);
  local_5c8 = param_2;
  cVar27 = *(char *)(param_3 + 1);
  if (param_2 == 0) {
    piVar29 = local_594;
    lVar28 = 0;
    do {
      lVar23 = (long)(int)(((int)lVar28 + 1U) % 10);
      if (cVar27 == '\0') {
        uVar34 = *param_3 + 0x9e3779b97f4a7c15;
        *param_3 = uVar34;
        uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
        uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
        uVar34 = uVar34 >> 0x1f ^ uVar34;
      }
      else {
        lVar25 = *in_FS_OFFSET;
        if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
          FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001f2c5 to 0001f2c9 has its CatchHandler @ 0001f771 */
          FUN_000ae640(lVar25 + -0x1398,local_5e8);
          FUN_000b07c0(local_5e8);
          *(undefined *)(in_FS_OFFSET + -0x274) = 1;
          FUN_000409c0(FUN_0001a6e0,lVar25 + -0x1398,&PTR_LOOP_00123008);
        }
        uVar16 = FUN_000aea50(lVar25 + -0x1398);
        uVar17 = FUN_000aea50(lVar25 + -0x1398);
        uVar34 = CONCAT44(uVar16,uVar17);
        cVar27 = *(char *)(param_3 + 1);
      }
      auVar9._8_8_ = 0;
      auVar9._0_8_ = uVar34;
      iVar18 = ((int)uVar34 -
               ((int)(uVar34 / 3) + (SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar9,8) & 0xfffffffe)))
               + 1;
      local_594[lVar23 * 10 + lVar28] = iVar18;
      lVar28 = lVar28 + 1;
      piVar29[lVar23] = iVar18;
      piVar29 = piVar29 + 10;
    } while (lVar28 != 10);
  }
  else if (param_2 == 1) {
    iVar18 = 0;
    puVar40 = local_518;
    while( true ) {
      puVar32 = puVar40 + -0xb0;
      do {
        if (cVar27 == '\0') {
          uVar34 = *param_3 + 0x9e3779b97f4a7c15;
          *param_3 = uVar34;
          uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
          uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
          uVar34 = uVar34 >> 0x1f ^ uVar34;
        }
        else {
          lVar28 = *in_FS_OFFSET;
          if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
            FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001f51d to 0001f521 has its CatchHandler @ 0001f773 */
            FUN_000ae640(lVar28 + -0x1398,local_5e8);
            FUN_000b07c0(local_5e8);
            *(undefined *)(in_FS_OFFSET + -0x274) = 1;
            FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
          }
          uVar16 = FUN_000aea50(lVar28 + -0x1398);
          uVar17 = FUN_000aea50(lVar28 + -0x1398);
          uVar34 = CONCAT44(uVar16,uVar17);
          cVar27 = *(char *)(param_3 + 1);
        }
        local_688 = &local_5c8;
        puVar33 = puVar32 + 0x2c;
        auVar10._8_8_ = 0;
        auVar10._0_8_ = uVar34;
        iVar31 = ((int)uVar34 -
                 ((SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar10,8) & 0xfffffffe) + (int)(uVar34 / 3)
                 )) + 1;
        *(int *)(puVar32 + 0x5c) = iVar31;
        *(int *)(puVar32 + 0x38) = iVar31;
        puVar32 = puVar33;
      } while (puVar40 != puVar33);
      puVar40 = puVar40 + 0xdc;
      if (iVar18 == 5) break;
      iVar18 = 5;
    }
    do {
      if (cVar27 == '\0') {
        uVar34 = *param_3 + 0x9e3779b97f4a7c15;
        *param_3 = uVar34;
        uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
        uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
        uVar34 = uVar34 >> 0x1f ^ uVar34;
      }
      else {
        lVar28 = *in_FS_OFFSET;
        if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
          FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001f662 to 0001f666 has its CatchHandler @ 0001f777 */
          FUN_000ae640(lVar28 + -0x1398,local_5e8);
          FUN_000b07c0(local_5e8);
          *(undefined *)(in_FS_OFFSET + -0x274) = 1;
          FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
        }
        uVar16 = FUN_000aea50(lVar28 + -0x1398);
        uVar17 = FUN_000aea50(lVar28 + -0x1398);
        uVar34 = CONCAT44(uVar16,uVar17);
        cVar27 = *(char *)(param_3 + 1);
      }
      piVar29 = local_688 + 0xb;
      auVar11._8_8_ = 0;
      auVar11._0_8_ = uVar34;
      iVar18 = ((int)uVar34 -
               ((SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar11,8) & 0xfffffffe) + (int)(uVar34 / 3)))
               + 1;
      local_688[0x3f] = iVar18;
      local_688[0x12] = iVar18;
      local_688 = piVar29;
    } while (piVar29 != local_4ec);
  }
  else if (param_2 == 2) {
    pplVar41 = &local_5f0;
    local_5f0 = DAT_000e2e78;
    do {
      iVar18 = *(int *)pplVar41;
      lVar28 = (long)iVar18;
      uVar39 = 0;
      piVar29 = local_594 + lVar28 * 10;
      do {
        uVar39 = uVar39 + 1;
        if (*(char *)(param_3 + 1) == '\0') {
          uVar34 = *param_3 + 0x9e3779b97f4a7c15;
          *param_3 = uVar34;
          uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
          uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
          uVar34 = uVar34 >> 0x1f ^ uVar34;
        }
        else {
          lVar23 = *in_FS_OFFSET;
          if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
            FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001f157 to 0001f15b has its CatchHandler @ 0001f76f */
            FUN_000ae640(lVar23 + -0x1398,local_5e8);
            FUN_000b07c0(local_5e8);
            *(undefined *)(in_FS_OFFSET + -0x274) = 1;
            FUN_000409c0(FUN_0001a6e0,lVar23 + -0x1398,&PTR_LOOP_00123008);
          }
          uVar16 = FUN_000aea50(lVar23 + -0x1398);
          uVar17 = FUN_000aea50(lVar23 + -0x1398);
          uVar34 = CONCAT44(uVar16,uVar17);
        }
        auVar7._8_8_ = 0;
        auVar7._0_8_ = uVar34;
        lVar23 = (long)(int)(uVar39 % 5 + iVar18);
        iVar31 = ((int)uVar34 -
                 ((SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar7,8) & 0xfffffffe) + (int)(uVar34 / 3))
                 ) + 1;
        local_594[lVar23 * 10 + lVar28] = iVar31;
        lVar28 = lVar28 + 1;
        piVar29[lVar23] = iVar31;
        piVar29 = piVar29 + 10;
      } while (uVar39 != 5);
      pplVar41 = (long **)((long)pplVar41 + 4);
    } while (pplVar41 != local_5e8);
    if (*(char *)(param_3 + 1) == '\0') {
      uVar34 = *param_3 + 0x9e3779b97f4a7c15;
      *param_3 = uVar34;
      uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
      uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
      uVar34 = uVar34 >> 0x1f ^ uVar34;
      cVar27 = '\0';
    }
    else {
      lVar28 = *in_FS_OFFSET;
      if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
        FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001f6b0 to 0001f6b4 has its CatchHandler @ 0001f779 */
        FUN_000ae640(lVar28 + -0x1398,local_5e8);
        FUN_000b07c0(local_5e8);
        *(undefined *)(in_FS_OFFSET + -0x274) = 1;
        FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
      }
      uVar16 = FUN_000aea50(lVar28 + -0x1398);
      uVar17 = FUN_000aea50(lVar28 + -0x1398);
      uVar34 = CONCAT44(uVar16,uVar17);
      cVar27 = *(char *)(param_3 + 1);
    }
    auVar8._8_8_ = 0;
    auVar8._0_8_ = uVar34;
    local_474 = ((int)uVar34 -
                ((SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar8,8) & 0xfffffffe) + (int)(uVar34 / 3)))
                + 1;
    local_528[0] = local_474;
  }
  else {
    piVar29 = &local_5c8;
    piVar35 = &local_5c8;
    do {
      if (cVar27 == '\0') {
        uVar34 = *param_3 + 0x9e3779b97f4a7c15;
        *param_3 = uVar34;
        uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
        uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
        uVar34 = uVar34 >> 0x1f ^ uVar34;
      }
      else {
        lVar28 = *in_FS_OFFSET;
        if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
          FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001ef0b to 0001ef0f has its CatchHandler @ 0001f73c */
          FUN_000ae640(lVar28 + -0x1398,local_5e8);
          FUN_000b07c0(local_5e8);
          *(undefined *)(in_FS_OFFSET + -0x274) = 1;
          FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
        }
        uVar16 = FUN_000aea50(lVar28 + -0x1398);
        uVar17 = FUN_000aea50(lVar28 + -0x1398);
        uVar34 = CONCAT44(uVar16,uVar17);
        cVar27 = *(char *)(param_3 + 1);
      }
      local_688 = &local_5c8;
      piVar24 = piVar29 + 10;
      auVar4._8_8_ = 0;
      auVar4._0_8_ = uVar34;
      iVar18 = ((int)uVar34 -
               ((SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar4,8) & 0xfffffffe) + (int)(uVar34 / 3)))
               + 1;
      piVar29[0x17] = iVar18;
      piVar35[0xe] = iVar18;
      piVar29 = piVar24;
      piVar36 = local_688;
      piVar35 = piVar35 + 1;
    } while (piVar24 != local_528);
    do {
      if (cVar27 == '\0') {
        uVar34 = *param_3 + 0x9e3779b97f4a7c15;
        *param_3 = uVar34;
        uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
        uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
        uVar34 = uVar34 >> 0x1f ^ uVar34;
      }
      else {
        lVar28 = *in_FS_OFFSET;
        if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
          FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001eeb5 to 0001eeb9 has its CatchHandler @ 0001f741 */
          FUN_000ae640(lVar28 + -0x1398,local_5e8);
          FUN_000b07c0(local_5e8);
          *(undefined *)(in_FS_OFFSET + -0x274) = 1;
          FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
        }
        uVar16 = FUN_000aea50(lVar28 + -0x1398);
        uVar17 = FUN_000aea50(lVar28 + -0x1398);
        uVar34 = CONCAT44(uVar16,uVar17);
        cVar27 = *(char *)(param_3 + 1);
      }
      piVar29 = local_688 + 10;
      auVar5._8_8_ = 0;
      auVar5._0_8_ = uVar34;
      iVar18 = ((int)uVar34 -
               ((SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar5,8) & 0xfffffffe) + (int)(uVar34 / 3)))
               + 1;
      local_688[0x4e] = iVar18;
      piVar36[0x45] = iVar18;
      local_688 = piVar29;
      piVar36 = piVar36 + 1;
    } while (piVar29 != local_528);
    if (cVar27 == '\0') {
      uVar34 = *param_3 + 0x9e3779b97f4a7c15;
      *param_3 = uVar34;
      uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
      uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
      uVar34 = uVar34 >> 0x1f ^ uVar34;
      cVar27 = '\0';
    }
    else {
      lVar28 = *in_FS_OFFSET;
      if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
        FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001f3bc to 0001f3c0 has its CatchHandler @ 0001f775 */
        FUN_000ae640(lVar28 + -0x1398,local_5e8);
        FUN_000b07c0(local_5e8);
        *(undefined *)(in_FS_OFFSET + -0x274) = 1;
        FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
      }
      uVar16 = FUN_000aea50(lVar28 + -0x1398);
      uVar17 = FUN_000aea50(lVar28 + -0x1398);
      uVar34 = CONCAT44(uVar16,uVar17);
      cVar27 = *(char *)(param_3 + 1);
    }
    auVar6._8_8_ = 0;
    auVar6._0_8_ = uVar34;
    local_4cc = ((int)uVar34 -
                ((SUB164(ZEXT816(0xaaaaaaaaaaaaaaab) * auVar6,8) & 0xfffffffe) + (int)(uVar34 / 3)))
                + 1;
    local_580 = local_4cc;
  }
  uVar39 = 0;
  piVar29 = local_594;
  do {
    lVar28 = 0;
    uVar19 = (uint)DAT_000e2df0;
    uVar50 = DAT_000e2df0._4_4_;
    do {
      local_688 = &local_5c8;
      uVar20 = *(uint *)((long)piVar29 + lVar28);
      uVar12 = ((uint *)((long)piVar29 + lVar28))[1];
      uVar51 = -(uint)(uVar19 == uVar39);
      uVar52 = -(uint)(uVar50 == uVar39);
      uVar47 = -(uint)(uVar20 == 0);
      uVar49 = -(uint)(uVar12 == 0);
      uVar43 = -(uint)(uVar47 == 0 && uVar51 == 0);
      uVar45 = -(uint)(uVar49 == 0 && uVar52 == 0);
      puVar1 = (uint *)((long)piVar29 + lVar28 + 400);
      *puVar1 = uVar20 & uVar43 |
                ~uVar43 & ~(~-(uint)(uVar51 == 0 && uVar20 == 0) & uVar51) & (uint)DAT_000e2e08;
      puVar1[1] = uVar12 & uVar45 |
                  ~uVar45 & ~(~-(uint)(uVar52 == 0 && uVar12 == 0) & uVar52) & DAT_000e2e08._4_4_;
      puVar1 = (uint *)((long)piVar29 + lVar28 + 800);
      *puVar1 = ~uVar47 & uVar19 | uVar47;
      puVar1[1] = ~uVar49 & uVar50 | uVar49;
      lVar28 = lVar28 + 8;
      uVar19 = uVar19 + (int)DAT_000e2e00;
      uVar50 = uVar50 + DAT_000e2e00._4_4_;
    } while (lVar28 != 0x28);
    uVar39 = uVar39 + 1;
    piVar29 = piVar29 + 10;
  } while (uVar39 != 10);
  piVar29 = local_404;
  piVar35 = piVar29;
  piVar36 = local_688;
  piVar24 = piVar29;
  do {
    do {
      lVar28 = 0;
      do {
        iVar18 = *(int *)((long)piVar24 + lVar28) + local_688[0x71];
        if (iVar18 < *(int *)((long)piVar35 + lVar28)) {
          *(int *)((long)piVar35 + lVar28) = iVar18;
          *(int *)((long)piVar35 + lVar28 + 400) = local_688[0xd5];
        }
        lVar28 = lVar28 + 4;
      } while (lVar28 != 0x28);
      piVar35 = piVar35 + 10;
      local_688 = local_688 + 10;
    } while (piVar35 != local_274);
    local_688 = piVar36 + 1;
    piVar24 = piVar24 + 10;
    piVar35 = piVar29;
    piVar36 = local_688;
  } while ((int *)((long)&local_5a4 + 4) != local_688);
  lVar28 = 1;
  iVar18 = -1;
  do {
    auVar46._8_8_ = 0;
    auVar46._0_8_ = local_59c;
    lVar23 = lVar28;
    iVar31 = iVar18;
    do {
      iVar2 = piVar29[lVar23];
      uVar16 = (undefined4)lVar23;
      iVar18 = iVar31;
      if (iVar31 < iVar2) {
        iVar18 = iVar2;
      }
      lVar23 = lVar23 + 1;
      auVar48._0_8_ = CONCAT44(-(uint)(iVar31 < iVar2),-(uint)(iVar31 < iVar2));
      auVar48._8_8_ = 0;
      auVar44._8_8_ = 0;
      auVar44._0_8_ = CONCAT44(uVar16,(int)lVar28 + -1) & auVar48._0_8_;
      auVar46 = ~auVar48 & auVar46 | auVar44;
      local_59c = auVar46._0_8_;
      iVar31 = iVar18;
    } while ((int)lVar23 != 10);
    lVar28 = lVar28 + 1;
    piVar29 = piVar29 + 10;
  } while (lVar28 != 10);
  if (cVar27 == '\0') {
    uVar34 = *param_3 + 0x9e3779b97f4a7c15;
    *param_3 = uVar34;
    uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
    uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
    uVar34 = uVar34 >> 0x1f ^ uVar34;
  }
  else {
    lVar28 = *in_FS_OFFSET;
    if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
      FUN_00018b10(local_5e8,"default");
                    /* try { // try from 0001f31b to 0001f31f has its CatchHandler @ 0001f76d */
      FUN_000ae640(lVar28 + -0x1398,local_5e8);
      FUN_000b07c0(local_5e8);
      *(undefined *)(in_FS_OFFSET + -0x274) = 1;
      FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
    }
    FUN_000aea50(lVar28 + -0x1398);
    uVar39 = FUN_000aea50(lVar28 + -0x1398);
    uVar34 = (ulong)uVar39;
  }
  if ((uVar34 & 1) != 0) {
    local_59c = CONCAT44(auVar46._0_4_,auVar46._4_4_);
  }
  iVar31 = 0;
  local_5a4 = 0xffffffffffffffff;
  iVar18 = (int)local_59c;
  local_618 = (int *)0x0;
  auVar13._12_4_ = 0;
  auVar13._0_12_ = stack0xfffffffffffff9fc;
  _local_608 = auVar13 << 0x20;
  auStack_5c4[0] = 0xffffffff;
  auStack_5c4[1] = 0xffffffff;
  auStack_5c4[2] = 0xffffffff;
  auStack_5c4[3] = 0xffffffff;
  auStack_5c4[4] = 0xffffffff;
  auStack_5c4[5] = 0xffffffff;
  auStack_5c4[6] = 0xffffffff;
  auStack_5c4[7] = 0xffffffff;
  local_628 = (undefined  [16])0x0;
  do {
    if ((iVar31 != iVar18) && (local_59c._4_4_ != iVar31)) {
      if ((int *)local_628._8_8_ == local_618) {
                    /* try { // try from 0001edcb to 0001edcf has its CatchHandler @ 0001f737 */
        FUN_0001e040(local_628,local_628._8_8_,local_608);
      }
      else {
        *(int *)local_628._8_8_ = iVar31;
        local_628._8_8_ = (int *)(local_628._8_8_ + 4);
      }
    }
    iVar31 = iVar31 + 1;
    local_608._0_4_ = iVar31;
  } while (iVar31 != 10);
  uVar34 = 8;
  do {
    if (*(char *)(param_3 + 1) == '\0') {
      uVar30 = *param_3 + 0x9e3779b97f4a7c15;
      *param_3 = uVar30;
      uVar30 = (uVar30 >> 0x1e ^ uVar30) * -0x40a7b892e31b1a47;
      uVar30 = (uVar30 >> 0x1b ^ uVar30) * -0x6b2fb644ecceee15;
      uVar30 = uVar30 >> 0x1f ^ uVar30;
    }
    else {
      lVar28 = *in_FS_OFFSET;
      if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
        FUN_00018b10(local_5e8,"default");
        lVar28 = *in_FS_OFFSET;
                    /* try { // try from 0001e89a to 0001e89e has its CatchHandler @ 0001f6ea */
        FUN_000ae640(lVar28 + -0x1398,local_5e8);
        if (local_5e8[0] != local_5d8) {
          thunk_FUN_000d36e0(local_5e8[0],local_5d8[0] + 1);
        }
        *(undefined *)(in_FS_OFFSET + -0x274) = 1;
        FUN_000409c0(FUN_0001a6e0,lVar28 + -0x1398,&PTR_LOOP_00123008);
      }
                    /* try { // try from 0001e7c6 to 0001e886 has its CatchHandler @ 0001f737 */
      lVar23 = FUN_000aea50(lVar28 + -0x1398);
      uVar39 = FUN_000aea50(lVar28 + -0x1398);
      uVar30 = (ulong)uVar39 ^ lVar23 << 0x20;
    }
    uVar26 = local_628._0_8_;
    uVar30 = uVar30 % uVar34;
    lVar28 = uVar34 - 1;
    uVar34 = uVar34 - 1;
    iVar18 = *(int *)(local_628._0_8_ + lVar28 * 4);
    *(int *)(local_628._0_8_ + lVar28 * 4) = *(int *)(local_628._0_8_ + uVar30 * 4);
    *(int *)(local_628._0_8_ + uVar30 * 4) = iVar18;
  } while (uVar34 != 1);
  uVar34 = 0;
  while( true ) {
    for (; uVar34 < 3; uVar34 = uVar34 + 1) {
      auStack_5c4[*(int *)(local_628._0_8_ + uVar34 * 4)] = 0;
    }
    if (5 < uVar34) break;
    piVar29 = (int *)(local_628._0_8_ + uVar34 * 4);
    uVar34 = uVar34 + 1;
    auStack_5c4[*piVar29] = 1;
  }
  while (auStack_5c4[*(int *)(local_628._0_8_ + uVar34 * 4)] = 2, uVar34 != 7) {
    uVar34 = 7;
  }
  local_670 = &local_e4;
  local_664 = 0x18;
  uVar14 = local_628._8_8_;
  local_668 = 0;
  do {
    if ((int)local_668 < 4) {
      uVar19 = local_668 & 1;
      uVar50 = 2;
      uVar20 = 5;
      uVar39 = local_664;
    }
    else {
      uVar50 = 1;
      uVar19 = 2;
      uVar39 = local_664 - 0x30;
      if (0x50 < (int)uVar39) {
        uVar39 = 0x50;
      }
      uVar20 = 0xc;
    }
    local_5f8 = (int *)0x0;
    _local_608 = (undefined  [16])0x0;
    *local_670 = uVar19;
    local_670[1] = uVar50;
    local_670[3] = uVar20;
    local_670[4] = uVar39;
    if (uVar26 == uVar14) goto LAB_0001eded;
    piVar35 = (int *)0x0;
    piVar29 = (int *)uVar26;
    do {
      while( true ) {
        local_62c = *piVar29;
        if (uVar19 != 2) break;
        if (auStack_5c4[local_62c] != 2) goto LAB_0001e9e2;
joined_r0x0001eccf:
        piVar29 = piVar29 + 1;
        if ((int *)uVar14 == piVar29) goto LAB_0001eab3;
      }
      if (auStack_5c4[local_62c] != uVar19) {
LAB_0001e9e2:
        piVar36 = (int *)&local_59c;
        bVar3 = true;
        do {
          if (uVar19 == 2) {
            iVar18 = 100000;
            piVar24 = (int *)uVar26;
            do {
              lVar28 = (long)*piVar24;
              if ((auStack_5c4[lVar28] == 2) &&
                 (iVar31 = local_404[(long)*piVar36 * 10 + lVar28] * 3 + 0xe +
                           local_404[lVar28 * 10 + (long)local_62c], iVar31 < iVar18)) {
                iVar18 = iVar31;
              }
              piVar24 = piVar24 + 1;
            } while ((int *)uVar14 != piVar24);
          }
          else {
            iVar18 = local_404[(long)*piVar36 * 10 + (long)local_62c] + 2;
          }
          if (bVar3) {
            bVar3 = iVar18 <= (int)uVar39;
          }
          piVar36 = piVar36 + 1;
        } while (local_594 != piVar36);
        if (bVar3) {
          if (local_5f8 == piVar35) {
            FUN_0001e040(local_608,piVar35,&local_62c);
            piVar35 = piStack_600;
          }
          else {
            *piVar35 = local_62c;
            piVar35 = piVar35 + 1;
            piStack_600 = piVar35;
          }
        }
        goto joined_r0x0001eccf;
      }
      piVar29 = piVar29 + 1;
    } while ((int *)uVar14 != piVar29);
LAB_0001eab3:
    auVar15 = local_608;
    if ((undefined  [8])piVar35 == local_608) break;
    lVar28 = (long)piVar35 - (long)local_608;
    if (*(char *)(param_3 + 1) == '\0') {
      uVar34 = *param_3 + 0x9e3779b97f4a7c15;
      *param_3 = uVar34;
      uVar34 = (uVar34 >> 0x1e ^ uVar34) * -0x40a7b892e31b1a47;
      uVar34 = (uVar34 >> 0x1b ^ uVar34) * -0x6b2fb644ecceee15;
      uVar34 = uVar34 >> 0x1f ^ uVar34;
    }
    else {
      lVar23 = *in_FS_OFFSET;
      if (*(char *)(in_FS_OFFSET + -0x274) == '\0') {
        FUN_00018b10(local_5e8,"default");
        lVar23 = *in_FS_OFFSET;
                    /* try { // try from 0001ed11 to 0001ed15 has its CatchHandler @ 0001f768 */
        FUN_000ae640(lVar23 + -0x1398,local_5e8);
        if (local_5e8[0] != local_5d8) {
          thunk_FUN_000d36e0(local_5e8[0],local_5d8[0] + 1);
        }
        *(undefined *)(in_FS_OFFSET + -0x274) = 1;
        FUN_000409c0(FUN_0001a6e0,lVar23 + -0x1398,&PTR_LOOP_00123008);
      }
                    /* try { // try from 0001eb0b to 0001ecfd has its CatchHandler @ 0001f6ef */
      lVar25 = FUN_000aea50(lVar23 + -0x1398);
      uVar39 = FUN_000aea50(lVar23 + -0x1398);
      uVar34 = (ulong)uVar39 ^ lVar25 << 0x20;
    }
    local_680 = (int)(lVar28 >> 2);
    local_670[2] = *(uint *)((long)auVar15 + (long)(int)(uVar34 % (ulong)(long)local_680) * 4);
    if (auVar15 != (undefined  [8])0x0) {
      thunk_FUN_000d36e0(auVar15,(long)local_5f8 - (long)auVar15);
    }
    local_668 = local_668 + 1;
    local_670 = local_670 + 5;
    local_664 = local_664 + 0x10;
    if (local_668 == 8) {
      *param_1 = CONCAT44(auStack_5c4[0],local_5c8);
      *(undefined8 *)((long)param_1 + 0x57c) = local_4c;
      lVar28 = (long)param_1 - (long)((ulong)(param_1 + 1) & 0xfffffffffffffff8);
      puVar37 = (undefined8 *)((long)&local_5c8 - lVar28);
      puVar38 = (undefined8 *)((ulong)(param_1 + 1) & 0xfffffffffffffff8);
      for (uVar34 = (ulong)((int)lVar28 + 0x584U >> 3); uVar34 != 0; uVar34 = uVar34 - 1) {
        *puVar38 = *puVar37;
        puVar37 = puVar37 + (ulong)bVar42 * -2 + 1;
        puVar38 = puVar38 + (ulong)bVar42 * -2 + 1;
      }
      thunk_FUN_000d36e0(uVar26,(long)local_618 - uVar26);
      if (local_40[0] == in_FS_OFFSET[5]) {
        return param_1;
      }
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
  } while( true );
  if (piVar35 != (int *)0x0) {
    thunk_FUN_000d36e0(piVar35,(long)local_5f8 - (long)piVar35);
  }
LAB_0001eded:
  thunk_FUN_000d36e0(uVar26,(long)local_618 - uVar26);
  local_64c = local_64c + -1;
  if (local_64c == 0) {
    uVar26 = FUN_00040f40(0x10);
                    /* try { // try from 0001ee1f to 0001ee23 has its CatchHandler @ 0001f743 */
    FUN_00053220(uVar26,"map generation exhausted feasible candidates");
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar26,&PTR_PTR_FUN_0011d470,FUN_00049930);
  }
  goto LAB_0001e210;
}


