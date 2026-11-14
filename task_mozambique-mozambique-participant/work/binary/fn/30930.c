// ===== FUNC 30930 size=1215

void FUN_00030930(undefined *param_1,int *param_2)

{
  long *plVar1;
  undefined uVar2;
  undefined8 uVar3;
  long *plVar4;
  long in_FS_OFFSET;
  undefined local_1b8 [8];
  undefined8 local_1b0;
  undefined local_1a8 [8];
  undefined8 local_1a0;
  undefined8 local_198;
  undefined local_190;
  long local_188 [2];
  undefined local_178 [8];
  undefined8 local_170;
  undefined8 local_168;
  undefined local_160;
  long local_158 [2];
  undefined local_148 [8];
  undefined8 local_140;
  undefined8 local_138;
  undefined local_130;
  long local_128 [2];
  undefined local_118 [8];
  undefined8 local_110;
  undefined8 local_108;
  undefined local_100;
  long local_f8 [2];
  undefined local_e8 [8];
  undefined8 local_e0;
  undefined8 local_d8;
  undefined local_d0;
  long local_c8 [4];
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
  long *plVar5;
  
  local_40[0] = *(long *)(in_FS_OFFSET + 0x28);
  local_1a8[0] = 0;
  local_1a0 = 0;
                    /* try { // try from 00030972 to 00030985 has its CatchHandler @ 00030fac */
  FUN_00024620(&local_1a0,0);
  local_1a8[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00030993 to 00030997 has its CatchHandler @ 00030f95 */
  FUN_00018b10(uVar3,&DAT_000e095d);
  local_188[0] = (long)*param_2;
  plVar1 = local_c8 + 2;
  local_198 = 0;
  local_190 = 5;
  local_188[1] = 0;
  local_1a0 = uVar3;
                    /* try { // try from 000309dc to 000309e0 has its CatchHandler @ 00030fa2 */
  FUN_0002fd20(plVar1,local_1a8,2,1,2);
  local_178[0] = 0;
  local_a8 = 0;
  local_170 = 0;
                    /* try { // try from 00030a05 to 00030a18 has its CatchHandler @ 00030f8b */
  FUN_00024620(&local_170,0);
  local_178[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00030a26 to 00030a2a has its CatchHandler @ 00030fa7 */
  FUN_00018b10(uVar3,"quantity");
  local_158[0] = (long)param_2[1];
  local_168 = 0;
  local_160 = 5;
  local_158[1] = 0;
  local_170 = uVar3;
                    /* try { // try from 00030a73 to 00030a77 has its CatchHandler @ 00030f90 */
  FUN_0002fd20(local_a0,local_178,2,1,2);
  local_90 = 0;
  local_148[0] = 0;
  local_140 = 0;
                    /* try { // try from 00030aaa to 00030ac0 has its CatchHandler @ 00030f9d */
  FUN_00024620(&local_140,0);
  local_148[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00030ace to 00030ad2 has its CatchHandler @ 00030f86 */
  FUN_00018b10(uVar3,"destination");
  local_128[0] = (long)param_2[2];
  local_138 = 0;
  local_130 = 5;
  local_128[1] = 0;
  local_140 = uVar3;
                    /* try { // try from 00030b27 to 00030b2b has its CatchHandler @ 00030f81 */
  FUN_0002fd20(local_88,local_148,2,1,2);
  local_78 = 0;
  local_118[0] = 0;
  local_110 = 0;
                    /* try { // try from 00030b5e to 00030b74 has its CatchHandler @ 00030f7c */
  FUN_00024620(&local_110,0);
  local_118[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00030b82 to 00030b86 has its CatchHandler @ 00030f42 */
  FUN_00018b10(uVar3,"points");
  local_f8[0] = (long)param_2[3];
  local_108 = 0;
  local_100 = 5;
  local_f8[1] = 0;
  local_110 = uVar3;
                    /* try { // try from 00030bdb to 00030bdf has its CatchHandler @ 00030f3d */
  FUN_0002fd20(local_70,local_118,2,1,2);
  local_60 = 0;
  local_e8[0] = 0;
  local_e0 = 0;
                    /* try { // try from 00030c12 to 00030c28 has its CatchHandler @ 00030efc */
  FUN_00024620(&local_e0,0);
  local_e8[0] = 3;
  uVar3 = FUN_00041fe0(0x20);
                    /* try { // try from 00030c36 to 00030c3a has its CatchHandler @ 00030ef7 */
  FUN_00018b10(uVar3,"deadline");
  local_c8[0] = (long)param_2[4];
  local_d8 = 0;
  local_d0 = 5;
  local_c8[1] = 0;
  local_e0 = uVar3;
                    /* try { // try from 00030c8f to 00030c93 has its CatchHandler @ 00030df4 */
  FUN_0002fd20(local_58,local_e8,2,1,2);
  local_48 = 0;
                    /* try { // try from 00030cb8 to 00030cbc has its CatchHandler @ 00030def */
  FUN_0002fd20(local_1b8,plVar1,5,1,2);
  uVar2 = *param_1;
  *param_1 = local_1b8[0];
  uVar3 = *(undefined8 *)(param_1 + 8);
  *(undefined8 *)(param_1 + 8) = local_1b0;
  local_1b8[0] = uVar2;
  local_1b0 = uVar3;
  FUN_00024620(&local_1b0);
  plVar4 = local_40;
  do {
    plVar5 = plVar4 + -3;
    FUN_00024620(plVar4 + -2,*(undefined *)plVar5);
    plVar4 = plVar5;
  } while (plVar5 != plVar1);
  FUN_00024620(local_c8,local_d0);
  FUN_00024620(&local_e0,local_e8[0]);
  FUN_00024620(local_f8,local_100);
  FUN_00024620(&local_110,local_118[0]);
  FUN_00024620(local_128,local_130);
  FUN_00024620(&local_140,local_148[0]);
  FUN_00024620(local_158,local_160);
  FUN_00024620(&local_170,local_178[0]);
  FUN_00024620(local_188,local_190);
  FUN_00024620(&local_1a0,local_1a8[0]);
  if (local_40[0] == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


