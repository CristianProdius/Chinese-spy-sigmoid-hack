// ===== FUNC 3fdf0 size=1884

/* WARNING: Type propagation algorithm not settling */

undefined8 FUN_0003fdf0(undefined8 param_1,int *param_2)

{
  undefined uVar1;
  long lVar2;
  long *plVar3;
  undefined *puVar4;
  undefined *puVar5;
  long in_FS_OFFSET;
  uint local_834;
  undefined local_7f9;
  ulong local_7f8 [2];
  undefined *local_7e8;
  long *local_7e0;
  long *local_7d8 [2];
  long local_7c8 [2];
  undefined local_7b8 [8];
  long local_7b0 [2];
  undefined local_7a0 [8];
  long local_798 [2];
  undefined local_788 [8];
  long *local_780;
  undefined8 local_778;
  undefined local_770 [8];
  ulong local_768 [2];
  undefined local_758 [8];
  long *local_750;
  undefined8 local_748;
  undefined local_740;
  ulong local_738 [2];
  undefined local_728 [8];
  undefined local_720 [8];
  undefined8 local_718;
  undefined local_710 [8];
  undefined local_708 [8];
  undefined8 local_700;
  undefined local_6f8 [16];
  undefined8 local_6e8;
  undefined local_6e0 [1360];
  long local_190;
  long local_180;
  undefined local_68;
  undefined local_60 [8];
  undefined local_58 [24];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_000311e0(local_728,param_2 + 2,*param_2 % 2);
  local_7f8[0] = 0;
  local_7f8[1] = 0;
                    /* try { // try from 0003fe5c to 0003fe60 has its CatchHandler @ 00040648 */
  FUN_0003e850(local_7f8,local_728);
  FUN_0001cf40(local_58);
  FUN_00024620(local_60,local_68);
  if (local_190 != 0) {
    thunk_FUN_000d36e0(local_190,local_180 - local_190);
  }
  local_7b8[0] = 0;
  local_7b0[0] = 0;
                    /* try { // try from 0003fec1 to 0003fed7 has its CatchHandler @ 00040650 */
  FUN_00024620(local_7b0,0);
  local_7b8[0] = 3;
  lVar2 = FUN_00041fe0(0x20);
                    /* try { // try from 0003fee5 to 0003fee9 has its CatchHandler @ 00040643 */
  FUN_00018b10(lVar2,"observation");
  local_7b0[1] = 0;
  local_7b0[0] = lVar2;
                    /* try { // try from 0003ff09 to 0003ff0d has its CatchHandler @ 00040775 */
  FUN_0002f160(local_7a0,local_7f8);
  local_798[1] = 0;
                    /* try { // try from 0003ff3d to 0003ff41 has its CatchHandler @ 0004073b */
  FUN_0002fd20(local_728,local_7b8,2,1,2);
  local_718 = 0;
  local_788[0] = 0;
  local_780 = (long *)0x0;
                    /* try { // try from 0003ff6f to 0003ff85 has its CatchHandler @ 0004075b */
  FUN_00024620(&local_780,0);
  local_788[0] = 3;
  plVar3 = (long *)FUN_00041fe0(0x20);
  local_7e8 = &local_7f9;
  local_7e0 = plVar3;
                    /* try { // try from 0003ffa2 to 0003ffa6 has its CatchHandler @ 0004071e */
  FUN_00018b10(plVar3,"game_done");
  local_778 = 0;
  local_770[0] = 4;
  local_768[1] = 0;
  local_768[0] = (ulong)(param_2[0x163] == 0x50);
  local_780 = plVar3;
                    /* try { // try from 00040017 to 0004001b has its CatchHandler @ 00040551 */
  FUN_0002fd20(local_710,local_788,2,1,2);
  local_700 = 0;
  local_758[0] = 0;
  local_750 = (long *)0x0;
                    /* try { // try from 00040049 to 0004005f has its CatchHandler @ 0004054c */
  FUN_00024620(&local_750,0);
  local_758[0] = 3;
  plVar3 = (long *)FUN_00041fe0(0x20);
                    /* try { // try from 0004006d to 00040071 has its CatchHandler @ 0004078d */
  FUN_00018b10(plVar3,"done");
  local_748 = 0;
  local_740 = 4;
  local_738[1] = 0;
  local_738[0] = (ulong)(param_2[0x163] == 0x50);
  local_750 = plVar3;
                    /* try { // try from 000400dd to 000400e1 has its CatchHandler @ 00040753 */
  FUN_0002fd20(local_6f8,local_758,2,1,2);
  local_6e8 = 0;
                    /* try { // try from 00040106 to 0004010a has its CatchHandler @ 0004063e */
  FUN_0002fd20(param_1,local_728,3,1,2);
  puVar4 = local_6e0;
  do {
    puVar5 = puVar4 + -0x18;
    FUN_00024620(puVar4 + -0x10,*puVar5);
    puVar4 = puVar5;
  } while (puVar5 != local_728);
  FUN_00024620(local_738,local_740);
  FUN_00024620(&local_750,local_758[0]);
  FUN_00024620(local_768,local_770[0]);
  FUN_00024620(&local_780,local_788[0]);
  FUN_00024620(local_798,local_7a0[0]);
  FUN_00024620(local_7b0,local_7b8[0]);
  if (param_2[0x163] == 0x50) {
    local_834 = 0xffffffff;
    if (param_2[0x167] != param_2[0x19d]) {
      local_834 = (uint)(param_2[0x167] <= param_2[0x19d]);
    }
    local_788[0] = 0;
    local_780 = (long *)0x0;
                    /* try { // try from 000401f8 to 0004020e has its CatchHandler @ 0004072b */
    FUN_00024620(&local_780,0);
    local_788[0] = 3;
    plVar3 = (long *)FUN_00041fe0(0x20);
    *plVar3 = (long)(plVar3 + 2);
                    /* try { // try from 00040228 to 0004022c has its CatchHandler @ 00040765 */
    FUN_00017bf0(plVar3,"scores");
    local_778 = 0;
    local_7b8[0] = 5;
    local_7b0[1] = 0;
    local_7a0[0] = 5;
    local_798[1] = 0;
    local_7b0[0] = (long)param_2[(long)(*param_2 % 2) * 0x36 + 0x167];
    local_798[0] = (long)param_2[(long)(1 - *param_2 % 2) * 0x36 + 0x167];
    local_780 = plVar3;
                    /* try { // try from 000402d1 to 000402d5 has its CatchHandler @ 0004074b */
    FUN_0002fd20(local_770,local_7b8,2,1,2);
    local_768[1] = 0;
                    /* try { // try from 000402fa to 000402fe has its CatchHandler @ 00040785 */
    FUN_0002fd20(local_728,local_788,2,1,2);
    local_718 = 0;
    local_758[0] = 0;
    local_750 = (long *)0x0;
                    /* try { // try from 00040324 to 0004033a has its CatchHandler @ 00040723 */
    FUN_00024620(&local_750,0);
    local_758[0] = 3;
    plVar3 = (long *)FUN_00041fe0(0x20);
    *plVar3 = (long)(plVar3 + 2);
                    /* try { // try from 00040354 to 00040358 has its CatchHandler @ 00040760 */
    FUN_00017bf0(plVar3,"half_points");
    local_738[0] = 1;
    local_748 = 0;
    if (local_834 != 0xffffffff) {
      local_738[0] = (ulong)(*param_2 % 2 == local_834) * 2;
    }
    local_740 = 5;
    local_738[1] = 0;
    local_750 = plVar3;
                    /* try { // try from 000403cc to 000403d0 has its CatchHandler @ 00040743 */
    FUN_0002fd20(local_710,local_758,2,1,2);
    local_700 = 0;
                    /* try { // try from 000403f5 to 000403f9 has its CatchHandler @ 0004077d */
    FUN_0002fd20(&local_7e8,local_728,2,1,2);
    local_7d8[0] = local_7c8;
                    /* try { // try from 00040420 to 00040424 has its CatchHandler @ 00040733 */
    FUN_00017bf0(local_7d8,"result");
                    /* try { // try from 0004042d to 00040431 has its CatchHandler @ 0004076d */
    puVar4 = (undefined *)FUN_00026330(param_1,local_7d8);
    if (local_7d8[0] != local_7c8) {
      thunk_FUN_000d36e0(local_7d8[0],local_7c8[0] + 1);
    }
    uVar1 = *puVar4;
    *puVar4 = local_7e8._0_1_;
    plVar3 = *(long **)(puVar4 + 8);
    *(long **)(puVar4 + 8) = local_7e0;
    local_7e8 = (undefined *)CONCAT71(local_7e8._1_7_,uVar1);
    local_7e0 = plVar3;
    FUN_00024620(&local_7e0);
    FUN_00024620(local_708,local_710[0]);
    FUN_00024620(local_720,local_728[0]);
    FUN_00024620(local_738,local_740);
    FUN_00024620(&local_750,local_758[0]);
    FUN_00024620(local_768,local_770[0]);
    FUN_00024620(&local_780,local_788[0]);
    FUN_00024620(local_798,local_7a0[0]);
    FUN_00024620(local_7b0,local_7b8[0]);
  }
  FUN_00024620(local_7f8 + 1,local_7f8[0] & 0xff);
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


