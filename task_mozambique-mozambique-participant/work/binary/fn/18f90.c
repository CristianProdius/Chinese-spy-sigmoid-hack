// ===== FUNC 18f90 size=572

undefined8 * FUN_00018f90(undefined8 *param_1,undefined4 param_2,undefined8 *param_3)

{
  long in_FS_OFFSET;
  undefined *local_c8;
  long local_c0;
  undefined local_b8;
  undefined7 uStack_b7;
  long *local_a8 [2];
  long local_98 [2];
  long *local_88;
  ulong local_80;
  long local_78 [2];
  long *local_68;
  ulong local_60;
  long local_58 [3];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  local_68 = local_58;
  FUN_00017bf0(&local_68,&DAT_000e3155,&DAT_000e3155);
  local_a8[0] = local_98;
                    /* try { // try from 00019012 to 00019016 has its CatchHandler @ 000191d4 */
  FUN_00017bf0(local_a8,"out_of_range");
                    /* try { // try from 0001902a to 0001902e has its CatchHandler @ 000191dc */
  FUN_0001bf50(&local_88,local_a8,param_2);
  local_c0 = 0;
  local_b8 = 0;
  local_c8 = &local_b8;
                    /* try { // try from 00019060 to 000190e6 has its CatchHandler @ 000191e4 */
  FUN_000b1110(&local_c8,local_60 + local_80 + param_3[1]);
  if (0x3fffffffffffffffU - local_c0 < local_80) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 000191aa to 000191cb has its CatchHandler @ 000191e4 */
    FUN_00015e26("basic_string::append",local_88);
  }
  FUN_000b2500(&local_c8);
  if (0x3fffffffffffffffU - local_c0 < local_60) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",local_68);
  }
  FUN_000b2500(&local_c8);
  if (0x3fffffffffffffffU - local_c0 < (ulong)param_3[1]) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",*param_3);
  }
  FUN_000b2500(&local_c8);
  if (local_88 != local_78) {
    thunk_FUN_000d36e0(local_88,local_78[0] + 1);
  }
  if (local_a8[0] != local_98) {
    thunk_FUN_000d36e0(local_a8[0],local_98[0] + 1);
  }
  if (local_68 != local_58) {
    thunk_FUN_000d36e0(local_68,local_58[0] + 1);
  }
  *param_1 = &PTR_FUN_0011ba70;
  *(undefined4 *)(param_1 + 1) = param_2;
                    /* try { // try from 00019154 to 00019158 has its CatchHandler @ 000191cc */
  FUN_00053220(param_1 + 2,local_c8);
  *param_1 = &PTR_FUN_0011bb10;
  if (local_c8 != &local_b8) {
    thunk_FUN_000d36e0(local_c8,CONCAT71(uStack_b7,local_b8) + 1);
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


