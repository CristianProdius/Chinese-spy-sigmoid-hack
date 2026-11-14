// ===== FUNC 33ab0 size=306

void FUN_00033ab0(undefined8 *param_1,void *param_2,undefined *param_3)

{
  void *__src;
  ulong uVar1;
  ulong uVar2;
  void *__dest;
  void *pvVar3;
  size_t __n;
  long lVar4;
  size_t __n_00;
  long lVar5;
  ulong uVar6;
  
  __src = (void *)*param_1;
  uVar2 = param_1[1] - (long)__src;
  if (uVar2 == 0x7fffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  __n = (long)param_2 - (long)__src;
  uVar6 = 1;
  if (uVar2 != 0) {
    uVar1 = uVar2 * 2;
    uVar6 = 0x7fffffffffffffff;
    if (uVar1 < 0x8000000000000000) {
      uVar6 = uVar1;
    }
    if (uVar1 < uVar2) {
      uVar6 = 0x7fffffffffffffff;
    }
  }
  __n_00 = param_1[1] - (long)param_2;
  __dest = (void *)FUN_00041fe0(uVar6);
  *(undefined *)((long)__dest + __n) = *param_3;
  if ((long)__n < 1) {
    pvVar3 = (void *)(__n + 1 + (long)__dest);
    if (0 < (long)__n_00) {
      pvVar3 = memcpy(pvVar3,param_2,__n_00);
    }
    lVar5 = __n_00 + (long)pvVar3;
    if (__src == (void *)0x0) goto LAB_00033b54;
LAB_00033ba9:
    lVar4 = param_1[2] - (long)__src;
  }
  else {
    memmove(__dest,__src,__n);
    pvVar3 = (void *)(__n + 1 + (long)__dest);
    if (0 < (long)__n_00) {
      pvVar3 = memcpy(pvVar3,param_2,__n_00);
      lVar5 = __n_00 + (long)pvVar3;
      goto LAB_00033ba9;
    }
    lVar5 = __n_00 + (long)pvVar3;
    lVar4 = param_1[2] - (long)__src;
  }
  thunk_FUN_000d36e0(__src,lVar4);
LAB_00033b54:
  *param_1 = __dest;
  param_1[1] = lVar5;
  param_1[2] = (long)__dest + uVar6;
  return;
}


