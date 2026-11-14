// ===== FUNC 1a930 size=128

void FUN_0001a930(long param_1,long param_2,long param_3)

{
  double dVar1;
  double dVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  
  if (0 < param_2 - param_1) {
    dVar1 = *(double *)(param_3 + 0x158);
    lVar5 = (param_2 - param_1 >> 5) * 0x2e8ba2e8ba2e8ba3;
    do {
      while( true ) {
        lVar4 = lVar5 >> 1;
        lVar3 = lVar4 * 0x160 + param_1;
        dVar2 = *(double *)(lVar3 + 0x158);
        if (!NAN(dVar2) && !NAN(dVar1)) break;
LAB_0001a99d:
        lVar5 = lVar4;
        if (lVar4 < 1) {
          return;
        }
      }
      if (dVar2 == dVar1) {
        if (*(int *)(lVar3 + 0x120) < *(int *)(param_3 + 0x120)) goto LAB_0001a960;
        goto LAB_0001a99d;
      }
      if (dVar2 <= dVar1) goto LAB_0001a99d;
LAB_0001a960:
      param_1 = lVar3 + 0x160;
      lVar5 = (lVar5 - lVar4) + -1;
    } while (0 < lVar5);
  }
  return;
}


