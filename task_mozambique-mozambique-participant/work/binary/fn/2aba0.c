// ===== FUNC 2aba0 size=245

void * FUN_0002aba0(void *param_1,void *param_2,void *param_3,long param_4,long param_5,
                   void *param_6,long param_7)

{
  void *pvVar1;
  size_t sVar2;
  
  if ((param_5 < param_4) && (param_5 <= param_7)) {
    pvVar1 = param_1;
    if (param_5 != 0) {
      sVar2 = (long)param_3 - (long)param_2;
      if (param_3 != param_2) {
        memmove(param_6,param_2,sVar2);
      }
      if (param_1 != param_2) {
        memmove((void *)((long)param_3 - ((long)param_2 - (long)param_1)),param_1,
                (long)param_2 - (long)param_1);
      }
      if (sVar2 != 0) {
        memmove(param_1,param_6,sVar2);
      }
      pvVar1 = (void *)((long)param_1 + sVar2);
    }
  }
  else {
    if (param_7 < param_4) {
      pvVar1 = (void *)FUN_00017ff0(param_1,param_2,param_3);
      return pvVar1;
    }
    pvVar1 = param_3;
    if (param_4 != 0) {
      sVar2 = (long)param_2 - (long)param_1;
      if (param_1 != param_2) {
        memmove(param_6,param_1,sVar2);
      }
      if (param_3 != param_2) {
        memmove(param_1,param_2,(long)param_3 - (long)param_2);
      }
      param_3 = (void *)((long)param_3 - sVar2);
      if (sVar2 != 0) {
        param_3 = memmove(param_3,param_6,sVar2);
      }
      return param_3;
    }
  }
  return pvVar1;
}


