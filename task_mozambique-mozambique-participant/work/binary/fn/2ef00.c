// ===== FUNC 2ef00 size=477

void FUN_0002ef00(long *param_1,undefined8 *param_2,long *param_3)

{
  undefined8 *puVar1;
  undefined8 *puVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  ulong uVar5;
  ulong uVar6;
  long *plVar7;
  undefined8 *puVar8;
  undefined8 *puVar9;
  long lVar10;
  undefined8 *puVar11;
  ulong uVar12;
  undefined8 *puVar13;
  undefined *puVar14;
  undefined8 *puVar15;
  long in_FS_OFFSET;
  ulong local_80;
  undefined local_59;
  undefined *local_58;
  long *local_50;
  long local_40;
  
  puVar1 = (undefined8 *)*param_1;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  puVar2 = (undefined8 *)param_1[1];
  uVar5 = (long)puVar2 - (long)puVar1 >> 4;
  if (uVar5 == 0x7ffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar12 = 1;
  if (puVar1 != puVar2) {
    uVar12 = uVar5;
  }
  uVar6 = uVar5 + uVar12;
  if (CARRY8(uVar5,uVar12) == false) {
    if (uVar6 == 0) {
      puVar9 = (undefined8 *)0x0;
      local_80 = uVar6;
      goto LAB_0002ef87;
    }
    local_80 = 0x7ffffffffffffff;
    if (uVar6 < 0x800000000000000) {
      local_80 = uVar6;
    }
    lVar10 = local_80 << 4;
  }
  else {
    lVar10 = 0x7ffffffffffffff0;
    local_80 = 0x7ffffffffffffff;
  }
  puVar9 = (undefined8 *)FUN_00041fe0(lVar10);
LAB_0002ef87:
  puVar14 = (undefined *)(((long)param_2 - (long)puVar1) + (long)puVar9);
  *puVar14 = 0;
  *(undefined8 *)(puVar14 + 8) = 0;
                    /* try { // try from 0002efa5 to 0002efb8 has its CatchHandler @ 0002f0e6 */
  FUN_00024620(puVar14 + 8,0);
  *puVar14 = 3;
  plVar7 = (long *)FUN_00041fe0(0x20);
  local_58 = &local_59;
  *plVar7 = (long)(plVar7 + 2);
  local_50 = plVar7;
                    /* try { // try from 0002efe4 to 0002efe8 has its CatchHandler @ 0002f0e1 */
  FUN_00017e00(plVar7,*param_3,param_3[1] + *param_3);
  *(long **)(puVar14 + 8) = plVar7;
  puVar11 = puVar9;
  if (param_2 != puVar1) {
    puVar11 = (undefined8 *)(((long)param_2 - (long)puVar1) + (long)puVar9);
    puVar15 = puVar9;
    puVar13 = puVar1;
    do {
      uVar3 = *puVar13;
      uVar4 = puVar13[1];
      puVar8 = puVar15 + 2;
      puVar13 = puVar13 + 2;
      *puVar15 = uVar3;
      puVar15[1] = uVar4;
      puVar15 = puVar8;
    } while (puVar11 != puVar8);
  }
  puVar11 = puVar11 + 2;
  puVar15 = puVar11;
  if (param_2 != puVar2) {
    puVar15 = (undefined8 *)((long)puVar11 + ((long)puVar2 - (long)param_2));
    memcpy(puVar11,param_2,(long)puVar2 - (long)param_2);
  }
  if (puVar1 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar1,param_1[2] - (long)puVar1);
  }
  *param_1 = (long)puVar9;
  param_1[1] = (long)puVar15;
  param_1[2] = (long)(puVar9 + local_80 * 2);
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


