// ===== FUNC 311e0 size=2668

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 * FUN_000311e0(undefined8 *param_1,undefined8 *param_2,int param_3)

{
  int iVar1;
  int *piVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  int *piVar5;
  long *plVar6;
  undefined8 uVar7;
  ulong uVar8;
  long lVar9;
  undefined4 uVar10;
  undefined8 *puVar11;
  long lVar12;
  undefined8 *puVar13;
  undefined *puVar14;
  long lVar16;
  long in_FS_OFFSET;
  byte bVar17;
  undefined *local_1f0;
  undefined local_1c8 [16];
  undefined8 local_1b8;
  undefined *local_1a8;
  long *plStack_1a0;
  undefined8 local_198;
  undefined local_188 [32];
  undefined local_168 [8];
  long *local_160;
  undefined8 local_158;
  undefined local_150;
  long local_148 [2];
  undefined local_138 [8];
  long *local_130;
  undefined8 local_128;
  undefined local_120;
  long local_118 [2];
  undefined local_108 [8];
  long *local_100;
  undefined8 local_f8;
  undefined local_f0;
  long local_e8 [2];
  undefined local_d8 [8];
  long *local_d0;
  undefined8 local_c8;
  undefined local_c0;
  long local_b8 [2];
  undefined local_a8 [16];
  undefined8 local_98;
  undefined local_90 [16];
  undefined8 local_80;
  undefined local_78 [16];
  undefined8 local_68;
  undefined local_60 [16];
  undefined8 local_50;
  undefined local_48 [8];
  long local_40;
  undefined *puVar15;
  
  bVar17 = 0;
  iVar1 = (int)param_1;
  puVar11 = (undefined8 *)((ulong)((long)param_1 + 0x1cc) & 0xfffffffffffffff8);
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  *(undefined (*) [16])((long)param_1 + 4) = (undefined  [16])0x0;
  *(undefined (*) [16])((long)param_1 + 0x14) = (undefined  [16])0x0;
  uVar3 = DAT_000e2e78;
  uVar7 = _DAT_000e2e70;
  *(undefined4 *)param_1 = 0;
  *(undefined8 *)((long)param_1 + 0x24) = 0;
  *(undefined8 *)((long)param_1 + 0x2c) = 0;
  *(undefined8 *)((long)param_1 + 0x34) = 0;
  *(undefined8 *)((long)param_1 + 0x1bc) = 0;
  puVar13 = (undefined8 *)((ulong)((long)param_1 + 0x3c) & 0xfffffffffffffff8);
  uVar8 = (ulong)((iVar1 - (int)puVar13) + 0x1c4U >> 3);
  for (; uVar8 != 0; uVar8 = uVar8 - 1) {
    *puVar13 = 0;
    puVar13 = puVar13 + 1;
  }
  *(undefined8 *)((long)param_1 + 0x1c4) = 0;
  *(undefined8 *)((long)param_1 + 0x34c) = 0;
  uVar8 = (ulong)((iVar1 - (int)puVar11) + 0x354U >> 3);
  for (; uVar8 != 0; uVar8 = uVar8 - 1) {
    *puVar11 = 0;
    puVar11 = puVar11 + 1;
  }
  *(undefined8 *)((long)param_1 + 0x354) = 0;
  *(undefined8 *)((long)param_1 + 0x4dc) = 0;
  puVar11 = (undefined8 *)((ulong)((long)param_1 + 0x35c) & 0xfffffffffffffff8);
  uVar8 = (ulong)((iVar1 - (int)puVar11) + 0x4e4U >> 3);
  for (; uVar8 != 0; uVar8 = uVar8 - 1) {
    *puVar11 = 0;
    puVar11 = puVar11 + 1;
  }
  *(undefined8 *)((long)param_1 + 0x4e4) = uVar7;
  *(undefined8 *)((long)param_1 + 0x4ec) = uVar3;
  *(undefined4 *)((long)param_1 + 0x4f4) = 0x18;
  puVar11 = param_1 + 0x9f;
  do {
    *(undefined4 *)(puVar11 + 2) = 0x18;
    puVar13 = (undefined8 *)((long)puVar11 + 0x14);
    *puVar11 = uVar7;
    puVar11[1] = uVar3;
    puVar11 = puVar13;
  } while ((undefined8 *)((long)param_1 + 0x584) != puVar13);
  *(undefined (*) [16])(param_1 + 0xb3) = (undefined  [16])0x0;
  param_1[0xb1] = 0;
  *(undefined4 *)(param_1 + 0xb2) = 0;
  param_1[0xb5] = 0;
  puVar11 = param_1 + 0xb6;
  for (lVar9 = 0xf; lVar9 != 0; lVar9 = lVar9 + -1) {
    *puVar11 = 0;
    puVar11 = puVar11 + 1;
  }
  *(undefined2 *)(param_1 + 0xc6) = 0;
  *(undefined2 *)((long)param_1 + 0x69c) = 0;
  param_1[0xc5] = 0;
  *(undefined8 *)((long)param_1 + 0x654) = 0;
  param_1[0xcc] = 0;
  *(undefined4 *)(param_1 + 0xcd) = 0;
  *(undefined8 *)((long)param_1 + 0x68c) = 0;
  *(undefined8 *)((long)param_1 + 0x694) = 0;
  *(undefined (*) [16])((long)param_1 + 0x634) = (undefined  [16])0x0;
  *(undefined (*) [16])((long)param_1 + 0x644) = (undefined  [16])0x0;
  *(undefined (*) [16])((long)param_1 + 0x66c) = (undefined  [16])0x0;
  *(undefined (*) [16])((long)param_1 + 0x67c) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0xd4) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0xd6) = (undefined  [16])0x0;
                    /* try { // try from 000313de to 000313e2 has its CatchHandler @ 00031d3b */
  FUN_0002fd20(param_1 + 0xd8,0,0,0,2);
  param_1[0xdc] = 0;
  lVar16 = (long)param_3;
  *(undefined (*) [16])(param_1 + 0xda) = (undefined  [16])0x0;
  puVar11 = param_2;
  puVar13 = param_1;
  for (lVar9 = 0xb0; lVar9 != 0; lVar9 = lVar9 + -1) {
    *puVar13 = *puVar11;
    puVar11 = puVar11 + (ulong)bVar17 * -2 + 1;
    puVar13 = puVar13 + (ulong)bVar17 * -2 + 1;
  }
  *(undefined4 *)puVar13 = *(undefined4 *)puVar11;
  puVar11 = param_2 + lVar16 * 0x1b + 0xb4;
  *(undefined4 *)(param_1 + 0xb1) = *(undefined4 *)(param_2 + lVar16 * 0x1b + 0xb2);
  *(undefined4 *)((long)param_1 + 0x58c) = *(undefined4 *)((long)param_2 + lVar16 * 0xd8 + 0x594);
  *(undefined4 *)(param_1 + 0xb2) = *(undefined4 *)(param_2 + lVar16 * 0x1b + 0xb3);
                    /* try { // try from 0003146c to 00031470 has its CatchHandler @ 00031d70 */
  FUN_00017ca0(param_1 + 0xb3,puVar11);
  uVar10 = *(undefined4 *)((long)param_2 + 0x584);
  uVar7 = param_2[lVar16 * 0x1b + 0xb8];
  param_1[0xb6] = param_2[lVar16 * 0x1b + 0xb7];
  param_1[0xb7] = uVar7;
  uVar7 = param_2[lVar16 * 0x1b + 0xba];
  param_1[0xb8] = param_2[lVar16 * 0x1b + 0xb9];
  param_1[0xb9] = uVar7;
  uVar7 = param_2[lVar16 * 0x1b + 0xbc];
  param_1[0xba] = param_2[lVar16 * 0x1b + 0xbb];
  param_1[0xbb] = uVar7;
  uVar7 = param_2[lVar16 * 0x1b + 0xbe];
  param_1[0xbc] = param_2[lVar16 * 0x1b + 0xbd];
  param_1[0xbd] = uVar7;
  uVar7 = param_2[lVar16 * 0x1b + 0xc0];
  param_1[0xbe] = param_2[lVar16 * 0x1b + 0xbf];
  param_1[0xbf] = uVar7;
  uVar7 = param_2[lVar16 * 0x1b + 0xc2];
  param_1[0xc0] = param_2[lVar16 * 0x1b + 0xc1];
  param_1[0xc1] = uVar7;
  uVar7 = param_2[lVar16 * 0x1b + 0xc4];
  param_1[0xc2] = param_2[lVar16 * 0x1b + 0xc3];
  param_1[0xc3] = uVar7;
  param_1[0xc4] = param_2[lVar16 * 0x1b + 0xc5];
  param_1[0xc5] = param_2[lVar16 * 0x1b + 0xc6];
  *(undefined2 *)(param_1 + 0xc6) = *(undefined2 *)(param_2 + lVar16 * 0x1b + 199);
  uVar7 = *(undefined8 *)((long)param_2 + lVar16 * 0xd8 + 0x644);
  *(undefined8 *)((long)param_1 + 0x634) = *(undefined8 *)((long)param_2 + lVar16 * 0xd8 + 0x63c);
  *(undefined8 *)((long)param_1 + 0x63c) = uVar7;
  uVar7 = *(undefined8 *)((long)param_2 + lVar16 * 0xd8 + 0x654);
  *(undefined8 *)((long)param_1 + 0x644) = *(undefined8 *)((long)param_2 + lVar16 * 0xd8 + 0x64c);
  *(undefined8 *)((long)param_1 + 0x64c) = uVar7;
  uVar7 = *(undefined8 *)((long)param_2 + lVar16 * 0xd8 + 0x65c);
  param_1[0xcc] = CONCAT44(param_3,uVar10);
  *(undefined8 *)((long)param_1 + 0x654) = uVar7;
  lVar12 = (long)(1 - param_3);
  *(undefined4 *)(param_1 + 0xcd) = *(undefined4 *)((long)param_2 + lVar12 * 0xd8 + 0x594);
  uVar7 = param_2[0xee];
  uVar3 = param_2[0xef];
  uVar4 = param_2[0xf0];
  iVar1 = *(int *)(param_2 + lVar16 * 0x1b + 0xb2);
  param_1[0xd4] = param_2[0xed];
  param_1[0xd5] = uVar7;
  param_1[0xd6] = uVar3;
  param_1[0xd7] = uVar4;
  *(undefined *)((long)param_1 + (long)iVar1 + 0x694) = 1;
  lVar9 = 0;
  do {
    if (*(char *)((long)param_2 + lVar9 + lVar16 * 0xd8 + 0x630) != '\0') {
      *(undefined *)((long)param_1 + lVar9 + 0x694) = 1;
    }
    lVar9 = lVar9 + 1;
  } while (lVar9 != 10);
  piVar2 = (int *)puVar11[1];
  for (piVar5 = (int *)*puVar11; piVar5 != piVar2; piVar5 = piVar5 + 6) {
    if (piVar5[2] == 0) {
      *(undefined *)((long)param_1 + (long)*piVar5 + 0x694) = 1;
    }
  }
  lVar9 = 0;
  do {
    uVar10 = 4;
    if (*(char *)((long)param_1 + lVar9 + 0x694) != '\0') {
      uVar10 = *(undefined4 *)((long)param_2 + lVar9 * 4 + 0x740);
    }
    *(undefined4 *)((long)param_1 + lVar9 * 4 + 0x66c) = uVar10;
    lVar9 = lVar9 + 1;
  } while (lVar9 != 10);
  lVar16 = 0;
  lVar9 = param_2[lVar12 * 0x1b + 0xb4];
  if (0 < (int)(param_2[lVar12 * 0x1b + 0xb5] - lVar9 >> 3) * -0x55555555) {
    do {
      piVar2 = (int *)(lVar9 + lVar16 * 0x18);
      if ((*(char *)((long)param_1 + (long)*piVar2 + 0x694) != '\0') ||
         ((-1 < piVar2[1] && (*(char *)((long)param_1 + (long)piVar2[1] + 0x694) != '\0')))) {
        local_168[0] = 0;
        local_160 = (long *)0x0;
                    /* try { // try from 000316ed to 00031703 has its CatchHandler @ 00031d33 */
        FUN_00024620(&local_160,0);
        local_168[0] = 3;
        plVar6 = (long *)FUN_00041fe0(0x20);
        *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 0003171c to 00031720 has its CatchHandler @ 00031d50 */
        FUN_00017bf0(plVar6,"boat");
        local_158 = 0;
        local_150 = 5;
        local_148[1] = 0;
        local_160 = plVar6;
        local_148[0] = lVar16;
                    /* try { // try from 00031774 to 00031778 has its CatchHandler @ 00031d13 */
        FUN_0002fd20(local_a8,local_168,2,1,2);
        local_98 = 0;
        local_138[0] = 0;
        local_130 = (long *)0x0;
                    /* try { // try from 000317ab to 000317c1 has its CatchHandler @ 00031d60 */
        FUN_00024620(&local_130,0);
        local_138[0] = 3;
        plVar6 = (long *)FUN_00041fe0(0x20);
        *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 000317da to 000317de has its CatchHandler @ 00031d23 */
        FUN_00017bf0(plVar6,"position");
        local_118[0] = (long)*piVar2;
        local_128 = 0;
        local_120 = 5;
        local_118[1] = 0;
        local_130 = plVar6;
                    /* try { // try from 00031833 to 00031837 has its CatchHandler @ 00031c62 */
        FUN_0002fd20(local_90,local_138,2,1,2);
        local_80 = 0;
        local_108[0] = 0;
        local_100 = (long *)0x0;
                    /* try { // try from 0003186a to 00031880 has its CatchHandler @ 00031c5d */
        FUN_00024620(&local_100,0);
        local_108[0] = 3;
        plVar6 = (long *)FUN_00041fe0(0x20);
        *plVar6 = (long)(plVar6 + 2);
                    /* try { // try from 00031899 to 0003189d has its CatchHandler @ 00031d68 */
        FUN_00017bf0(plVar6,"destination");
        local_e8[0] = (long)piVar2[1];
        local_f8 = 0;
        local_f0 = 5;
        local_e8[1] = 0;
        local_100 = plVar6;
                    /* try { // try from 000318f2 to 000318f6 has its CatchHandler @ 00031d2b */
        FUN_0002fd20(local_78,local_108,2,1,2);
        local_68 = 0;
        local_d8[0] = 0;
        local_d0 = (long *)0x0;
                    /* try { // try from 00031929 to 0003193f has its CatchHandler @ 00031d4b */
        FUN_00024620(&local_d0,0);
        local_d8[0] = 3;
        plVar6 = (long *)FUN_00041fe0(0x20);
        *plVar6 = (long)(plVar6 + 2);
        local_1a8 = local_1c8;
        plStack_1a0 = plVar6;
                    /* try { // try from 0003196c to 00031970 has its CatchHandler @ 00031d0e */
        FUN_00017bf0(plVar6,&DAT_000e0986);
        local_b8[0] = (long)piVar2[2];
        local_c8 = 0;
        local_c0 = 5;
        local_b8[1] = 0;
        local_d0 = plVar6;
                    /* try { // try from 000319c5 to 000319c9 has its CatchHandler @ 00031d58 */
        FUN_0002fd20(local_60,local_d8,2,1,2);
        local_50 = 0;
                    /* try { // try from 000319f1 to 000319f5 has its CatchHandler @ 00031d1b */
        FUN_0002fd20(&local_1a8,local_a8,4,1,2);
        if (*(char *)(param_1 + 0xd8) == '\0') {
          *(undefined *)(param_1 + 0xd8) = 2;
                    /* try { // try from 00031a16 to 00031a35 has its CatchHandler @ 00031d75 */
          FUN_000210f0(local_1c8,2);
          param_1[0xd9] = local_1c8._0_8_;
        }
        else if (*(char *)(param_1 + 0xd8) != '\x02') {
          uVar7 = FUN_00040f40(0x20);
          local_1c8._0_8_ =
               FUN_000137b8(*(undefined *)(param_1 + 0xd8),"cannot use push_back() with ");
                    /* try { // try from 00031c25 to 00031c29 has its CatchHandler @ 00031d7d */
          FUN_0001df60(local_188);
                    /* try { // try from 00031c35 to 00031c39 has its CatchHandler @ 00031d43 */
          FUN_00013ba0(uVar7,0x134,local_188);
          FUN_000b07c0(local_188);
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00031c53 to 00031c57 has its CatchHandler @ 00031d75 */
          FUN_00041f00(uVar7,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
        }
        FUN_000182f0(param_1[0xd9],&local_1a8);
        FUN_00024620(&plStack_1a0,(ulong)local_1a8 & 0xff);
        puVar15 = local_48;
        do {
          puVar14 = puVar15 + -0x18;
          FUN_00024620(puVar15 + -0x10,*puVar14);
          puVar15 = puVar14;
        } while (puVar14 != local_a8);
        FUN_00024620(local_b8,local_c0);
        FUN_00024620(&local_d0,local_d8[0]);
        FUN_00024620(local_e8,local_f0);
        FUN_00024620(&local_100,local_108[0]);
        FUN_00024620(local_118,local_120);
        FUN_00024620(&local_130,local_138[0]);
        FUN_00024620(local_148,local_150);
        FUN_00024620(&local_160);
      }
      lVar16 = lVar16 + 1;
      lVar9 = param_2[lVar12 * 0x1b + 0xb4];
    } while ((int)lVar16 < (int)(param_2[lVar12 * 0x1b + 0xb5] - lVar9 >> 3) * -0x55555555);
  }
  if (*(int *)((long)param_2 + 0x584) < 0x50) {
                    /* try { // try from 00031bd2 to 00031bd6 has its CatchHandler @ 00031d70 */
    FUN_00021660(local_1c8,param_2,param_1 + 0xb1,(undefined4 *)((long)param_1 + 0x66c),
                 param_2 + 0xed);
  }
  else {
    local_1b8 = 0;
    local_1c8._8_8_ = 0;
    local_1c8._0_8_ = 0;
  }
  local_1f0 = local_1c8;
  local_1a8 = (undefined *)param_1[0xda];
  plStack_1a0 = (long *)param_1[0xdb];
  local_198 = param_1[0xdc];
  param_1[0xda] = local_1c8._0_8_;
  param_1[0xdb] = local_1c8._8_8_;
  param_1[0xdc] = local_1b8;
  local_1b8 = 0;
  local_1c8 = (undefined  [16])0x0;
  FUN_0001cf40(&local_1a8);
  FUN_0001cf40(local_1f0);
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


