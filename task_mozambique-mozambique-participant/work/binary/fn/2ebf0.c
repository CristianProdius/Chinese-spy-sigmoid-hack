// ===== FUNC 2ebf0 size=368

void FUN_0002ebf0(long *param_1,undefined8 *param_2,undefined *param_3)

{
  undefined *puVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  ulong uVar6;
  void *pvVar7;
  undefined8 *puVar8;
  undefined8 *puVar9;
  undefined8 *puVar10;
  ulong uVar11;
  ulong uVar12;
  long lVar13;
  
  puVar2 = (undefined8 *)param_1[1];
  puVar3 = (undefined8 *)*param_1;
  uVar11 = (long)puVar2 - (long)puVar3 >> 4;
  if (uVar11 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar6 = 1;
  if (puVar3 != puVar2) {
    uVar6 = uVar11;
  }
  uVar12 = uVar11 + uVar6;
  if (CARRY8(uVar11,uVar6) == false) {
    if (uVar12 == 0) {
      puVar8 = (undefined8 *)0x0;
      goto LAB_0002ec55;
    }
    if (0x7ffffffffffffff < uVar12) {
      uVar12 = 0x7ffffffffffffff;
    }
    lVar13 = uVar12 << 4;
  }
  else {
    lVar13 = 0x7ffffffffffffff0;
    uVar12 = 0x7ffffffffffffff;
  }
  puVar8 = (undefined8 *)FUN_00041fe0(lVar13);
LAB_0002ec55:
  puVar1 = (undefined *)((long)puVar8 + ((long)param_2 - (long)puVar3));
  *puVar1 = *param_3;
                    /* try { // try from 0002ec70 to 0002ec74 has its CatchHandler @ 0002ed6e */
  FUN_000210f0(puVar1 + 8);
  puVar9 = puVar8;
  if (param_2 != puVar3) {
    puVar9 = puVar3;
    puVar10 = puVar8;
    do {
      uVar4 = *puVar9;
      uVar5 = puVar9[1];
      puVar9 = puVar9 + 2;
      *puVar10 = uVar4;
      puVar10[1] = uVar5;
      puVar10 = puVar10 + 2;
    } while (param_2 != puVar9);
    puVar9 = (undefined8 *)(((long)param_2 - (long)puVar3) + (long)puVar8);
  }
  puVar9 = puVar9 + 2;
  if (param_2 != puVar2) {
    pvVar7 = memcpy(puVar9,param_2,(long)puVar2 - (long)param_2);
    puVar9 = (undefined8 *)((long)pvVar7 + ((long)puVar2 - (long)param_2));
  }
  if (puVar3 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar3,param_1[2] - (long)puVar3);
  }
  *param_1 = (long)puVar8;
  param_1[1] = (long)puVar9;
  param_1[2] = (long)(puVar8 + uVar12 * 2);
  return;
}


