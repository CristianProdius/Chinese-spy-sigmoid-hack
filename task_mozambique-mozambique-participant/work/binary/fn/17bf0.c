// ===== FUNC 17bf0 size=159

void FUN_00017bf0(undefined8 *param_1,undefined *param_2,long param_3)

{
  undefined *__dest;
  ulong __n;
  long in_FS_OFFSET;
  ulong local_28;
  long local_20;
  
  __n = param_3 - (long)param_2;
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  local_28 = __n;
  if (__n < 0x10) {
    __dest = (undefined *)*param_1;
    if (__n == 1) {
      *__dest = *param_2;
      __dest = (undefined *)*param_1;
      goto LAB_00017c34;
    }
    if (__n == 0) goto LAB_00017c34;
  }
  else {
    __dest = (undefined *)FUN_000b0760(param_1,&local_28,0);
    *param_1 = __dest;
    param_1[2] = local_28;
  }
  memcpy(__dest,param_2,__n);
  __dest = (undefined *)*param_1;
LAB_00017c34:
  param_1[1] = local_28;
  __dest[local_28] = 0;
  if (local_20 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


