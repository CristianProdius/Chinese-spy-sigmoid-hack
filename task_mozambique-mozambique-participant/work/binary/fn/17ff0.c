// ===== FUNC 17ff0 size=468

undefined8 * FUN_00017ff0(undefined8 *param_1,undefined8 *param_2,undefined8 *param_3)

{
  undefined uVar1;
  undefined4 uVar2;
  undefined8 *puVar3;
  long lVar4;
  long lVar5;
  undefined8 *puVar6;
  size_t __n;
  undefined8 *puVar7;
  long lVar8;
  undefined8 *puVar9;
  undefined8 *puVar10;
  undefined8 *puVar11;
  long lVar12;
  long lVar13;
  
  if (param_1 == param_2) {
    return param_3;
  }
  if (param_2 == param_3) {
    return param_1;
  }
  lVar4 = (long)param_3 - (long)param_1 >> 3;
  puVar6 = (undefined8 *)((long)param_1 + ((long)param_3 - (long)param_2));
  lVar12 = (long)param_2 - (long)param_1 >> 3;
  puVar9 = param_2;
  if (lVar12 == lVar4 - lVar12) {
    do {
      uVar2 = *(undefined4 *)param_1;
      puVar6 = param_1 + 1;
      uVar1 = *(undefined *)((long)param_1 + 4);
      *param_1 = *puVar9;
      *(undefined4 *)puVar9 = uVar2;
      *(undefined *)((long)puVar9 + 4) = uVar1;
      param_1 = puVar6;
      puVar9 = puVar9 + 1;
    } while (param_2 != puVar6);
  }
  else {
    while( true ) {
      lVar13 = lVar4 - lVar12;
      lVar8 = lVar4;
      lVar5 = lVar4;
      lVar4 = lVar13;
      if (lVar12 < lVar13) {
        do {
          lVar5 = lVar12;
          if (lVar5 == 1) {
            uVar2 = *(undefined4 *)param_1;
            uVar1 = *(undefined *)((long)param_1 + 4);
            puVar9 = param_1 + lVar8;
            if (puVar9 != param_1 + 1) {
              memmove(param_1,param_1 + 1,lVar8 * 8 - 8);
            }
            *(undefined4 *)(puVar9 + -1) = uVar2;
            *(undefined *)((long)puVar9 + -4) = uVar1;
            return puVar6;
          }
          if (0 < lVar13) {
            lVar12 = 0;
            do {
              uVar2 = *(undefined4 *)(param_1 + lVar12);
              uVar1 = *(undefined *)((long)param_1 + lVar12 * 8 + 4);
              param_1[lVar12] = param_1[lVar5 + lVar12];
              *(undefined4 *)(param_1 + lVar5 + lVar12) = uVar2;
              *(undefined *)((long)param_1 + lVar12 * 8 + lVar5 * 8 + 4) = uVar1;
              lVar12 = lVar12 + 1;
            } while (lVar13 != lVar12);
            param_1 = param_1 + lVar13;
          }
          if (lVar8 % lVar5 == 0) {
            return puVar6;
          }
          lVar12 = lVar5 - lVar8 % lVar5;
          lVar13 = lVar5 - lVar12;
          lVar8 = lVar5;
          lVar4 = lVar13;
        } while (lVar12 < lVar13);
      }
      puVar9 = param_1 + lVar5;
      if (lVar4 == 1) break;
      puVar10 = param_1 + lVar12;
      if (0 < lVar12) {
        lVar8 = 0;
        puVar3 = puVar10;
        do {
          puVar7 = puVar9 + -1;
          puVar11 = puVar3 + -1;
          uVar2 = *(undefined4 *)puVar11;
          uVar1 = *(undefined *)((long)puVar3 + -4);
          lVar8 = lVar8 + 1;
          *puVar11 = *puVar7;
          *(undefined4 *)puVar7 = uVar2;
          *(undefined *)((long)puVar9 + -4) = uVar1;
          puVar10 = param_1;
          puVar3 = puVar11;
          puVar9 = puVar7;
        } while (lVar12 != lVar8);
      }
      lVar12 = lVar5 % lVar4;
      param_1 = puVar10;
      if (lVar12 == 0) {
        return puVar6;
      }
    }
    uVar2 = *(undefined4 *)(puVar9 + -1);
    uVar1 = *(undefined *)((long)puVar9 + -4);
    if (param_1 != puVar9 + -1) {
      __n = (long)(puVar9 + -1) - (long)param_1;
      memmove((void *)((long)puVar9 - __n),param_1,__n);
    }
    *(undefined4 *)param_1 = uVar2;
    *(undefined *)((long)param_1 + 4) = uVar1;
    param_2 = puVar6;
  }
  return param_2;
}


