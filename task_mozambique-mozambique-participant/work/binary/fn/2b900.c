// ===== FUNC 2b900 size=235

long FUN_0002b900(int *param_1,int *param_2,int *param_3,int *param_4,undefined8 *param_5,
                 undefined8 param_6,long param_7,int *param_8,int *param_9)

{
  long lVar1;
  undefined8 uVar2;
  undefined8 *puVar3;
  void *__dest;
  size_t __n;
  
  if (param_2 != param_1) {
    param_7 = param_7 + 0x1d8;
    do {
      while( true ) {
        if (param_4 == param_3) {
          __n = (long)param_2 - (long)param_1;
          if (param_2 != param_1) {
            param_5 = (undefined8 *)memmove(param_5,param_1,__n);
          }
          goto LAB_0002b9c9;
        }
        lVar1 = param_7 + (long)*param_8 * 0x28;
        if (*(int *)(lVar1 + (long)*param_3 * 4) +
            *(int *)(param_7 + (long)*param_3 * 0x28 + (long)*param_9 * 4) <
            *(int *)(lVar1 + (long)*param_1 * 4) +
            *(int *)(param_7 + (long)*param_1 * 0x28 + (long)*param_9 * 4)) break;
        uVar2 = *(undefined8 *)param_1;
        param_1 = param_1 + 2;
        puVar3 = param_5 + 1;
        *param_5 = uVar2;
        param_5 = puVar3;
        if (param_1 == param_2) goto LAB_0002b9a8;
      }
      uVar2 = *(undefined8 *)param_3;
      puVar3 = param_5 + 1;
      param_3 = param_3 + 2;
      *param_5 = uVar2;
      param_5 = puVar3;
    } while (param_1 != param_2);
  }
LAB_0002b9a8:
  __n = 0;
LAB_0002b9c9:
  __dest = (void *)((long)param_5 + __n);
  if (param_4 != param_3) {
    __dest = memmove(__dest,param_3,(long)param_4 - (long)param_3);
  }
  return (long)__dest + ((long)param_4 - (long)param_3);
}


