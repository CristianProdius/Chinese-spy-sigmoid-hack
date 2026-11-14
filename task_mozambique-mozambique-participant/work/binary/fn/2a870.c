// ===== FUNC 2a870 size=139

int * FUN_0002a870(int *param_1,long param_2,int *param_3)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  long param_7;
  int *param_8;
  int *param_9;
  
  if (0 < param_2 - (long)param_1) {
    param_7 = param_7 + 0x1d8;
    lVar1 = param_7 + (long)*param_8 * 0x28;
    lVar2 = param_2 - (long)param_1 >> 3;
    do {
      while( true ) {
        lVar3 = lVar2 >> 1;
        lVar4 = (long)param_1[lVar3 * 2];
        if (*(int *)(lVar1 + lVar4 * 4) + *(int *)(param_7 + lVar4 * 0x28 + (long)*param_9 * 4) <=
            *(int *)(lVar1 + (long)*param_3 * 4) +
            *(int *)(param_7 + (long)*param_3 * 0x28 + (long)*param_9 * 4)) break;
        lVar2 = lVar3;
        if (lVar3 < 1) {
          return param_1;
        }
      }
      param_1 = param_1 + lVar3 * 2 + 2;
      lVar2 = (lVar2 - lVar3) + -1;
    } while (0 < lVar2);
  }
  return param_1;
}


