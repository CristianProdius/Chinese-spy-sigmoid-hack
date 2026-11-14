// ===== FUNC 268c0 size=240

long * FUN_000268c0(undefined8 *param_1,undefined8 *param_2,long *param_3)

{
  undefined4 uVar1;
  ulong __n;
  undefined *__src;
  long lVar2;
  long *__dest;
  long *plVar3;
  undefined8 *puVar4;
  long in_FS_OFFSET;
  ulong local_48;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_2 != param_1) {
    plVar3 = param_3;
    do {
      __n = param_1[1];
      __dest = plVar3 + 2;
      *plVar3 = (long)__dest;
      __src = (undefined *)*param_1;
      local_48 = __n;
      if (__n < 0x10) {
        if (__n == 1) {
          *(undefined *)(plVar3 + 2) = *__src;
        }
        else if (__n != 0) goto LAB_00026969;
      }
      else {
                    /* try { // try from 00026955 to 00026959 has its CatchHandler @ 000269bf */
        __dest = (long *)FUN_000b0760(plVar3,&local_48,0);
        *plVar3 = (long)__dest;
        plVar3[2] = local_48;
LAB_00026969:
        memcpy(__dest,__src,__n);
        __dest = (long *)*plVar3;
      }
      plVar3[1] = local_48;
      puVar4 = param_1 + 7;
      param_3 = plVar3 + 7;
      *(undefined *)((long)__dest + local_48) = 0;
      lVar2 = param_1[5];
      uVar1 = *(undefined4 *)(param_1 + 6);
      plVar3[4] = param_1[4];
      plVar3[5] = lVar2;
      *(undefined4 *)(plVar3 + 6) = uVar1;
      plVar3 = param_3;
      param_1 = puVar4;
    } while (param_2 != puVar4);
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_3;
}


