// ===== FUNC 20da0 size=575

undefined  [16] FUN_00020da0(long param_1,undefined8 *param_2)

{
  undefined8 *__src;
  bool bVar1;
  uint uVar2;
  int iVar3;
  long lVar4;
  ulong uVar5;
  long lVar6;
  long lVar7;
  void *__s2;
  ulong __n;
  undefined uVar8;
  ulong uVar9;
  ulong uVar10;
  long lVar11;
  undefined auVar12 [16];
  void *local_58;
  
  lVar4 = param_1 + 8;
  if (*(long *)(param_1 + 0x10) == 0) {
    lVar11 = lVar4;
    if (*(long *)(param_1 + 0x18) != lVar4) {
      local_58 = (void *)*param_2;
      uVar9 = param_2[1];
LAB_00020f57:
      lVar6 = FUN_00049d30(lVar11);
      uVar10 = *(ulong *)(lVar6 + 0x28);
      __s2 = *(void **)(lVar6 + 0x20);
      __n = uVar10;
      if (uVar9 <= uVar10) {
        __n = uVar9;
      }
LAB_00020e58:
      if ((__n == 0) || (iVar3 = memcmp(__s2,local_58,__n), iVar3 == 0)) {
        uVar8 = 0;
        lVar7 = uVar10 - uVar9;
        if (0x7fffffff < lVar7) goto LAB_00020e92;
        if (lVar7 < -0x80000000) goto LAB_00020eb0;
        iVar3 = (int)lVar7;
      }
      uVar8 = 0;
      if (-1 < iVar3) goto LAB_00020e92;
      goto LAB_00020eb0;
    }
    uVar2 = 1;
  }
  else {
    local_58 = (void *)*param_2;
    uVar9 = param_2[1];
    lVar6 = *(long *)(param_1 + 0x10);
    do {
      lVar11 = lVar6;
      uVar10 = *(ulong *)(lVar11 + 0x28);
      __s2 = *(void **)(lVar11 + 0x20);
      __n = uVar10;
      if (uVar9 <= uVar10) {
        __n = uVar9;
      }
      if (__n == 0) {
LAB_00020e23:
        uVar5 = uVar9 - uVar10;
        if ((long)uVar5 < 0x80000000) {
          if (-0x80000001 < (long)uVar5) goto LAB_00020e3d;
          goto LAB_00020de8;
        }
LAB_00020e41:
        lVar6 = *(long *)(lVar11 + 0x18);
        bVar1 = false;
      }
      else {
        uVar2 = memcmp(local_58,__s2,__n);
        uVar5 = (ulong)uVar2;
        if (uVar2 == 0) goto LAB_00020e23;
LAB_00020e3d:
        if (-1 < (int)uVar5) goto LAB_00020e41;
LAB_00020de8:
        lVar6 = *(long *)(lVar11 + 0x10);
        bVar1 = true;
      }
    } while (lVar6 != 0);
    lVar6 = lVar11;
    if (!bVar1) goto LAB_00020e58;
    if (*(long *)(param_1 + 0x18) != lVar11) goto LAB_00020f57;
LAB_00020eb0:
    uVar2 = 1;
    if (lVar11 != lVar4) {
      uVar2 = FUN_00017b10(local_58,uVar9,*(undefined8 *)(lVar11 + 0x20),
                           *(undefined8 *)(lVar11 + 0x28));
      uVar2 = uVar2 >> 0x1f;
    }
  }
  lVar6 = FUN_00041fe0(0x40);
  *(void **)(lVar6 + 0x20) = (void *)(lVar6 + 0x30);
  __src = param_2 + 2;
  if ((undefined8 *)*param_2 == __src) {
    lVar7 = param_2[1];
    if (lVar7 + 1U != 0) {
      memcpy((void *)(lVar6 + 0x30),__src,lVar7 + 1U);
    }
  }
  else {
    *(void **)(lVar6 + 0x20) = (void *)*param_2;
    lVar7 = param_2[1];
    *(undefined8 *)(lVar6 + 0x30) = param_2[2];
  }
  *(long *)(lVar6 + 0x28) = lVar7;
  *param_2 = __src;
  param_2[1] = 0;
  *(undefined *)(param_2 + 2) = 0;
  FUN_00049eb0(uVar2,lVar6,lVar11,lVar4);
  uVar8 = 1;
  *(long *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) + 1;
LAB_00020e92:
  auVar12[8] = uVar8;
  auVar12._0_8_ = lVar6;
  auVar12._9_7_ = 0;
  return auVar12;
}


