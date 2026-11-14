// ===== FUNC 17ca0 size=333

void FUN_00017ca0(long *param_1,long *param_2)

{
  undefined8 uVar1;
  long lVar2;
  undefined8 *puVar3;
  undefined *__dest;
  size_t __n;
  undefined8 *puVar4;
  long extraout_RDX;
  undefined8 *puVar5;
  undefined8 *puVar6;
  ulong uVar7;
  long in_FS_OFFSET;
  
  if (param_2 == param_1) {
    return;
  }
  puVar6 = (undefined8 *)param_2[1];
  puVar4 = (undefined8 *)*param_2;
  puVar5 = (undefined8 *)*param_1;
  uVar7 = (long)puVar6 - (long)puVar4;
  if (uVar7 <= (ulong)(param_1[2] - (long)puVar5)) {
    puVar3 = (undefined8 *)param_1[1];
    __n = (long)puVar3 - (long)puVar5;
    if (__n < uVar7) {
      if (__n != 0) {
        memmove(puVar5,puVar4,__n);
        puVar3 = (undefined8 *)param_1[1];
        puVar5 = (undefined8 *)*param_1;
        puVar6 = (undefined8 *)param_2[1];
        puVar4 = (undefined8 *)*param_2;
        __n = (long)puVar3 - (long)puVar5;
      }
      puVar4 = (undefined8 *)(__n + (long)puVar4);
      lVar2 = (long)puVar5 + uVar7;
      if (puVar4 != puVar6) {
        do {
          uVar1 = puVar4[1];
          puVar5 = puVar4 + 3;
          *puVar3 = *puVar4;
          puVar3[1] = uVar1;
          puVar3[2] = puVar4[2];
          puVar3 = puVar3 + 3;
          puVar4 = puVar5;
        } while (puVar5 != puVar6);
        param_1[1] = lVar2;
        return;
      }
    }
    else {
      lVar2 = (long)puVar5 + uVar7;
      if (puVar6 != puVar4) {
        memmove(puVar5,puVar4,uVar7);
        lVar2 = *param_1 + uVar7;
      }
    }
    param_1[1] = lVar2;
    return;
  }
  if (uVar7 < 0x7ffffffffffffff9) {
    puVar3 = (undefined8 *)FUN_00041fe0(uVar7);
    puVar5 = puVar3;
    for (; puVar6 != puVar4; puVar4 = puVar4 + 3) {
      uVar1 = puVar4[1];
      *puVar5 = *puVar4;
      puVar5[1] = uVar1;
      puVar5[2] = puVar4[2];
      puVar5 = puVar5 + 3;
    }
    lVar2 = *param_1;
    if (lVar2 != 0) {
      thunk_FUN_000d36e0(lVar2,param_1[2] - lVar2);
    }
    *param_1 = (long)puVar3;
    param_1[2] = (long)puVar3 + uVar7;
    param_1[1] = (long)puVar3 + uVar7;
    return;
  }
  FUN_00015c88();
  uVar7 = extraout_RDX - (long)param_2;
  lVar2 = *(long *)(in_FS_OFFSET + 0x28);
  if (uVar7 < 0x10) {
    __dest = (undefined *)*puVar5;
    if (uVar7 == 1) {
      *__dest = *(undefined *)param_2;
      __dest = (undefined *)*puVar5;
      goto LAB_00017e44;
    }
    if (uVar7 == 0) goto LAB_00017e44;
  }
  else {
    __dest = (undefined *)FUN_000b0760();
    *puVar5 = __dest;
    puVar5[2] = uVar7;
  }
  memcpy(__dest,param_2,uVar7);
  __dest = (undefined *)*puVar5;
LAB_00017e44:
  puVar5[1] = uVar7;
  __dest[uVar7] = 0;
  if (lVar2 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


