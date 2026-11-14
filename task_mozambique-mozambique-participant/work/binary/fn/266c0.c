// ===== FUNC 266c0 size=156

undefined8 FUN_000266c0(undefined8 param_1,char *param_2)

{
  size_t sVar1;
  undefined8 uVar2;
  long in_FS_OFFSET;
  long *local_58 [2];
  long local_48 [3];
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  local_58[0] = local_48;
  if (param_2 == (char *)0x0) {
                    /* WARNING: Subroutine does not return */
    FUN_00015d21("basic_string: construction from null is not valid");
  }
  sVar1 = strlen(param_2);
  FUN_00017bf0(local_58,param_2,param_2 + sVar1);
                    /* try { // try from 0002670e to 00026712 has its CatchHandler @ 0002675c */
  uVar2 = FUN_00026330(param_1,local_58);
  if (local_58[0] != local_48) {
    thunk_FUN_000d36e0(local_58[0],local_48[0] + 1);
  }
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar2;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


