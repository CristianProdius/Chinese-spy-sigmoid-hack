// ===== FUNC 18b10 size=194

void FUN_00018b10(long *param_1,char *param_2)

{
  size_t __n;
  long *__dest;
  long in_FS_OFFSET;
  size_t local_38;
  long local_30;
  
  __dest = param_1 + 2;
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  *param_1 = (long)__dest;
  if (param_2 == (char *)0x0) {
                    /* WARNING: Subroutine does not return */
    FUN_00015d21("basic_string: construction from null is not valid");
  }
  __n = strlen(param_2);
  local_38 = __n;
  if (__n < 0x10) {
    if (__n == 1) {
      *(char *)(param_1 + 2) = *param_2;
      goto LAB_00018b63;
    }
    if (__n == 0) goto LAB_00018b63;
  }
  else {
    __dest = (long *)FUN_000b0760(param_1,&local_38,0);
    *param_1 = (long)__dest;
    param_1[2] = local_38;
  }
  memcpy(__dest,param_2,__n);
  __dest = (long *)*param_1;
LAB_00018b63:
  param_1[1] = local_38;
  *(undefined *)((long)__dest + local_38) = 0;
  if (local_30 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


