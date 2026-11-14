// ===== FUNC 1f780 size=915

void FUN_0001f780(long *param_1,undefined8 *param_2,undefined8 *param_3)

{
  undefined4 uVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  undefined *__src;
  undefined8 uVar4;
  ulong uVar5;
  ulong uVar6;
  undefined8 uVar7;
  long *__dest;
  ulong uVar8;
  size_t __n;
  long lVar9;
  undefined8 *puVar10;
  long *plVar11;
  undefined8 *puVar12;
  undefined8 *puVar13;
  undefined8 *puVar14;
  long in_FS_OFFSET;
  undefined8 *local_68;
  ulong local_58;
  ulong local_48;
  long local_40;
  
  puVar2 = (undefined8 *)param_1[1];
  puVar3 = (undefined8 *)*param_1;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  uVar5 = ((long)puVar2 - (long)puVar3 >> 3) * 0x6db6db6db6db6db7;
  if (uVar5 == 0x249249249249249) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar8 = 1;
  if (puVar3 != puVar2) {
    uVar8 = uVar5;
  }
  uVar6 = uVar5 + uVar8;
  if (CARRY8(uVar5,uVar8) == false) {
    if (uVar6 != 0) {
      local_58 = 0x249249249249249;
      if (uVar6 < 0x24924924924924a) {
        local_58 = uVar6;
      }
      lVar9 = local_58 * 0x38;
      goto LAB_0001fa8f;
    }
    local_68 = (undefined8 *)0x0;
    local_58 = uVar6;
  }
  else {
    lVar9 = 0x7ffffffffffffff8;
    local_58 = 0x249249249249249;
LAB_0001fa8f:
    local_68 = (undefined8 *)FUN_00041fe0(lVar9);
  }
  plVar11 = (long *)(((long)param_2 - (long)puVar3) + (long)local_68);
  __src = (undefined *)*param_3;
  __dest = plVar11 + 2;
  uVar5 = param_3[1];
  *plVar11 = (long)__dest;
  local_48 = uVar5;
  if (uVar5 < 0x10) {
    if (uVar5 == 1) {
      *(undefined *)(plVar11 + 2) = *__src;
      goto LAB_0001f85b;
    }
    if (uVar5 == 0) goto LAB_0001f85b;
  }
  else {
                    /* try { // try from 0001faaa to 0001faae has its CatchHandler @ 0001fb31 */
    __dest = (long *)FUN_000b0760(plVar11,&local_48,0);
    *plVar11 = (long)__dest;
    plVar11[2] = local_48;
  }
  memcpy(__dest,__src,uVar5);
  __dest = (long *)*plVar11;
LAB_0001f85b:
  plVar11[1] = local_48;
  *(undefined *)((long)__dest + local_48) = 0;
  lVar9 = param_3[5];
  uVar1 = *(undefined4 *)(param_3 + 6);
  plVar11[4] = param_3[4];
  plVar11[5] = lVar9;
  *(undefined4 *)(plVar11 + 6) = uVar1;
  puVar10 = local_68;
  puVar13 = puVar3;
  if (param_2 != puVar3) {
    do {
      *puVar10 = puVar10 + 2;
      puVar14 = (undefined8 *)*puVar13;
      if (puVar14 == puVar13 + 2) {
        uVar7 = 0xffffffffffffffff;
        if (puVar13[1] + 1 != 0) {
          memcpy(puVar10 + 2,puVar14,puVar13[1] + 1);
          uVar7 = puVar13[1];
        }
      }
      else {
        uVar7 = puVar13[2];
        *puVar10 = puVar14;
        puVar10[2] = uVar7;
        uVar7 = puVar13[1];
      }
      puVar10[1] = uVar7;
      uVar7 = puVar13[5];
      puVar14 = puVar13 + 7;
      uVar1 = *(undefined4 *)(puVar13 + 6);
      puVar10[4] = puVar13[4];
      puVar10[5] = uVar7;
      *(undefined4 *)(puVar10 + 6) = uVar1;
      puVar13 = puVar14;
      puVar10 = puVar10 + 7;
    } while (param_2 != puVar14);
    puVar10 = local_68 +
              ((((ulong)((long)param_2 + (-0x38 - (long)puVar3)) >> 3) * 0xdb6db6db6db6db7 &
               0x1fffffffffffffff) + 1) * 7;
  }
  puVar10 = puVar10 + 7;
  puVar13 = param_2;
  puVar14 = puVar10;
  if (param_2 != puVar2) {
    do {
      puVar12 = (undefined8 *)*puVar13;
      lVar9 = puVar13[1];
      *puVar14 = puVar14 + 2;
      if (puVar12 == puVar13 + 2) {
        __n = lVar9 + 1;
        if (__n != 0) {
          memcpy(puVar14 + 2,puVar12,__n);
        }
      }
      else {
        uVar7 = puVar13[2];
        *puVar14 = puVar12;
        puVar14[2] = uVar7;
      }
      uVar7 = puVar13[4];
      uVar4 = puVar13[5];
      puVar12 = puVar13 + 7;
      puVar14[1] = lVar9;
      uVar1 = *(undefined4 *)(puVar13 + 6);
      puVar14[4] = uVar7;
      puVar14[5] = uVar4;
      *(undefined4 *)(puVar14 + 6) = uVar1;
      puVar13 = puVar12;
      puVar14 = puVar14 + 7;
    } while (puVar2 != puVar12);
    puVar10 = puVar10 + ((((ulong)((long)puVar2 + (-0x38 - (long)param_2)) >> 3) * 0xdb6db6db6db6db7
                         & 0x1fffffffffffffff) + 1) * 7;
  }
  if (puVar3 != (undefined8 *)0x0) {
    thunk_FUN_000d36e0(puVar3,param_1[2] - (long)puVar3);
  }
  param_1[1] = (long)puVar10;
  *param_1 = (long)local_68;
  param_1[2] = (long)(local_68 + local_58 * 7);
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


