// ===== FUNC 13cc9 size=233

undefined8 * FUN_00013cc9(undefined8 *param_1,undefined4 param_2,undefined8 param_3)

{
  long in_FS_OFFSET;
  undefined8 local_c0 [4];
  undefined local_a0 [32];
  undefined local_80 [32];
  undefined local_60 [32];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_00018b10(local_60,&DAT_000e3155);
                    /* try { // try from 00013d1b to 00013d1f has its CatchHandler @ 00013db7 */
  FUN_00018b10(local_a0,"type_error");
                    /* try { // try from 00013d2e to 00013d32 has its CatchHandler @ 00013daa */
  FUN_0001bf50(local_80,local_a0,param_2);
                    /* try { // try from 00013d46 to 00013d4a has its CatchHandler @ 00013d9d */
  FUN_00021000(local_c0,local_80,local_60,param_3);
  FUN_000b07c0(local_80);
  FUN_000b07c0(local_a0);
  FUN_000b07c0(local_60);
                    /* try { // try from 00013d6e to 00013d72 has its CatchHandler @ 00013dca */
  FUN_0001bf10(param_1,param_2,local_c0[0]);
  *param_1 = &PTR_FUN_0011bae8;
  FUN_000b07c0(local_c0);
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


