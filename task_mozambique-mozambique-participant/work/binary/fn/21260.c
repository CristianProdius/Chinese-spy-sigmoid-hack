// ===== FUNC 21260 size=799

void FUN_00021260(long *param_1,undefined8 *param_2,undefined8 *param_3)

{
  undefined4 uVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  long lVar4;
  void *pvVar5;
  undefined8 uVar6;
  ulong uVar7;
  ulong uVar8;
  undefined8 uVar9;
  ulong uVar10;
  size_t sVar11;
  undefined8 *puVar12;
  undefined8 *puVar13;
  undefined8 *puVar14;
  word *pwVar15;
  word *pwVar16;
  undefined8 *local_60;
  long local_48;
  
  puVar2 = (undefined8 *)param_1[1];
  puVar3 = (undefined8 *)*param_1;
  uVar7 = ((long)puVar2 - (long)puVar3 >> 3) * 0x6db6db6db6db6db7;
  if (uVar7 == 0x249249249249249) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar10 = 1;
  if (puVar3 != puVar2) {
    uVar10 = uVar7;
  }
  uVar8 = uVar7 + uVar10;
  if (CARRY8(uVar7,uVar10) == false) {
    if (uVar8 == 0) {
      local_48 = 0;
      pwVar16 = &Elf64_Ehdr_00000000.e_phnum;
      local_60 = (undefined8 *)0x0;
      goto LAB_000212ee;
    }
    if (0x249249249249249 < uVar8) {
      uVar8 = 0x249249249249249;
    }
    local_48 = uVar8 * 0x38;
  }
  else {
    local_48 = 0x7ffffffffffffff8;
  }
  local_60 = (undefined8 *)FUN_00041fe0(local_48);
  pwVar16 = (word *)(local_60 + 7);
  local_48 = (long)local_60 + local_48;
LAB_000212ee:
  puVar13 = param_3 + 2;
  lVar4 = param_3[1];
  puVar14 = (undefined8 *)(((long)param_2 - (long)puVar3) + (long)local_60);
  pvVar5 = (void *)*param_3;
  *puVar14 = puVar14 + 2;
  if ((undefined8 *)pvVar5 == puVar13) {
    sVar11 = lVar4 + 1;
    if (sVar11 != 0) {
      memcpy(puVar14 + 2,puVar13,sVar11);
    }
  }
  else {
    *puVar14 = pvVar5;
    puVar14[2] = param_3[2];
  }
  uVar9 = param_3[4];
  uVar6 = param_3[5];
  uVar1 = *(undefined4 *)(param_3 + 6);
  puVar14[1] = lVar4;
  *param_3 = puVar13;
  param_3[1] = 0;
  *(undefined *)(param_3 + 2) = 0;
  *(undefined4 *)(puVar14 + 6) = uVar1;
  puVar14[4] = uVar9;
  puVar14[5] = uVar6;
  puVar13 = puVar3;
  puVar14 = local_60;
  if (param_2 != puVar3) {
    do {
      *puVar14 = puVar14 + 2;
      puVar12 = (undefined8 *)*puVar13;
      if (puVar12 == puVar13 + 2) {
        uVar9 = 0xffffffffffffffff;
        if (puVar13[1] + 1 != 0) {
          memcpy(puVar14 + 2,puVar12,puVar13[1] + 1);
          uVar9 = puVar13[1];
        }
      }
      else {
        uVar9 = puVar13[2];
        *puVar14 = puVar12;
        puVar14[2] = uVar9;
        uVar9 = puVar13[1];
      }
      puVar14[1] = uVar9;
      puVar12 = puVar13 + 7;
      uVar9 = puVar13[4];
      uVar6 = puVar13[5];
      *(undefined4 *)(puVar14 + 6) = *(undefined4 *)(puVar13 + 6);
      puVar14[4] = uVar9;
      puVar14[5] = uVar6;
      puVar13 = puVar12;
      puVar14 = puVar14 + 7;
    } while (param_2 != puVar12);
    pwVar16 = (word *)(local_60 +
                      ((((ulong)((long)param_2 + (-0x38 - (long)puVar3)) >> 3) * 0xdb6db6db6db6db7 &
                       0x1fffffffffffffff) + 2) * 7);
  }
  puVar13 = param_2;
  pwVar15 = pwVar16;
  if (param_2 != puVar2) {
    do {
      puVar14 = (undefined8 *)*puVar13;
      lVar4 = puVar13[1];
      *(word **)pwVar15 = pwVar15 + 8;
      if (puVar14 == puVar13 + 2) {
        sVar11 = lVar4 + 1;
        if (sVar11 != 0) {
          memcpy(pwVar15 + 8,puVar14,sVar11);
        }
      }
      else {
        uVar9 = puVar13[2];
        *(undefined8 **)pwVar15 = puVar14;
        *(undefined8 *)(pwVar15 + 8) = uVar9;
      }
      uVar9 = puVar13[4];
      uVar6 = puVar13[5];
      uVar1 = *(undefined4 *)(puVar13 + 6);
      puVar13 = puVar13 + 7;
      *(long *)(pwVar15 + 4) = lVar4;
      *(undefined8 *)(pwVar15 + 0x10) = uVar9;
      *(undefined8 *)(pwVar15 + 0x14) = uVar6;
      *(undefined4 *)(pwVar15 + 0x18) = uVar1;
      pwVar15 = pwVar15 + 0x1c;
    } while (puVar2 != puVar13);
    pwVar16 = pwVar16 + ((((ulong)((long)puVar2 + (-0x38 - (long)param_2)) >> 3) * 0xdb6db6db6db6db7
                         & 0x1fffffffffffffff) + 1) * 0x1c;
  }
  if (puVar3 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar3,param_1[2] - (long)puVar3);
  }
  param_1[1] = (long)pwVar16;
  *param_1 = (long)local_60;
  param_1[2] = local_48;
  return;
}


