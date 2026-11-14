// ===== FUNC 182f0 size=359

void FUN_000182f0(long *param_1,undefined8 *param_2)

{
  undefined8 *puVar1;
  undefined8 *puVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  ulong uVar5;
  ulong uVar6;
  undefined8 *puVar7;
  undefined8 *puVar8;
  word *pwVar9;
  long lVar10;
  undefined8 *puVar11;
  ulong uVar12;
  undefined8 *puVar13;
  undefined8 *puVar14;
  
  puVar1 = (undefined8 *)param_1[1];
  puVar14 = (undefined8 *)param_1[2];
  if (puVar1 != puVar14) {
    uVar3 = *param_2;
    uVar4 = param_2[1];
    *(undefined *)param_2 = 0;
    param_2[1] = 0;
    *puVar1 = uVar3;
    puVar1[1] = uVar4;
    param_1[1] = (long)(puVar1 + 2);
    return;
  }
  puVar2 = (undefined8 *)*param_1;
  uVar5 = (long)puVar1 - (long)puVar2 >> 4;
  if (uVar5 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar12 = 1;
  if (puVar1 != puVar2) {
    uVar12 = uVar5;
  }
  uVar6 = uVar5 + uVar12;
  if (CARRY8(uVar5,uVar12)) {
    lVar10 = 0x7ffffffffffffff0;
  }
  else {
    if (uVar6 == 0) {
      pwVar9 = &Elf64_Ehdr_00000000.e_type;
      lVar10 = 0;
      puVar11 = (undefined8 *)0x0;
      goto LAB_0001838c;
    }
    if (0x7ffffffffffffff < uVar6) {
      uVar6 = 0x7ffffffffffffff;
    }
    lVar10 = uVar6 << 4;
  }
  puVar11 = (undefined8 *)FUN_00041fe0(lVar10);
  puVar14 = (undefined8 *)param_1[2];
  lVar10 = lVar10 + (long)puVar11;
  pwVar9 = (word *)(puVar11 + 2);
LAB_0001838c:
  uVar3 = *param_2;
  uVar4 = param_2[1];
  *(undefined *)param_2 = 0;
  param_2[1] = 0;
  puVar7 = (undefined8 *)((long)puVar11 + ((long)puVar1 - (long)puVar2));
  *puVar7 = uVar3;
  puVar7[1] = uVar4;
  puVar7 = puVar2;
  puVar13 = puVar11;
  if (puVar1 != puVar2) {
    do {
      uVar3 = puVar7[1];
      puVar8 = puVar7 + 2;
      *puVar13 = *puVar7;
      puVar13[1] = uVar3;
      puVar7 = puVar8;
      puVar13 = puVar13 + 2;
    } while (puVar1 != puVar8);
    pwVar9 = (word *)((long)puVar11 + (long)puVar1 + (0x10 - (long)puVar2));
  }
  if (puVar2 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar2,(long)puVar14 - (long)puVar2);
  }
  *param_1 = (long)puVar11;
  param_1[1] = (long)pwVar9;
  param_1[2] = lVar10;
  return;
}


