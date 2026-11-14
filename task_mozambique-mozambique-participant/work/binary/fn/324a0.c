// ===== FUNC 324a0 size=1261

void FUN_000324a0(undefined *param_1,int *param_2)

{
  undefined uVar1;
  int iVar2;
  undefined8 uVar3;
  undefined (*pauVar4) [16];
  ulong uVar5;
  undefined *puVar6;
  undefined *puVar7;
  undefined *puVar8;
  long lVar9;
  int *piVar10;
  undefined *puVar11;
  long lVar12;
  long in_FS_OFFSET;
  undefined local_179;
  undefined *local_178;
  undefined (*local_170) [16];
  undefined local_168 [8];
  undefined8 local_160;
  undefined8 local_158;
  undefined local_150;
  long local_148 [2];
  undefined local_138 [8];
  undefined8 local_130;
  undefined8 local_128;
  undefined local_120;
  long local_118 [2];
  undefined local_108 [8];
  undefined (*local_100) [16];
  undefined8 local_f8;
  undefined local_f0;
  long local_e8 [2];
  undefined local_d8 [8];
  undefined8 local_d0;
  undefined8 local_c8;
  undefined local_c0;
  undefined (*local_b8) [16];
  undefined8 local_b0;
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
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  local_168[0] = 0;
  local_160 = 0;
                    /* try { // try from 000324e2 to 000324f5 has its CatchHandler @ 00032b88 */
  FUN_00024620(&local_160,0);
  local_168[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00032503 to 00032507 has its CatchHandler @ 00032bc7 */
  FUN_00018b10(uVar3,"position");
  local_148[0] = (long)*param_2;
  local_158 = 0;
  local_150 = 5;
  local_148[1] = 0;
  local_160 = uVar3;
                    /* try { // try from 0003254c to 00032550 has its CatchHandler @ 00032bc2 */
  FUN_0002fd20(local_a8,local_168,2,1,2);
  local_98 = 0;
  local_138[0] = 0;
  local_130 = 0;
                    /* try { // try from 00032583 to 00032599 has its CatchHandler @ 00032be9 */
  FUN_00024620(&local_130,0);
  local_138[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 000325a7 to 000325ab has its CatchHandler @ 00032be4 */
  FUN_00018b10(uVar3,"destination");
  local_118[0] = (long)param_2[1];
  local_128 = 0;
  local_120 = 5;
  local_118[1] = 0;
  local_130 = uVar3;
                    /* try { // try from 00032600 to 00032604 has its CatchHandler @ 00032bdf */
  FUN_0002fd20(local_90,local_138,2,1,2);
  local_80 = 0;
  local_108[0] = 0;
  local_100 = (undefined (*) [16])0x0;
                    /* try { // try from 00032637 to 0003264d has its CatchHandler @ 00032bd7 */
  FUN_00024620(&local_100,0);
  local_108[0] = 3;
  pauVar4 = (undefined (*) [16])FUN_00041fe0(0x20);
  local_178 = &local_179;
  local_170 = pauVar4;
                    /* try { // try from 0003266a to 0003266e has its CatchHandler @ 00032b04 */
  FUN_00018b10(pauVar4,&DAT_000e0986);
  local_e8[0] = (long)param_2[2];
  local_f8 = 0;
  local_f0 = 5;
  local_e8[1] = 0;
  local_100 = pauVar4;
                    /* try { // try from 000326c3 to 000326c7 has its CatchHandler @ 00032afa */
  FUN_0002fd20(local_78,local_108,2,1,2);
  local_68 = 0;
  local_d8[0] = 0;
  local_d0 = 0;
                    /* try { // try from 000326fa to 00032710 has its CatchHandler @ 00032aff */
  FUN_00024620(&local_d0,0);
  local_d8[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 0003271e to 00032722 has its CatchHandler @ 00032af5 */
  FUN_00018b10(uVar3,"cargo");
  local_c8 = 0;
  local_c0 = 0;
  local_b8 = (undefined (*) [16])0x0;
  local_d0 = uVar3;
                    /* try { // try from 0003275d to 00032780 has its CatchHandler @ 00032b8d */
  FUN_00024620(&local_b8,0);
  piVar10 = param_2 + 3;
  local_c0 = 2;
  pauVar4 = (undefined (*) [16])FUN_00041fe0(0x18);
  *(undefined8 *)pauVar4[1] = 0;
  *pauVar4 = (undefined  [16])0x0;
  uVar5 = (long)(param_2 + 6) - (long)piVar10;
  lVar9 = (long)uVar5 >> 2;
  local_170 = pauVar4;
  if (0x1ffffffffffffffc < uVar5) {
    local_178 = &local_179;
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003298f to 00032993 has its CatchHandler @ 00032999 */
    FUN_00015e26("cannot create std::vector larger than max_size()");
  }
  lVar12 = lVar9 * 0x10;
  if (lVar9 == 0) {
    puVar6 = (undefined *)0x0;
    local_178 = &local_179;
  }
  else {
    local_178 = &local_179;
                    /* try { // try from 000327d2 to 000327d6 has its CatchHandler @ 00032999 */
    puVar6 = (undefined *)FUN_00041fe0(lVar12);
  }
  *(undefined **)*pauVar4 = puVar6;
  *(undefined **)pauVar4[1] = puVar6 + lVar12;
  if (param_2 + 6 != piVar10) {
    puVar11 = puVar6 + 0x30;
    puVar7 = puVar6;
    do {
      iVar2 = *piVar10;
      *puVar7 = 5;
      puVar8 = puVar7 + 0x10;
      piVar10 = piVar10 + 1;
      *(long *)(puVar7 + 8) = (long)iVar2;
      puVar7 = puVar8;
      puVar6 = puVar11;
    } while (puVar11 != puVar8);
  }
  *(undefined **)(*pauVar4 + 8) = puVar6;
  local_b0 = 0;
  local_b8 = pauVar4;
                    /* try { // try from 00032842 to 00032846 has its CatchHandler @ 0003299e */
  FUN_0002fd20(local_60,local_d8,2,1,2);
  local_50 = 0;
                    /* try { // try from 0003286b to 0003286f has its CatchHandler @ 000329a6 */
  FUN_0002fd20(&local_178,local_a8,4,1,2);
  uVar1 = *param_1;
  *param_1 = local_178._0_1_;
  pauVar4 = *(undefined (**) [16])(param_1 + 8);
  *(undefined (**) [16])(param_1 + 8) = local_170;
  local_178 = (undefined *)CONCAT71(local_178._1_7_,uVar1);
  local_170 = pauVar4;
  FUN_00024620(&local_170);
  puVar6 = local_48;
  do {
    puVar11 = puVar6 + -0x18;
    FUN_00024620(puVar6 + -0x10,*puVar11);
    puVar6 = puVar11;
  } while (puVar11 != local_a8);
  FUN_00024620(&local_b8,local_c0);
  FUN_00024620(&local_d0,local_d8[0]);
  FUN_00024620(local_e8,local_f0);
  FUN_00024620(&local_100,local_108[0]);
  FUN_00024620(local_118,local_120);
  FUN_00024620(&local_130,local_138[0]);
  FUN_00024620(local_148,local_150);
  FUN_00024620(&local_160,local_168[0]);
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


