// ===== FUNC 2b330 size=348

void FUN_0002b330(undefined8 *param_1,void *param_2,undefined8 *param_3)

{
  void *__dest;
  void *pvVar1;
  void *__src;
  ulong uVar2;
  ulong uVar3;
  void *__dest_00;
  ulong uVar4;
  size_t __n;
  long lVar5;
  size_t __n_00;
  
  pvVar1 = (void *)param_1[1];
  __src = (void *)*param_1;
  uVar2 = (long)pvVar1 - (long)__src >> 3;
  if (uVar2 == 0xfffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar4 = 1;
  if (__src != pvVar1) {
    uVar4 = uVar2;
  }
  uVar3 = uVar2 + uVar4;
  __n = (long)param_2 - (long)__src;
  if (CARRY8(uVar2,uVar4) == false) {
    if (uVar3 != 0) {
      if (0xfffffffffffffff < uVar3) {
        uVar3 = 0xfffffffffffffff;
      }
      lVar5 = uVar3 * 8;
      goto LAB_0002b43a;
    }
    lVar5 = 0;
    __dest_00 = (void *)0x0;
  }
  else {
    lVar5 = 0x7ffffffffffffff8;
LAB_0002b43a:
    __dest_00 = (void *)FUN_00041fe0(lVar5);
    lVar5 = lVar5 + (long)__dest_00;
  }
  __dest = (void *)((long)__dest_00 + __n + 8);
  __n_00 = (long)pvVar1 - (long)param_2;
  *(undefined8 *)((long)__dest_00 + __n) = *param_3;
  if ((long)__n < 1) {
    if (0 < (long)__n_00) {
      memcpy(__dest,param_2,__n_00);
    }
    if (__src == (void *)0x0) goto LAB_0002b3bd;
  }
  else {
    __dest_00 = memmove(__dest_00,__src,__n);
    if (0 < (long)__n_00) {
      memcpy(__dest,param_2,__n_00);
    }
  }
  thunk_FUN_000d36e0(__src,param_1[2] - (long)__src);
LAB_0002b3bd:
  *param_1 = __dest_00;
  param_1[1] = (long)__dest + __n_00;
  param_1[2] = lVar5;
  return;
}


