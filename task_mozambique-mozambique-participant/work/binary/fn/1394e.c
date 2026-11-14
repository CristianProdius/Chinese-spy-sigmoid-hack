// ===== FUNC 1394e size=233

undefined8 * FUN_0001394e(undefined8 *param_1,undefined4 param_2,undefined8 param_3)

{
  long in_FS_OFFSET;
  undefined8 local_c0 [4];
  undefined local_a0 [32];
  undefined local_80 [32];
  undefined local_60 [32];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_00018b10(local_60,&DAT_000e3155);
                    /* try { // try from 000139a0 to 000139a4 has its CatchHandler @ 00013a3c */
  FUN_00018b10(local_a0,"invalid_iterator");
                    /* try { // try from 000139b3 to 000139b7 has its CatchHandler @ 00013a2f */
  FUN_0001bf50(local_80,local_a0,param_2);
                    /* try { // try from 000139cb to 000139cf has its CatchHandler @ 00013a22 */
  FUN_00021000(local_c0,local_80,local_60,param_3);
  FUN_000b07c0(local_80);
  FUN_000b07c0(local_a0);
  FUN_000b07c0(local_60);
                    /* try { // try from 000139f3 to 000139f7 has its CatchHandler @ 00013a4f */
  FUN_0001bf10(param_1,param_2,local_c0[0]);
  *param_1 = &PTR_FUN_0011bac0;
  FUN_000b07c0(local_c0);
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


