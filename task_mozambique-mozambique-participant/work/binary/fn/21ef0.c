// ===== FUNC 21ef0 size=396

void FUN_00021ef0(long *param_1,undefined8 *param_2,undefined8 *param_3)

{
  size_t __n;
  undefined8 *puVar1;
  undefined8 *puVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  ulong uVar5;
  ulong uVar6;
  undefined8 *puVar7;
  undefined8 *puVar8;
  undefined8 *puVar9;
  ulong uVar10;
  undefined8 *puVar11;
  qword *__dest;
  qword *pqVar12;
  long local_50;
  
  puVar1 = (undefined8 *)param_1[1];
  puVar2 = (undefined8 *)*param_1;
  uVar5 = ((long)puVar1 - (long)puVar2 >> 3) * -0x5555555555555555;
  if (uVar5 == 0x555555555555555) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar10 = 1;
  if (puVar2 != puVar1) {
    uVar10 = uVar5;
  }
  uVar6 = uVar5 + uVar10;
  if (CARRY8(uVar5,uVar10) == false) {
    if (uVar6 == 0) {
      local_50 = 0;
      __dest = &Elf64_Ehdr_00000000.e_entry;
      puVar9 = (undefined8 *)0x0;
      goto LAB_00021f72;
    }
    if (0x555555555555555 < uVar6) {
      uVar6 = 0x555555555555555;
    }
    local_50 = uVar6 * 0x18;
  }
  else {
    local_50 = 0x7ffffffffffffff8;
  }
  puVar9 = (undefined8 *)FUN_00041fe0(local_50);
  local_50 = (long)puVar9 + local_50;
  __dest = puVar9 + 3;
LAB_00021f72:
  uVar4 = param_3[1];
  uVar3 = param_3[2];
  puVar7 = (undefined8 *)((long)puVar9 + ((long)param_2 - (long)puVar2));
  *puVar7 = *param_3;
  puVar7[1] = uVar4;
  *(undefined8 *)((long)puVar9 + ((long)param_2 - (long)puVar2) + 0x10) = uVar3;
  puVar7 = puVar2;
  puVar11 = puVar9;
  if (param_2 != puVar2) {
    do {
      uVar4 = puVar7[1];
      uVar3 = puVar7[2];
      puVar8 = puVar7 + 3;
      *puVar11 = *puVar7;
      puVar11[1] = uVar4;
      puVar11[2] = uVar3;
      puVar7 = puVar8;
      puVar11 = puVar11 + 3;
    } while (puVar8 != param_2);
    __dest = (qword *)((long)puVar9 +
                      ((long)param_2 + (-0x18 - (long)puVar2) & 0xfffffffffffffff8U) + 0x30);
  }
  pqVar12 = __dest;
  if (param_2 != puVar1) {
    __n = ((long)puVar1 + (-0x18 - (long)param_2) & 0xfffffffffffffff8U) + 0x18;
    pqVar12 = (qword *)((long)__dest + __n);
    memcpy(__dest,param_2,__n);
  }
  if (puVar2 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar2,param_1[2] - (long)puVar2);
  }
  *param_1 = (long)puVar9;
  param_1[1] = (long)pqVar12;
  param_1[2] = local_50;
  return;
}


