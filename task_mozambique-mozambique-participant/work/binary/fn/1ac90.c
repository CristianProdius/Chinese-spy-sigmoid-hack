// ===== FUNC 1ac90 size=353

void FUN_0001ac90(undefined8 *param_1,undefined *param_2)

{
  undefined *puVar1;
  undefined uVar2;
  undefined8 *puVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  ulong uVar6;
  ulong uVar7;
  undefined8 *puVar8;
  undefined8 *puVar9;
  long lVar10;
  undefined8 *puVar11;
  ulong uVar12;
  word *pwVar13;
  undefined8 *puVar14;
  undefined8 *puVar15;
  
  puVar3 = (undefined8 *)param_1[1];
  puVar15 = (undefined8 *)param_1[2];
  if (puVar3 != puVar15) {
    uVar2 = *param_2;
    puVar3[1] = 0;
    *(undefined *)puVar3 = 4;
    *(undefined *)(puVar3 + 1) = uVar2;
    param_1[1] = puVar3 + 2;
    return;
  }
  puVar4 = (undefined8 *)*param_1;
  uVar6 = (long)puVar3 - (long)puVar4 >> 4;
  if (uVar6 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar12 = 1;
  if (puVar3 != puVar4) {
    uVar12 = uVar6;
  }
  uVar7 = uVar6 + uVar12;
  if (CARRY8(uVar6,uVar12)) {
    lVar10 = 0x7ffffffffffffff0;
  }
  else {
    if (uVar7 == 0) {
      pwVar13 = &Elf64_Ehdr_00000000.e_type;
      lVar10 = 0;
      puVar11 = (undefined8 *)0x0;
      goto LAB_0001ad2c;
    }
    if (0x7ffffffffffffff < uVar7) {
      uVar7 = 0x7ffffffffffffff;
    }
    lVar10 = uVar7 << 4;
  }
  puVar11 = (undefined8 *)FUN_00041fe0(lVar10);
  puVar15 = (undefined8 *)param_1[2];
  lVar10 = lVar10 + (long)puVar11;
  pwVar13 = (word *)(puVar11 + 2);
LAB_0001ad2c:
  uVar2 = *param_2;
  puVar1 = (undefined *)((long)puVar11 + ((long)puVar3 - (long)puVar4));
  *(undefined8 *)(puVar1 + 8) = 0;
  *puVar1 = 4;
  puVar1[8] = uVar2;
  puVar8 = puVar4;
  puVar14 = puVar11;
  if (puVar3 != puVar4) {
    do {
      uVar5 = puVar8[1];
      puVar9 = puVar8 + 2;
      *puVar14 = *puVar8;
      puVar14[1] = uVar5;
      puVar8 = puVar9;
      puVar14 = puVar14 + 2;
    } while (puVar3 != puVar9);
    pwVar13 = (word *)((long)puVar11 + (long)((long)puVar3 + (0x10 - (long)puVar4)));
  }
  if (puVar4 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar4,(long)puVar15 - (long)puVar4);
  }
  *param_1 = puVar11;
  param_1[1] = pwVar13;
  param_1[2] = lVar10;
  return;
}


