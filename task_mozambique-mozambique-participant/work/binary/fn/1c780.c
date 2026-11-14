// ===== FUNC 1c780 size=180

void FUN_0001c780(undefined8 *param_1,undefined8 *param_2)

{
  ulong __n;
  undefined *__src;
  undefined8 uVar1;
  undefined8 uVar2;
  undefined8 *__dest;
  long in_FS_OFFSET;
  ulong local_38;
  long local_30;
  
  __dest = param_1 + 2;
  __n = param_2[1];
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  *param_1 = __dest;
  __src = (undefined *)*param_2;
  local_38 = __n;
  if (__n < 0x10) {
    if (__n == 1) {
      *(undefined *)(param_1 + 2) = *__src;
      goto LAB_0001c7c6;
    }
    if (__n == 0) goto LAB_0001c7c6;
  }
  else {
    __dest = (undefined8 *)FUN_000b0760(param_1,&local_38,0);
    *param_1 = __dest;
    param_1[2] = local_38;
  }
  memcpy(__dest,__src,__n);
  __dest = (undefined8 *)*param_1;
LAB_0001c7c6:
  param_1[1] = local_38;
  *(undefined *)((long)__dest + local_38) = 0;
  uVar1 = param_2[4];
  uVar2 = param_2[5];
  *(undefined4 *)(param_1 + 6) = *(undefined4 *)(param_2 + 6);
  param_1[4] = uVar1;
  param_1[5] = uVar2;
  if (local_30 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


