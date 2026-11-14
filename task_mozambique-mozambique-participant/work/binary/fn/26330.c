// ===== FUNC 26330 size=846

long FUN_00026330(char *param_1,undefined8 *param_2)

{
  undefined8 *__src;
  long lVar1;
  void *pvVar2;
  ulong uVar3;
  ulong uVar4;
  char cVar5;
  int iVar6;
  uint uVar7;
  long lVar8;
  undefined8 uVar9;
  char *__s;
  size_t sVar10;
  long lVar11;
  ulong uVar12;
  long lVar13;
  long lVar14;
  long lVar15;
  long in_FS_OFFSET;
  undefined auVar16 [16];
  undefined *local_68;
  undefined8 local_60;
  undefined local_58 [24];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  cVar5 = *param_1;
  if (cVar5 == '\0') {
    *param_1 = '\x01';
    lVar8 = FUN_00041fe0(0x30);
    *(undefined4 *)(lVar8 + 8) = 0;
    *(undefined8 *)(lVar8 + 0x10) = 0;
    *(long *)(lVar8 + 0x18) = lVar8 + 8;
    *(long *)(lVar8 + 0x20) = lVar8 + 8;
    *(undefined8 *)(lVar8 + 0x28) = 0;
    *(long *)(param_1 + 8) = lVar8;
    cVar5 = *param_1;
  }
  if (cVar5 != '\x01') {
    uVar9 = FUN_00040f40(0x20);
    __s = (char *)FUN_000137b8(*param_1);
    local_58[0] = 0;
    local_68 = local_58;
    local_60 = 0;
    sVar10 = strlen(__s);
                    /* try { // try from 0002664b to 00026669 has its CatchHandler @ 00026698 */
    FUN_000b1110(&local_68,sVar10 + 0x32);
    FUN_00017ba0(&local_68,"cannot use operator[] with a string argument with ");
    FUN_00017ba0(&local_68,__s);
                    /* try { // try from 00026675 to 00026679 has its CatchHandler @ 0002669d */
    FUN_00013ba0(uVar9,0x131,&local_68);
    FUN_000b07c0(&local_68);
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar9,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
  }
  lVar1 = *(long *)(param_1 + 8);
  lVar8 = lVar1 + 8;
  lVar15 = lVar8;
  if (*(long *)(lVar1 + 0x10) != 0) {
    pvVar2 = (void *)*param_2;
    uVar3 = param_2[1];
    lVar11 = *(long *)(lVar1 + 0x10);
    do {
      while( true ) {
        lVar14 = lVar11;
        uVar4 = *(ulong *)(lVar14 + 0x28);
        uVar12 = uVar3;
        if (uVar4 <= uVar3) {
          uVar12 = uVar4;
        }
        if ((uVar12 != 0) && (iVar6 = memcmp(*(void **)(lVar14 + 0x20),pvVar2,uVar12), iVar6 != 0))
        break;
        lVar11 = uVar4 - uVar3;
        if (lVar11 < 0x80000000) {
          if (-0x80000001 < lVar11) {
            iVar6 = (int)lVar11;
            break;
          }
          goto LAB_000263a0;
        }
LAB_000263ec:
        lVar11 = *(long *)(lVar14 + 0x10);
        lVar15 = lVar14;
        if (*(long *)(lVar14 + 0x10) == 0) goto LAB_000263f8;
      }
      if (-1 < iVar6) goto LAB_000263ec;
LAB_000263a0:
      lVar11 = *(long *)(lVar14 + 0x18);
    } while (*(long *)(lVar14 + 0x18) != 0);
LAB_000263f8:
    if (lVar8 != lVar15) {
      uVar4 = *(ulong *)(lVar15 + 0x28);
      uVar12 = uVar3;
      if (uVar4 <= uVar3) {
        uVar12 = uVar4;
      }
      if ((uVar12 == 0) || (iVar6 = memcmp(pvVar2,*(void **)(lVar15 + 0x20),uVar12), iVar6 == 0)) {
        lVar11 = uVar3 - uVar4;
        if (0x7fffffff < lVar11) goto LAB_00026441;
        if (lVar11 < -0x80000000) goto LAB_00026475;
        iVar6 = (int)lVar11;
      }
      if (-1 < iVar6) goto LAB_00026441;
    }
  }
LAB_00026475:
  lVar11 = FUN_00041fe0(0x50);
  pvVar2 = (void *)(lVar11 + 0x30);
  *(void **)(lVar11 + 0x20) = pvVar2;
  __src = param_2 + 2;
  if ((undefined8 *)*param_2 == __src) {
    lVar14 = param_2[1];
    if (lVar14 + 1U != 0) {
      memcpy(pvVar2,__src,lVar14 + 1U);
    }
  }
  else {
    *(void **)(lVar11 + 0x20) = (void *)*param_2;
    lVar14 = param_2[1];
    *(undefined8 *)(lVar11 + 0x30) = param_2[2];
  }
  *(long *)(lVar11 + 0x28) = lVar14;
  *(undefined *)(lVar11 + 0x40) = 0;
  *param_2 = __src;
  param_2[1] = 0;
  *(undefined *)(param_2 + 2) = 0;
  *(undefined8 *)(lVar11 + 0x48) = 0;
  auVar16 = FUN_00026160(lVar1,lVar15,lVar11 + 0x20);
  lVar13 = auVar16._8_8_;
  lVar15 = auVar16._0_8_;
  if (lVar13 == 0) {
    FUN_00024620(lVar11 + 0x48,0);
    if (pvVar2 != *(void **)(lVar11 + 0x20)) {
      thunk_FUN_000d36e0(*(void **)(lVar11 + 0x20),*(long *)(lVar11 + 0x30) + 1);
    }
    thunk_FUN_000d36e0(lVar11,0x50);
  }
  else {
    if ((lVar8 == lVar13) || (lVar15 != 0)) {
      uVar7 = 1;
    }
    else {
      uVar7 = FUN_00017b10(*(undefined8 *)(lVar11 + 0x20),lVar14,*(undefined8 *)(lVar13 + 0x20),
                           *(undefined8 *)(lVar13 + 0x28));
      uVar7 = uVar7 >> 0x1f;
    }
    FUN_00049eb0(uVar7,lVar11,lVar13,lVar8);
    *(long *)(lVar1 + 0x28) = *(long *)(lVar1 + 0x28) + 1;
    lVar15 = lVar11;
  }
LAB_00026441:
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return lVar15 + 0x40;
}


