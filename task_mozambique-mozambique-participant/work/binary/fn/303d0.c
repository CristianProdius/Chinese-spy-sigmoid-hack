// ===== FUNC 303d0 size=1115

void FUN_000303d0(undefined *param_1,long *param_2)

{
  undefined uVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  undefined8 uVar5;
  long *plVar6;
  undefined *puVar7;
  long in_FS_OFFSET;
  undefined local_a9;
  undefined *local_a8;
  long *local_a0;
  undefined local_98 [8];
  undefined local_90 [8];
  undefined8 local_88;
  long *local_78;
  undefined8 local_70;
  long local_68;
  undefined local_60;
  long *local_58;
  undefined8 local_50;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  local_78 = (long *)((ulong)local_78 & 0xffffffffffffff00);
  local_70 = 0;
                    /* try { // try from 0003040f to 00030422 has its CatchHandler @ 0003084c */
  FUN_00024620(&local_70,0);
  local_78 = (long *)CONCAT71(local_78._1_7_,3);
  uVar5 = FUN_00041fe0(0x20);
                    /* try { // try from 00030430 to 00030434 has its CatchHandler @ 0003090f */
  FUN_00018b10(uVar5,"op");
  local_60 = 0;
  local_68 = 0;
  local_58 = (long *)0x0;
  local_70 = uVar5;
                    /* try { // try from 0003045b to 0003046e has its CatchHandler @ 000308e5 */
  FUN_00024620(&local_58,0);
  local_60 = 3;
  plVar6 = (long *)FUN_00041fe0(0x20);
  local_a8 = &local_a9;
  lVar3 = *param_2;
  lVar4 = param_2[1];
  *plVar6 = (long)(plVar6 + 2);
  local_a0 = plVar6;
                    /* try { // try from 00030497 to 0003049b has its CatchHandler @ 00030842 */
  FUN_00017e00(plVar6,lVar3,lVar4 + lVar3);
  local_50 = 0;
  local_58 = plVar6;
                    /* try { // try from 000304ca to 000304ce has its CatchHandler @ 000308f6 */
  FUN_0002fd20(local_98,&local_78,2,1,2);
  local_88 = 0;
                    /* try { // try from 000304f0 to 000304f4 has its CatchHandler @ 00030847 */
  FUN_0002fd20(&local_a8,local_98,1,1,2);
  uVar1 = *param_1;
  *param_1 = local_a8._0_1_;
  plVar6 = *(long **)(param_1 + 8);
  *(long **)(param_1 + 8) = local_a0;
  local_a0 = plVar6;
  local_a8._0_1_ = uVar1;
  FUN_00024620(&local_a0);
  FUN_00024620(local_90,local_98[0]);
  FUN_00024620(&local_58,local_60);
  FUN_00024620(&local_70,(ulong)local_78 & 0xff);
  if (*(int *)(param_2 + 4) < 0) {
    iVar2 = *(int *)((long)param_2 + 0x24);
  }
  else {
    local_a8 = (undefined *)CONCAT71(local_a8._1_7_,5);
    local_a0 = (long *)(long)*(int *)(param_2 + 4);
    local_78 = &local_68;
    FUN_00017bf0(&local_78,"boat");
                    /* try { // try from 000307e5 to 000307e9 has its CatchHandler @ 000308ed */
    puVar7 = (undefined *)FUN_00026330(param_1,&local_78);
    if (local_78 != &local_68) {
      thunk_FUN_000d36e0(local_78,local_68 + 1);
    }
    plVar6 = *(long **)(puVar7 + 8);
    uVar1 = *puVar7;
    *puVar7 = 5;
    *(long **)(puVar7 + 8) = local_a0;
    local_a0 = plVar6;
    local_a8._0_1_ = uVar1;
    FUN_00024620(&local_a0);
    iVar2 = *(int *)((long)param_2 + 0x24);
  }
  if (iVar2 < 0) {
    iVar2 = *(int *)(param_2 + 5);
  }
  else {
    local_a0 = (long *)(long)iVar2;
    local_a8 = (undefined *)CONCAT71(local_a8._1_7_,5);
    local_78 = &local_68;
    FUN_00017bf0(&local_78,"destination");
                    /* try { // try from 0003075d to 00030761 has its CatchHandler @ 0003090d */
    puVar7 = (undefined *)FUN_00026330(param_1,&local_78);
    if (local_78 != &local_68) {
      thunk_FUN_000d36e0(local_78,local_68 + 1);
    }
    plVar6 = *(long **)(puVar7 + 8);
    uVar1 = *puVar7;
    *puVar7 = 5;
    *(long **)(puVar7 + 8) = local_a0;
    local_a0 = plVar6;
    local_a8._0_1_ = uVar1;
    FUN_00024620(&local_a0);
    iVar2 = *(int *)(param_2 + 5);
  }
  if (iVar2 < 0) {
    iVar2 = *(int *)((long)param_2 + 0x2c);
  }
  else {
    local_a0 = (long *)(long)iVar2;
    local_a8 = (undefined *)CONCAT71(local_a8._1_7_,5);
    local_78 = &local_68;
    FUN_00017bf0(&local_78,&DAT_000e095d);
                    /* try { // try from 0003065d to 00030661 has its CatchHandler @ 000308f4 */
    puVar7 = (undefined *)FUN_00026330(param_1,&local_78);
    if (local_78 != &local_68) {
      thunk_FUN_000d36e0(local_78,local_68 + 1);
    }
    plVar6 = *(long **)(puVar7 + 8);
    uVar1 = *puVar7;
    *puVar7 = 5;
    *(long **)(puVar7 + 8) = local_a0;
    local_a0 = plVar6;
    local_a8._0_1_ = uVar1;
    FUN_00024620(&local_a0);
    iVar2 = *(int *)((long)param_2 + 0x2c);
  }
  if (iVar2 != 0) {
    local_a0 = (long *)(long)iVar2;
    local_a8 = (undefined *)CONCAT71(local_a8._1_7_,5);
    local_78 = &local_68;
    FUN_00017bf0(&local_78,"quantity");
                    /* try { // try from 000306dd to 000306e1 has its CatchHandler @ 000308f2 */
    puVar7 = (undefined *)FUN_00026330(param_1,&local_78);
    if (local_78 != &local_68) {
      thunk_FUN_000d36e0(local_78,local_68 + 1);
    }
    uVar1 = *puVar7;
    *puVar7 = 5;
    plVar6 = *(long **)(puVar7 + 8);
    *(long **)(puVar7 + 8) = local_a0;
    local_a0 = plVar6;
    local_a8._0_1_ = uVar1;
    FUN_00024620(&local_a0);
  }
  if (-1 < *(int *)(param_2 + 6)) {
    local_a8 = (undefined *)CONCAT71(local_a8._1_7_,5);
    local_a0 = (long *)(long)*(int *)(param_2 + 6);
    local_78 = &local_68;
    FUN_00017bf0(&local_78,"contract");
                    /* try { // try from 000305dd to 000305e1 has its CatchHandler @ 0003090b */
    puVar7 = (undefined *)FUN_00026330(param_1,&local_78);
    if (local_78 != &local_68) {
      thunk_FUN_000d36e0(local_78,local_68 + 1);
    }
    uVar1 = *puVar7;
    *puVar7 = 5;
    plVar6 = *(long **)(puVar7 + 8);
    *(long **)(puVar7 + 8) = local_a0;
    local_a0 = plVar6;
    local_a8._0_1_ = uVar1;
    FUN_00024620(&local_a0);
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


