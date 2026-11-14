// ===== FUNC 1a7a0 size=293

void * FUN_0001a7a0(long *param_1,long *param_2)

{
  long lVar1;
  char *__s1;
  int iVar2;
  void *in_RAX;
  void *pvVar3;
  void *pvVar4;
  void *pvVar5;
  size_t __n;
  ulong __n_00;
  void *pvVar6;
  
  if (param_2 == param_1) {
    return in_RAX;
  }
  pvVar6 = (void *)param_2[1];
  pvVar3 = (void *)*param_2;
  pvVar5 = (void *)*param_1;
  __n_00 = (long)pvVar6 - (long)pvVar3;
  if (__n_00 <= (ulong)(param_1[2] - (long)pvVar5)) {
    pvVar4 = (void *)param_1[1];
    __n = (long)pvVar4 - (long)pvVar5;
    if (__n < __n_00) {
      if (__n != 0) {
        memmove(pvVar5,pvVar3,__n);
        pvVar4 = (void *)param_1[1];
        pvVar5 = (void *)*param_1;
        pvVar6 = (void *)param_2[1];
        pvVar3 = (void *)*param_2;
        __n = (long)pvVar4 - (long)pvVar5;
      }
      pvVar3 = (void *)((long)pvVar3 + __n);
      if (pvVar3 != pvVar6) {
        pvVar3 = memmove(pvVar4,pvVar3,(long)pvVar6 - (long)pvVar3);
        param_1[1] = __n_00 + *param_1;
        return pvVar3;
      }
    }
    else if (pvVar6 != pvVar3) {
      pvVar3 = memmove(pvVar5,pvVar3,__n_00);
      param_1[1] = __n_00 + *param_1;
      return pvVar3;
    }
    param_1[1] = __n_00 + (long)pvVar5;
    return pvVar4;
  }
  if (__n_00 < 0x7ffffffffffffffd) {
    pvVar4 = (void *)FUN_00041fe0(__n_00);
    pvVar5 = pvVar4;
    if (pvVar6 != pvVar3) {
      pvVar5 = memcpy(pvVar4,pvVar3,__n_00);
    }
    lVar1 = *param_1;
    if (lVar1 != 0) {
      pvVar5 = (void *)thunk_FUN_000d36e0(lVar1,param_1[2] - lVar1);
    }
    *param_1 = (long)pvVar4;
    param_1[2] = __n_00 + (long)pvVar4;
    param_1[1] = __n_00 + (long)pvVar4;
    return pvVar5;
  }
  FUN_00015c88();
  if ((param_2 != (long *)&DAT_000e2d90) &&
     (__s1 = (char *)param_2[1], __s1 != "St19_Sp_make_shared_tag")) {
    if (*__s1 == '*') {
      return (void *)0x0;
    }
    iVar2 = strcmp(__s1,"St19_Sp_make_shared_tag");
    if (iVar2 != 0) {
      return (void *)0x0;
    }
  }
  return (void *)((long)pvVar5 + 0x10);
}


