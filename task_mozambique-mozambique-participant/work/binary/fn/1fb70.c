// ===== FUNC 1fb70 size=446

void FUN_0001fb70(long *param_1,ulong param_2)

{
  ulong uVar1;
  undefined8 *puVar2;
  void *__src;
  long lVar3;
  void *__dest;
  undefined8 *puVar4;
  undefined8 *puVar5;
  ulong uVar6;
  ulong uVar7;
  long lVar8;
  undefined8 *puVar9;
  long lVar10;
  
  if (param_2 == 0) {
    return;
  }
  puVar2 = (undefined8 *)param_1[1];
  lVar8 = *param_1;
  uVar7 = (long)puVar2 - lVar8 >> 3;
  if (param_2 <= (ulong)(param_1[2] - (long)puVar2 >> 3)) {
    *(undefined4 *)puVar2 = 0;
    puVar4 = puVar2 + 1;
    *(undefined *)((long)puVar2 + 4) = 0;
    puVar9 = puVar4;
    if (param_2 - 1 != 0) {
      puVar9 = puVar4 + (param_2 - 1);
      do {
        puVar5 = puVar4 + 1;
        *puVar4 = *puVar2;
        puVar4 = puVar5;
      } while (puVar9 != puVar5);
    }
    param_1[1] = (long)puVar9;
    return;
  }
  if (0xfffffffffffffff - uVar7 < param_2) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_default_append");
  }
  uVar1 = param_2 + uVar7;
  if (uVar7 < param_2) {
    uVar7 = 0xfffffffffffffff;
    if (uVar1 < 0x1000000000000000) {
      uVar7 = uVar1;
    }
    lVar10 = uVar7 << 3;
  }
  else {
    lVar10 = 0x7ffffffffffffff8;
    uVar6 = uVar7 * 2;
    if (uVar7 <= uVar6) {
      if (0xfffffffffffffff < uVar6) {
        uVar6 = 0xfffffffffffffff;
      }
      lVar10 = uVar6 * 8;
    }
  }
  __dest = (void *)FUN_00041fe0(lVar10);
  __src = (void *)*param_1;
  lVar3 = param_1[1];
  puVar2 = (undefined8 *)((long)__dest + ((long)puVar2 - lVar8));
  *(undefined4 *)puVar2 = 0;
  *(undefined *)((long)puVar2 + 4) = 0;
  if (param_2 - 1 != 0) {
    puVar4 = puVar2 + 1;
    do {
      puVar9 = puVar4 + 1;
      *puVar4 = *puVar2;
      puVar4 = puVar9;
    } while (puVar2 + 1 + (param_2 - 1) != puVar9);
  }
  if (lVar3 - (long)__src < 1) {
    if (__src == (void *)0x0) goto LAB_0001fc4a;
    lVar8 = param_1[2] - (long)__src;
  }
  else {
    memmove(__dest,__src,lVar3 - (long)__src);
    lVar8 = param_1[2] - (long)__src;
  }
  thunk_FUN_000d36e0(__src,lVar8);
LAB_0001fc4a:
  *param_1 = (long)__dest;
  param_1[1] = (long)((long)__dest + uVar1 * 8);
  param_1[2] = lVar10 + (long)__dest;
  return;
}


