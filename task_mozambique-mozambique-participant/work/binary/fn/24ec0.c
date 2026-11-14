// ===== FUNC 24ec0 size=351

undefined  [16] FUN_00024ec0(long param_1,undefined8 *param_2)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  ulong uVar4;
  long lVar5;
  long lVar6;
  size_t __n;
  long lVar7;
  ulong uVar8;
  void *__s2;
  ulong uVar9;
  undefined auVar10 [16];
  void *local_50;
  
  if (*(long *)(param_1 + 0x10) == 0) {
    lVar7 = param_1 + 8;
LAB_00024fd4:
    if (*(long *)(param_1 + 0x18) == lVar7) {
      lVar6 = 0;
      goto LAB_00024f92;
    }
    lVar5 = FUN_00049d30(lVar7);
    uVar8 = *(ulong *)(lVar5 + 0x28);
    __s2 = *(void **)(lVar5 + 0x20);
    uVar9 = param_2[1];
    local_50 = (void *)*param_2;
    __n = uVar8;
    if (uVar9 <= uVar8) {
      __n = uVar9;
    }
  }
  else {
    local_50 = (void *)*param_2;
    uVar9 = param_2[1];
    lVar5 = *(long *)(param_1 + 0x10);
    do {
      lVar7 = lVar5;
      uVar8 = *(ulong *)(lVar7 + 0x28);
      __s2 = *(void **)(lVar7 + 0x20);
      __n = uVar8;
      if (uVar9 <= uVar8) {
        __n = uVar9;
      }
      if (__n == 0) {
LAB_00024f3c:
        uVar4 = uVar9 - uVar8;
        if (0x7fffffff < (long)uVar4) goto LAB_00024f5a;
        if (-0x80000001 < (long)uVar4) goto LAB_00024f56;
LAB_00024f00:
        lVar5 = *(long *)(lVar7 + 0x10);
        bVar1 = true;
      }
      else {
        uVar2 = memcmp(local_50,__s2,__n);
        uVar4 = (ulong)uVar2;
        if (uVar2 == 0) goto LAB_00024f3c;
LAB_00024f56:
        if ((int)uVar4 < 0) goto LAB_00024f00;
LAB_00024f5a:
        lVar5 = *(long *)(lVar7 + 0x18);
        bVar1 = false;
      }
    } while (lVar5 != 0);
    lVar5 = lVar7;
    if (bVar1) goto LAB_00024fd4;
  }
  if ((__n == 0) || (iVar3 = memcmp(__s2,local_50,__n), iVar3 == 0)) {
    lVar6 = uVar8 - uVar9;
    if (0x7fffffff < lVar6) {
      lVar7 = 0;
      lVar6 = lVar5;
      goto LAB_00024f92;
    }
    if (lVar6 < -0x80000000) {
      lVar6 = 0;
      goto LAB_00024f92;
    }
    iVar3 = (int)lVar6;
  }
  lVar6 = 0;
  if (-1 < iVar3) {
    lVar7 = lVar6;
    lVar6 = lVar5;
  }
LAB_00024f92:
  auVar10._8_8_ = lVar7;
  auVar10._0_8_ = lVar6;
  return auVar10;
}


