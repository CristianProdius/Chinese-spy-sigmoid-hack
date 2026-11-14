// ===== FUNC 13ba0 size=233

undefined8 * FUN_00013ba0(undefined8 *param_1,undefined4 param_2,undefined8 param_3)

{
  long in_FS_OFFSET;
  undefined8 local_c0 [4];
  undefined local_a0 [32];
  undefined local_80 [32];
  undefined local_60 [32];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_00018b10(local_60,&DAT_000e3155);
                    /* try { // try from 00013bf2 to 00013bf6 has its CatchHandler @ 00013c8e */
  FUN_00018b10(local_a0,"type_error");
                    /* try { // try from 00013c05 to 00013c09 has its CatchHandler @ 00013c81 */
  FUN_0001bf50(local_80,local_a0,param_2);
                    /* try { // try from 00013c1d to 00013c21 has its CatchHandler @ 00013c74 */
  FUN_00021000(local_c0,local_80,local_60,param_3);
  FUN_000b07c0(local_80);
  FUN_000b07c0(local_a0);
  FUN_000b07c0(local_60);
                    /* try { // try from 00013c45 to 00013c49 has its CatchHandler @ 00013ca1 */
  FUN_0001bf10(param_1,param_2,local_c0[0]);
  *param_1 = &PTR_FUN_0011bae8;
  FUN_000b07c0(local_c0);
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


