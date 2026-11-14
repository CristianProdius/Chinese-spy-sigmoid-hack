// ===== FUNC 1a9c0 size=124

void FUN_0001a9c0(long param_1,long param_2,long param_3)

{
  double *pdVar1;
  double dVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  
  if (0 < param_2 - param_1) {
    dVar2 = *(double *)(param_3 + 0x158);
    lVar5 = (param_2 - param_1 >> 5) * 0x2e8ba2e8ba2e8ba3;
    do {
      while( true ) {
        lVar4 = lVar5 >> 1;
        lVar3 = lVar4 * 0x160 + param_1;
        pdVar1 = (double *)(lVar3 + 0x158);
        if (NAN(dVar2) || NAN(*pdVar1)) break;
        if (dVar2 == *pdVar1) {
          if (*(int *)(lVar3 + 0x120) <= *(int *)(param_3 + 0x120)) break;
        }
        else if (dVar2 < *pdVar1 || dVar2 == *pdVar1) break;
        lVar5 = lVar4;
        if (lVar4 < 1) {
          return;
        }
      }
      param_1 = lVar3 + 0x160;
      lVar5 = (lVar5 - lVar4) + -1;
    } while (0 < lVar5);
  }
  return;
}


