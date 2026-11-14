// ===== FUNC 32dc0 size=1974

void FUN_00032dc0(undefined *param_1,int *param_2)

{
  undefined uVar1;
  int iVar2;
  undefined8 uVar3;
  undefined (*pauVar4) [16];
  undefined *puVar5;
  ulong uVar6;
  qword *pqVar7;
  long lVar8;
  undefined *puVar9;
  int *piVar10;
  long *plVar11;
  int *piVar13;
  long lVar14;
  long in_FS_OFFSET;
  undefined local_1b9;
  undefined *local_1b8;
  undefined (*local_1b0) [16];
  undefined local_1a8 [8];
  undefined8 local_1a0;
  undefined8 local_198;
  undefined local_190;
  long local_188;
  undefined8 local_180;
  undefined local_178 [8];
  undefined8 local_170;
  undefined8 local_168;
  undefined local_160;
  undefined (*local_158) [16];
  undefined8 local_150;
  undefined local_148 [8];
  undefined8 local_140;
  undefined8 local_138;
  undefined local_130;
  undefined (*local_128) [16];
  undefined8 local_120;
  undefined local_118 [8];
  undefined8 local_110;
  undefined8 local_108;
  undefined local_100 [8];
  undefined local_f8 [8];
  undefined8 local_f0;
  undefined local_e8 [8];
  undefined (*local_e0) [16];
  undefined8 local_d8;
  undefined local_d0;
  undefined (*local_c8) [16];
  undefined8 local_c0;
  long local_b8 [2];
  undefined8 local_a8;
  undefined local_a0 [16];
  undefined8 local_90;
  undefined local_88 [16];
  undefined8 local_78;
  undefined local_70 [16];
  undefined8 local_60;
  undefined local_58 [16];
  undefined8 local_48;
  long local_40 [2];
  long *plVar12;
  
  local_40[0] = *(long *)(in_FS_OFFSET + 0x28);
  local_1a8[0] = 0;
  local_1a0 = 0;
                    /* try { // try from 00032e12 to 00032e28 has its CatchHandler @ 00033a28 */
  FUN_00024620(&local_1a0,0);
  local_1a8[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00032e36 to 00032e3a has its CatchHandler @ 000338f6 */
  FUN_00018b10(uVar3,"topology");
  local_188 = (long)*param_2;
  local_198 = 0;
  local_190 = 5;
  local_180 = 0;
  local_1a0 = uVar3;
                    /* try { // try from 00032e96 to 00032e9a has its CatchHandler @ 000338b6 */
  FUN_0002fd20(local_b8,local_1a8,2,1,2);
  local_a8 = 0;
  local_178[0] = 0;
  local_170 = 0;
                    /* try { // try from 00032ecd to 00032ee3 has its CatchHandler @ 00033581 */
  FUN_00024620(&local_170,0);
  local_178[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00032ef1 to 00032ef5 has its CatchHandler @ 00033a5c */
  FUN_00018b10(uVar3,"roles");
  local_168 = 0;
  local_160 = 0;
  local_158 = (undefined (*) [16])0x0;
  local_170 = uVar3;
                    /* try { // try from 00032f30 to 00032f4e has its CatchHandler @ 000338a9 */
  FUN_00024620(&local_158,0);
  local_160 = 2;
  piVar13 = param_2 + 0xb;
  piVar10 = param_2 + 1;
  pauVar4 = (undefined (*) [16])FUN_00041fe0(0x18);
  *(undefined8 *)pauVar4[1] = 0;
  *pauVar4 = (undefined  [16])0x0;
  lVar8 = (long)piVar13 - (long)piVar10 >> 2;
  local_1b8 = &local_1b9;
  local_1b0 = pauVar4;
  if (0x1ffffffffffffffc < (ulong)((long)piVar13 - (long)piVar10)) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00033570 to 00033574 has its CatchHandler @ 00033586 */
    FUN_00015e26("cannot create std::vector larger than max_size()");
  }
  lVar14 = lVar8 * 0x10;
  if (lVar8 == 0) {
    puVar5 = (undefined *)0x0;
  }
  else {
                    /* try { // try from 00032fa3 to 00032fa7 has its CatchHandler @ 00033586 */
    puVar5 = (undefined *)FUN_00041fe0(lVar14);
  }
  *(undefined **)*pauVar4 = puVar5;
  *(undefined **)pauVar4[1] = puVar5 + lVar14;
  puVar9 = puVar5;
  if (piVar13 != piVar10) {
    do {
      iVar2 = *piVar10;
      piVar10 = piVar10 + 1;
      *puVar9 = 5;
      *(long *)(puVar9 + 8) = (long)iVar2;
      puVar9 = puVar9 + 0x10;
    } while (piVar13 != piVar10);
    puVar5 = puVar5 + 0xa0;
  }
  *(undefined **)(*pauVar4 + 8) = puVar5;
  local_150 = 0;
  local_158 = pauVar4;
                    /* try { // try from 0003301d to 00033021 has its CatchHandler @ 00033676 */
  FUN_0002fd20(local_a0,local_178,2,1,2);
  local_90 = 0;
  local_148[0] = 0;
  local_140 = 0;
                    /* try { // try from 0003304f to 00033065 has its CatchHandler @ 0003367b */
  FUN_00024620(&local_140,0);
  local_148[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00033073 to 00033077 has its CatchHandler @ 00033750 */
  FUN_00018b10(uVar3,"homes");
  local_138 = 0;
  local_130 = 0;
  local_128 = (undefined (*) [16])0x0;
  local_140 = uVar3;
                    /* try { // try from 000330b2 to 000330cc has its CatchHandler @ 00033a35 */
  FUN_00024620(&local_128,0);
  local_130 = 2;
  pauVar4 = (undefined (*) [16])FUN_00041fe0(0x18);
  *(undefined8 *)pauVar4[1] = 0;
  *pauVar4 = (undefined  [16])0x0;
  uVar6 = (long)(param_2 + 0xd) - (long)piVar13;
  lVar8 = (long)uVar6 >> 2;
  local_1b0 = pauVar4;
  if (uVar6 < 0x1ffffffffffffffd) {
    lVar14 = lVar8 * 0x10;
    if (lVar8 == 0) {
      pqVar7 = &Elf64_Ehdr_00000000.e_phoff;
      puVar5 = (undefined *)0x0;
      local_1b8 = &local_1b9;
    }
    else {
      local_1b8 = &local_1b9;
                    /* try { // try from 0003311c to 00033120 has its CatchHandler @ 000339d9 */
      puVar5 = (undefined *)FUN_00041fe0(lVar14);
      pqVar7 = (qword *)(puVar5 + 0x20);
    }
    iVar2 = param_2[0xb];
    *(undefined **)*pauVar4 = puVar5;
    *puVar5 = 5;
    *(long *)(puVar5 + 8) = (long)iVar2;
    iVar2 = param_2[0xc];
    puVar5[0x10] = 5;
    *(long *)(puVar5 + 0x18) = (long)iVar2;
    *(qword **)(*pauVar4 + 8) = pqVar7;
    *(undefined **)pauVar4[1] = puVar5 + lVar14;
    local_120 = 0;
    local_128 = pauVar4;
                    /* try { // try from 00033186 to 0003318a has its CatchHandler @ 00033a30 */
    FUN_0002fd20(local_88,local_148,2,1,2);
    local_78 = 0;
    local_118[0] = 0;
    local_110 = 0;
                    /* try { // try from 000331bd to 000331d3 has its CatchHandler @ 00033970 */
    FUN_00024620(&local_110,0);
    local_118[0] = 3;
    uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 000331e1 to 000331e5 has its CatchHandler @ 000339b3 */
    FUN_00018b10(uVar3,"routes");
    local_108 = 0;
    local_110 = uVar3;
                    /* try { // try from 00033205 to 00033209 has its CatchHandler @ 000339b8 */
    FUN_00032290(local_100,param_2 + 0xd);
    local_f0 = 0;
                    /* try { // try from 0003323e to 00033242 has its CatchHandler @ 000339d4 */
    FUN_0002fd20(local_70,local_118,2,1,2);
    local_60 = 0;
    local_e8[0] = 0;
    local_e0 = (undefined (*) [16])0x0;
                    /* try { // try from 00033275 to 0003328b has its CatchHandler @ 000338fb */
    FUN_00024620(&local_e0,0);
    local_e8[0] = 3;
    pauVar4 = (undefined (*) [16])FUN_00041fe0(0x20);
    local_1b8 = &local_1b9;
    local_1b0 = pauVar4;
                    /* try { // try from 000332a3 to 000332a7 has its CatchHandler @ 0003396b */
    FUN_00018b10(pauVar4,"contracts");
    local_d8 = 0;
    local_d0 = 0;
    local_c8 = (undefined (*) [16])0x0;
    local_e0 = pauVar4;
                    /* try { // try from 000332e2 to 00033306 has its CatchHandler @ 00033a64 */
    FUN_00024620(&local_c8,0);
    local_d0 = 2;
    piVar13 = param_2 + 0x139;
    pauVar4 = (undefined (*) [16])FUN_00041fe0(0x18);
    *(undefined8 *)pauVar4[1] = 0;
    lVar14 = (long)(param_2 + 0x161) - (long)piVar13;
    *pauVar4 = (undefined  [16])0x0;
    lVar8 = lVar14 >> 2;
    if (-1 < lVar14) {
      lVar14 = lVar8 * -0x3333333333333330;
      if (lVar8 * -0x3333333333333333 == 0) {
        puVar5 = (undefined *)0x0;
      }
      else {
                    /* try { // try from 00033350 to 00033354 has its CatchHandler @ 00033758 */
        puVar5 = (undefined *)FUN_00041fe0(lVar14);
      }
      *(undefined **)*pauVar4 = puVar5;
      *(undefined **)pauVar4[1] = puVar5 + lVar14;
      for (; param_2 + 0x161 != piVar13; piVar13 = piVar13 + 5) {
        *puVar5 = 0;
        *(undefined8 *)(puVar5 + 8) = 0;
                    /* try { // try from 00033381 to 00033385 has its CatchHandler @ 0003382c */
        FUN_00030930(puVar5,piVar13);
        puVar5 = puVar5 + 0x10;
      }
      *(undefined **)(*pauVar4 + 8) = puVar5;
      local_c0 = 0;
      local_c8 = pauVar4;
                    /* try { // try from 000333ce to 000333d2 has its CatchHandler @ 00033831 */
      FUN_0002fd20(local_58,local_e8,2,1,2);
      local_48 = 0;
                    /* try { // try from 000333f8 to 000333fc has its CatchHandler @ 000338b1 */
      FUN_0002fd20(&local_1b8,local_b8,5,1,2);
      uVar1 = *param_1;
      *param_1 = local_1b8._0_1_;
      pauVar4 = *(undefined (**) [16])(param_1 + 8);
      *(undefined (**) [16])(param_1 + 8) = local_1b0;
      local_1b8 = (undefined *)CONCAT71(local_1b8._1_7_,uVar1);
      local_1b0 = pauVar4;
      FUN_00024620(&local_1b0);
      plVar11 = local_40;
      do {
        plVar12 = plVar11 + -3;
        FUN_00024620(plVar11 + -2,*(undefined *)plVar12);
        plVar11 = plVar12;
      } while (plVar12 != local_b8);
      FUN_00024620(&local_c8,local_d0);
      FUN_00024620(&local_e0,local_e8[0]);
      FUN_00024620(local_f8,local_100[0]);
      FUN_00024620(&local_110,local_118[0]);
      FUN_00024620(&local_128,local_130);
      FUN_00024620(&local_140,local_148[0]);
      FUN_00024620(&local_158,local_160);
      FUN_00024620(&local_170,local_178[0]);
      FUN_00024620(&local_188,local_190);
      FUN_00024620(&local_1a0,local_1a8[0]);
      if (local_40[0] == *(long *)(in_FS_OFFSET + 0x28)) {
        return;
      }
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003355f to 00033563 has its CatchHandler @ 00033758 */
    FUN_00015e26("cannot create std::vector larger than max_size()");
  }
  local_1b8 = &local_1b9;
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003357c to 00033580 has its CatchHandler @ 000339d9 */
  FUN_00015e26("cannot create std::vector larger than max_size()");
}


