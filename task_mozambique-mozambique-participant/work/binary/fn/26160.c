// ===== FUNC 26160 size=444

undefined  [16] FUN_00026160(long param_1,ulong param_2,undefined8 *param_3)

{
  ulong uVar1;
  void *__s1;
  void *__s2;
  int iVar2;
  uint uVar3;
  long lVar4;
  ulong uVar5;
  ulong uVar6;
  ulong uVar7;
  undefined auVar8 [16];
  undefined auVar9 [16];
  
  if (param_2 == param_1 + 8U) {
    if (*(long *)(param_1 + 0x28) != 0) {
      param_2 = *(ulong *)(param_1 + 0x20);
      iVar2 = FUN_00017b10(*(undefined8 *)(param_2 + 0x20),*(undefined8 *)(param_2 + 0x28),*param_3,
                           param_3[1]);
      if (-1 < iVar2) goto LAB_0002627c;
      goto LAB_000262bb;
    }
    goto LAB_0002627c;
  }
  uVar1 = param_3[1];
  uVar7 = *(ulong *)(param_2 + 0x28);
  __s1 = (void *)*param_3;
  __s2 = *(void **)(param_2 + 0x20);
  uVar5 = uVar7;
  if (uVar1 <= uVar7) {
    uVar5 = uVar1;
  }
  uVar6 = param_2;
  if (uVar5 == 0) {
    lVar4 = uVar1 - uVar7;
    if ((lVar4 < 0x80000000) && ((lVar4 < -0x80000000 || ((int)lVar4 < 0)))) {
LAB_0002624a:
      if (*(ulong *)(param_1 + 0x18) != param_2) {
        uVar7 = FUN_00049d30(param_2);
        iVar2 = FUN_00017b10(*(undefined8 *)(uVar7 + 0x20),*(undefined8 *)(uVar7 + 0x28),__s1,uVar1)
        ;
        if (iVar2 < 0) {
          if (*(long *)(uVar7 + 0x18) == 0) {
            uVar6 = 0;
            param_2 = uVar7;
          }
          goto LAB_00026217;
        }
        goto LAB_0002627c;
      }
      goto LAB_00026217;
    }
LAB_000261f0:
    uVar5 = uVar7 - uVar1;
    if ((long)uVar5 < 0x80000000) {
      if (-0x80000001 < (long)uVar5) goto LAB_0002620a;
      goto LAB_000262d0;
    }
  }
  else {
    iVar2 = memcmp(__s1,__s2,uVar5);
    if (iVar2 == 0) {
      lVar4 = uVar1 - uVar7;
      if (lVar4 < 0x80000000) {
        if (lVar4 < -0x80000000) goto LAB_0002624a;
        iVar2 = (int)lVar4;
        goto LAB_000261df;
      }
    }
    else {
LAB_000261df:
      if (iVar2 < 0) goto LAB_0002624a;
    }
    uVar3 = memcmp(__s2,__s1,uVar5);
    uVar5 = (ulong)uVar3;
    if (uVar3 == 0) goto LAB_000261f0;
LAB_0002620a:
    if ((int)uVar5 < 0) {
LAB_000262d0:
      if (*(ulong *)(param_1 + 0x20) == param_2) {
LAB_000262bb:
        auVar9._8_8_ = 0;
        auVar9._0_8_ = param_2;
        return auVar9 << 0x40;
      }
      uVar7 = FUN_00049c90(param_2);
      iVar2 = FUN_00017b10(__s1,uVar1,*(undefined8 *)(uVar7 + 0x20),*(undefined8 *)(uVar7 + 0x28));
      if (-1 < iVar2) {
LAB_0002627c:
        auVar9 = FUN_00024ec0(param_1,param_3);
        return auVar9;
      }
      uVar6 = 0;
      if (*(long *)(param_2 + 0x18) != 0) {
        uVar6 = uVar7;
        param_2 = uVar7;
      }
      goto LAB_00026217;
    }
  }
  param_2 = 0;
LAB_00026217:
  auVar8._8_8_ = param_2;
  auVar8._0_8_ = uVar6;
  return auVar8;
}


