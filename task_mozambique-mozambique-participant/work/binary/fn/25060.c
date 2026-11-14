// ===== FUNC 25060 size=347

void FUN_00025060(int *param_1,int *param_2)

{
  long lVar1;
  long lVar2;
  undefined uVar3;
  int iVar4;
  int *piVar5;
  long lVar6;
  int iVar7;
  int *piVar8;
  long lVar9;
  int *piVar10;
  long param_7;
  int *param_8;
  int *param_9;
  
  if (param_1 != param_2) {
    for (piVar8 = param_1 + 2; piVar8 != param_2; piVar8 = piVar8 + 2) {
      while( true ) {
        iVar4 = *piVar8;
        lVar9 = (long)iVar4;
        uVar3 = *(undefined *)(piVar8 + 1);
        lVar6 = (long)*param_9;
        lVar1 = param_7 + 0x1d8 + (long)*param_8 * 0x28;
        lVar2 = param_7 + 0x1d8 + lVar9 * 0x28;
        iVar7 = *(int *)(lVar2 + lVar6 * 4) + *(int *)(lVar1 + lVar9 * 4);
        if (iVar7 < *(int *)(lVar1 + (long)*param_1 * 4) +
                    *(int *)(param_7 + 0x1d8 + (long)*param_1 * 0x28 + lVar6 * 4)) break;
        piVar5 = piVar8 + -2;
        piVar10 = piVar8;
        if (iVar7 < *(int *)(lVar1 + (long)piVar8[-2] * 4) +
                    *(int *)(param_7 + 0x1d8 + (long)piVar8[-2] * 0x28 + lVar6 * 4)) {
          do {
            piVar10 = piVar5;
            *(undefined8 *)(piVar10 + 2) = *(undefined8 *)piVar10;
            lVar1 = param_7 + 0x1d8 + (long)*param_8 * 0x28;
            lVar6 = (long)piVar10[-2];
            piVar5 = piVar10 + -2;
          } while (*(int *)(lVar2 + (long)*param_9 * 4) + *(int *)(lVar1 + lVar9 * 4) <
                   *(int *)(lVar1 + lVar6 * 4) +
                   *(int *)(param_7 + 0x1d8 + lVar6 * 0x28 + (long)*param_9 * 4));
        }
        *piVar10 = iVar4;
        piVar8 = piVar8 + 2;
        *(undefined *)(piVar10 + 1) = uVar3;
        if (param_2 == piVar8) {
          return;
        }
      }
      if (param_1 != piVar8) {
        memmove(param_1 + 2,param_1,(long)piVar8 - (long)param_1);
      }
      *param_1 = iVar4;
      *(undefined *)(param_1 + 1) = uVar3;
    }
  }
  return;
}


