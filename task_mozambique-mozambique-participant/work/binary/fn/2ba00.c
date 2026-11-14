// ===== FUNC 2ba00 size=242

long FUN_0002ba00(int *param_1,int *param_2,int *param_3,int *param_4,undefined8 *param_5,
                 undefined8 param_6,long param_7,int *param_8,int *param_9)

{
  long lVar1;
  undefined8 uVar2;
  undefined8 *puVar3;
  void *__dest;
  
  if ((param_3 != param_4) && (param_1 != param_2)) {
    param_7 = param_7 + 0x1d8;
    puVar3 = param_5;
    do {
      lVar1 = param_7 + (long)*param_8 * 0x28;
      if (*(int *)(lVar1 + (long)*param_3 * 4) +
          *(int *)(param_7 + (long)*param_3 * 0x28 + (long)*param_9 * 4) <
          *(int *)(lVar1 + (long)*param_1 * 4) +
          *(int *)(param_7 + (long)*param_1 * 0x28 + (long)*param_9 * 4)) {
        uVar2 = *(undefined8 *)param_3;
        param_3 = param_3 + 2;
        *puVar3 = uVar2;
      }
      else {
        uVar2 = *(undefined8 *)param_1;
        param_1 = param_1 + 2;
        *puVar3 = uVar2;
      }
      param_5 = puVar3 + 1;
    } while ((param_1 != param_2) && (param_5 = puVar3 + 1, puVar3 = param_5, param_3 != param_4));
  }
  if (param_2 != param_1) {
    param_5 = (undefined8 *)memmove(param_5,param_1,(long)param_2 - (long)param_1);
  }
  __dest = (void *)((long)param_5 + ((long)param_2 - (long)param_1));
  if (param_4 != param_3) {
    __dest = memmove(__dest,param_3,(long)param_4 - (long)param_3);
  }
  return (long)__dest + ((long)param_4 - (long)param_3);
}


