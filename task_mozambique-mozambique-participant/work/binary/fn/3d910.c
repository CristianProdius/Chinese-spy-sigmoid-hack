// ===== FUNC 3d910 size=2448

void FUN_0003d910(undefined *param_1,int *param_2)

{
  int *piVar1;
  undefined uVar2;
  int iVar3;
  undefined8 uVar4;
  undefined (*pauVar5) [16];
  long lVar6;
  undefined *puVar7;
  ulong uVar8;
  undefined *puVar9;
  int *piVar10;
  long lVar11;
  long in_FS_OFFSET;
  bool bVar12;
  undefined local_249;
  undefined *local_248;
  undefined (*local_240) [16];
  undefined local_238 [8];
  undefined8 local_230;
  undefined8 local_228;
  undefined local_220;
  long local_218 [2];
  undefined local_208 [8];
  undefined8 local_200;
  undefined8 local_1f8;
  undefined local_1f0;
  long local_1e8 [2];
  undefined local_1d8 [8];
  undefined8 local_1d0;
  undefined8 local_1c8;
  undefined local_1c0;
  long local_1b8 [2];
  undefined local_1a8 [8];
  undefined8 local_1a0;
  undefined8 local_198;
  undefined local_190 [8];
  undefined local_188 [8];
  undefined8 local_180;
  undefined local_178 [8];
  undefined8 local_170;
  undefined8 local_168;
  undefined local_160;
  undefined (*local_158) [16];
  undefined8 local_150;
  undefined local_148 [8];
  undefined (*local_140) [16];
  undefined8 local_138;
  undefined local_130;
  undefined (*local_128) [16];
  undefined8 local_120;
  undefined local_118 [8];
  undefined8 local_110;
  undefined8 local_108;
  undefined local_100;
  undefined (*local_f8) [16];
  undefined8 local_f0;
  undefined local_e8 [16];
  undefined8 local_d8;
  undefined local_d0 [16];
  undefined8 local_c0;
  undefined local_b8 [16];
  undefined8 local_a8;
  undefined local_a0 [16];
  undefined8 local_90;
  undefined local_88 [16];
  undefined8 local_78;
  undefined local_70 [16];
  undefined8 local_60;
  undefined local_58 [16];
  undefined8 local_48;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  local_238[0] = 0;
  local_230 = 0;
                    /* try { // try from 0003d961 to 0003d977 has its CatchHandler @ 0003e6cb */
  FUN_00024620(&local_230,0);
  local_238[0] = 3;
  uVar4 = FUN_00041fe0(0x20);
                    /* try { // try from 0003d985 to 0003d989 has its CatchHandler @ 0003e599 */
  FUN_00018b10(uVar4,&DAT_000e1d86);
  local_218[0] = (long)*param_2;
  local_228 = 0;
  local_220 = 5;
  local_218[1] = 0;
  local_230 = uVar4;
                    /* try { // try from 0003d9e0 to 0003d9e4 has its CatchHandler @ 0003e57f */
  FUN_0002fd20(local_e8,local_238,2,1,2);
  local_d8 = 0;
  local_208[0] = 0;
  local_200 = 0;
                    /* try { // try from 0003da17 to 0003da2d has its CatchHandler @ 0003e2c5 */
  FUN_00024620(&local_200,0);
  local_208[0] = 3;
  uVar4 = FUN_00041fe0(0x20);
                    /* try { // try from 0003da3b to 0003da3f has its CatchHandler @ 0003e2b5 */
  FUN_00018b10(uVar4,"score");
  local_1e8[0] = (long)param_2[1];
  local_1f8 = 0;
  local_1f0 = 5;
  local_1e8[1] = 0;
  local_200 = uVar4;
                    /* try { // try from 0003da94 to 0003da98 has its CatchHandler @ 0003e5a6 */
  FUN_0002fd20(local_d0,local_208,2,1,2);
  local_c0 = 0;
  local_1d8[0] = 0;
  local_1d0 = 0;
                    /* try { // try from 0003dacb to 0003dae1 has its CatchHandler @ 0003e58c */
  FUN_00024620(&local_1d0,0);
  local_1d8[0] = 3;
  uVar4 = FUN_00041fe0(0x20);
                    /* try { // try from 0003daef to 0003daf3 has its CatchHandler @ 0003e76d */
  FUN_00018b10(uVar4,"crafted_deliveries");
  local_1b8[0] = (long)param_2[2];
  local_1c8 = 0;
  local_1c0 = 5;
  local_1b8[1] = 0;
  local_1d0 = uVar4;
                    /* try { // try from 0003db48 to 0003db4c has its CatchHandler @ 0003e768 */
  FUN_0002fd20(local_b8,local_1d8,2,1,2);
  local_a8 = 0;
  local_1a8[0] = 0;
  local_1a0 = 0;
                    /* try { // try from 0003db7f to 0003db95 has its CatchHandler @ 0003e59e */
  FUN_00024620(&local_1a0,0);
  local_1a8[0] = 3;
  uVar4 = FUN_00041fe0(0x20);
                    /* try { // try from 0003dba3 to 0003dba7 has its CatchHandler @ 0003e584 */
  FUN_00018b10(uVar4,"boats");
  local_198 = 0;
  local_1a0 = uVar4;
                    /* try { // try from 0003dbc8 to 0003dbcc has its CatchHandler @ 0003e591 */
  FUN_00032c30(local_190,param_2 + 4);
  local_180 = 0;
                    /* try { // try from 0003dc01 to 0003dc05 has its CatchHandler @ 0003e57a */
  FUN_0002fd20(local_a0,local_1a8,2,1,2);
  local_90 = 0;
  local_178[0] = 0;
  local_170 = 0;
                    /* try { // try from 0003dc38 to 0003dc4e has its CatchHandler @ 0003e2cd */
  FUN_00024620(&local_170,0);
  local_178[0] = 3;
  uVar4 = FUN_00041fe0(0x20);
                    /* try { // try from 0003dc5c to 0003dc60 has its CatchHandler @ 0003e2bd */
  FUN_00018b10(uVar4,"warehouses");
  local_168 = 0;
  local_160 = 0;
  local_158 = (undefined (*) [16])0x0;
  local_170 = uVar4;
                    /* try { // try from 0003dc9b to 0003dcbc has its CatchHandler @ 0003e6d3 */
  FUN_00024620(&local_158,0);
  local_160 = 2;
  piVar10 = param_2 + 0x28;
  pauVar5 = (undefined (*) [16])FUN_00041fe0(0x18);
  *(undefined8 *)pauVar5[1] = 0;
  uVar8 = (long)piVar10 - (long)(param_2 + 10);
  *pauVar5 = (undefined  [16])0x0;
  lVar6 = (long)uVar8 >> 2;
  if (0x5ffffffffffffff4 < uVar8) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003e28e to 0003e292 has its CatchHandler @ 0003e77f */
    FUN_00015e26("cannot create std::vector larger than max_size()");
  }
  lVar11 = lVar6 * -0x5555555555555550;
  if (lVar6 * -0x5555555555555555 == 0) {
    lVar6 = 0;
  }
  else {
                    /* try { // try from 0003dd10 to 0003dd2d has its CatchHandler @ 0003e77f */
    lVar6 = FUN_00041fe0(lVar11);
  }
  *(long *)*pauVar5 = lVar6;
  *(long *)pauVar5[1] = lVar11 + lVar6;
  uVar4 = FUN_0003d7b0(param_2 + 10,piVar10);
  *(undefined8 *)(*pauVar5 + 8) = uVar4;
  local_150 = 0;
  local_158 = pauVar5;
                    /* try { // try from 0003dd6e to 0003dd72 has its CatchHandler @ 0003e787 */
  FUN_0002fd20(local_88,local_178,2,1,2);
  local_78 = 0;
  local_148[0] = 0;
  local_140 = (undefined (*) [16])0x0;
                    /* try { // try from 0003dda5 to 0003ddbb has its CatchHandler @ 0003e7e9 */
  FUN_00024620(&local_140,0);
  local_148[0] = 3;
  pauVar5 = (undefined (*) [16])FUN_00041fe0(0x20);
  local_248 = &local_249;
  local_240 = pauVar5;
                    /* try { // try from 0003dde3 to 0003dde7 has its CatchHandler @ 0003e7ee */
  FUN_00018b10(pauVar5,"workshops");
  local_138 = 0;
  local_130 = 0;
  local_128 = (undefined (*) [16])0x0;
  local_140 = pauVar5;
                    /* try { // try from 0003de22 to 0003de42 has its CatchHandler @ 0003e6dd */
  FUN_00024620(&local_128,0);
  local_130 = 2;
  piVar1 = (int *)((long)param_2 + 0xaa);
  pauVar5 = (undefined (*) [16])FUN_00041fe0(0x18);
  uVar8 = (long)piVar1 - (long)piVar10;
  *(undefined8 *)pauVar5[1] = 0;
  *pauVar5 = (undefined  [16])0x0;
  local_240 = pauVar5;
  if (uVar8 >> 0x3b != 0) {
    local_248 = &local_249;
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003e2ab to 0003e2af has its CatchHandler @ 0003e6d8 */
    FUN_00015e26("cannot create std::vector larger than max_size()");
  }
  if (uVar8 == 0) {
    puVar7 = (undefined *)0x0;
    local_248 = &local_249;
  }
  else {
    local_248 = &local_249;
                    /* try { // try from 0003de94 to 0003de98 has its CatchHandler @ 0003e6d8 */
    puVar7 = (undefined *)FUN_00041fe0();
  }
  *(undefined **)*pauVar5 = puVar7;
  *(undefined **)pauVar5[1] = puVar7 + uVar8 * 0x10;
  puVar9 = puVar7;
  if (piVar1 != piVar10) {
    do {
      uVar2 = *(undefined *)piVar10;
      piVar10 = (int *)((long)piVar10 + 1);
      *puVar9 = 4;
      *(undefined8 *)(puVar9 + 8) = 0;
      puVar9[8] = uVar2;
      puVar9 = puVar9 + 0x10;
    } while (piVar1 != piVar10);
    puVar7 = puVar7 + 0xa0;
  }
  *(undefined **)(*pauVar5 + 8) = puVar7;
  local_120 = 0;
  local_128 = pauVar5;
                    /* try { // try from 0003df1d to 0003df21 has its CatchHandler @ 0003e794 */
  FUN_0002fd20(local_70,local_148,2,1,2);
  local_60 = 0;
  local_118[0] = 0;
  local_110 = 0;
                    /* try { // try from 0003df4f to 0003df65 has its CatchHandler @ 0003e799 */
  FUN_00024620(&local_110,0);
  local_118[0] = 3;
  uVar4 = FUN_00041fe0(0x20);
                    /* try { // try from 0003df73 to 0003df77 has its CatchHandler @ 0003e7dc */
  FUN_00018b10(uVar4,&DAT_000e1db3);
  local_108 = 0;
  local_100 = 0;
  local_f8 = (undefined (*) [16])0x0;
  local_110 = uVar4;
                    /* try { // try from 0003dfb2 to 0003dfd6 has its CatchHandler @ 0003e7e1 */
  FUN_00024620(&local_f8,0);
  piVar10 = param_2 + 0x35;
  local_100 = 2;
  param_2 = param_2 + 0x2b;
  pauVar5 = (undefined (*) [16])FUN_00041fe0(0x18);
  *pauVar5 = (undefined  [16])0x0;
  *(undefined8 *)pauVar5[1] = 0;
  lVar6 = (long)piVar10 - (long)param_2 >> 2;
  local_240 = pauVar5;
  if (0x1ffffffffffffffc < (ulong)((long)piVar10 - (long)param_2)) {
    local_248 = &local_249;
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003e29f to 0003e2a3 has its CatchHandler @ 0003e684 */
    FUN_00015e26("cannot create std::vector larger than max_size()");
  }
  lVar11 = lVar6 * 0x10;
  if (lVar6 == 0) {
    puVar7 = (undefined *)0x0;
    local_248 = &local_249;
  }
  else {
    local_248 = &local_249;
                    /* try { // try from 0003e034 to 0003e038 has its CatchHandler @ 0003e684 */
    puVar7 = (undefined *)FUN_00041fe0(lVar11);
  }
  *(undefined **)*pauVar5 = puVar7;
  *(undefined **)pauVar5[1] = puVar7 + lVar11;
  puVar9 = puVar7;
  if (piVar10 != param_2) {
    do {
      iVar3 = *param_2;
      param_2 = param_2 + 1;
      *puVar9 = 5;
      *(long *)(puVar9 + 8) = (long)iVar3;
      puVar9 = puVar9 + 0x10;
    } while (piVar10 != param_2);
    puVar7 = puVar7 + 0xa0;
  }
  *(undefined **)(*pauVar5 + 8) = puVar7;
  local_f0 = 0;
  local_f8 = pauVar5;
                    /* try { // try from 0003e0ac to 0003e0b0 has its CatchHandler @ 0003e67f */
  FUN_0002fd20(local_58,local_118,2,1,2);
  local_48 = 0;
                    /* try { // try from 0003e0d8 to 0003e0dc has its CatchHandler @ 0003e2b0 */
  FUN_0002fd20(&local_248,local_e8,7,1,2);
  uVar2 = *param_1;
  *param_1 = local_248._0_1_;
  pauVar5 = *(undefined (**) [16])(param_1 + 8);
  *(undefined (**) [16])(param_1 + 8) = local_240;
  local_248 = (undefined *)CONCAT71(local_248._1_7_,uVar2);
  local_240 = pauVar5;
  FUN_00024620(&local_240);
  puVar7 = local_58;
  do {
    FUN_00024620(puVar7 + 8,*puVar7);
    bVar12 = local_e8 != puVar7;
    puVar7 = puVar7 + -0x18;
  } while (bVar12);
  FUN_00024620(&local_f8,local_100);
  FUN_00024620(&local_110,local_118[0]);
  FUN_00024620(&local_128,local_130);
  FUN_00024620(&local_140,local_148[0]);
  FUN_00024620(&local_158,local_160);
  FUN_00024620(&local_170,local_178[0]);
  FUN_00024620(local_188,local_190[0]);
  FUN_00024620(&local_1a0,local_1a8[0]);
  FUN_00024620(local_1b8,local_1c0);
  FUN_00024620(&local_1d0,local_1d8[0]);
  FUN_00024620(local_1e8,local_1f0);
  FUN_00024620(&local_200,local_208[0]);
  FUN_00024620(local_218,local_220);
  FUN_00024620(&local_230,local_238[0]);
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


