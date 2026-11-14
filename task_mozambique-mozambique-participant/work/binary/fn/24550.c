// ===== FUNC 24550 size=190

void FUN_00024550(long *param_1,ulong param_2)

{
  long lVar1;
  long lVar2;
  undefined8 *puVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 *puVar7;
  undefined8 *puVar8;
  undefined8 *puVar9;
  undefined8 *puVar10;
  
  if (param_2 >> 0x3b != 0) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::reserve");
  }
  lVar1 = *param_1;
  if (param_2 <= (ulong)(param_1[2] - lVar1 >> 4)) {
    return;
  }
  lVar2 = param_1[1];
  puVar7 = (undefined8 *)FUN_00041fe0(param_2 * 0x10);
  puVar3 = (undefined8 *)param_1[1];
  puVar4 = (undefined8 *)*param_1;
  if (puVar3 != puVar4) {
    puVar8 = puVar4;
    puVar9 = puVar7;
    do {
      uVar5 = *puVar8;
      uVar6 = puVar8[1];
      puVar10 = puVar9 + 2;
      puVar8 = puVar8 + 2;
      *puVar9 = uVar5;
      puVar9[1] = uVar6;
      puVar9 = puVar10;
    } while ((undefined8 *)(((long)puVar3 - (long)puVar4) + (long)puVar7) != puVar10);
  }
  if (puVar4 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar4,param_1[2] - (long)puVar4);
  }
  *param_1 = (long)puVar7;
  param_1[1] = (lVar2 - lVar1) + (long)puVar7;
  param_1[2] = (long)(puVar7 + param_2 * 2);
  return;
}


