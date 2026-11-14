// ===== FUNC 18750 size=901

void FUN_00018750(long *param_1,ulong *param_2,uint param_3,char param_4)

{
  uint uVar1;
  ulong *puVar2;
  int iVar3;
  ulong uVar4;
  ulong uVar5;
  void *__dest;
  ulong uVar6;
  int iVar7;
  ulong uVar8;
  size_t __n;
  ulong *puVar9;
  long lVar10;
  ulong *puVar11;
  uint uVar12;
  uint uVar13;
  long local_58;
  
  uVar5 = (ulong)param_3;
  puVar2 = (ulong *)param_1[2];
  uVar1 = *(uint *)(param_1 + 3);
  uVar8 = (ulong)uVar1;
  if (puVar2 == (ulong *)param_1[4]) {
    uVar8 = uVar8 + ((long)puVar2 - *param_1) * 8;
    if (uVar8 == 0x7fffffffffffffc0) {
                    /* WARNING: Subroutine does not return */
      FUN_00015e26("vector<bool>::_M_insert_aux");
    }
    local_58 = 8;
    if (uVar8 != 0) {
      uVar4 = uVar8 * 2;
      local_58 = 0xffffffffffffff8;
      if (uVar8 <= uVar4) {
        uVar8 = 0x7fffffffffffffc0;
        if (uVar4 < 0x7fffffffffffffc1) {
          uVar8 = uVar4;
        }
        local_58 = (uVar8 + 0x3f >> 6) << 3;
      }
    }
    __dest = (void *)FUN_00041fe0(local_58);
    puVar2 = (ulong *)*param_1;
    __n = 0;
    if (puVar2 != param_2) {
      __n = (long)param_2 - (long)puVar2;
      memmove(__dest,puVar2,__n);
    }
    puVar9 = (ulong *)(__n + (long)__dest);
    if (uVar5 == 0) {
      uVar8 = 1;
      iVar3 = 1;
      puVar11 = puVar9;
    }
    else {
      iVar7 = 0;
      uVar8 = uVar5;
      puVar11 = param_2;
      do {
        while( true ) {
          uVar6 = 1L << ((byte)iVar7 & 0x3f);
          uVar4 = ~uVar6 & *puVar9;
          if ((*puVar11 & uVar6) != 0) {
            uVar4 = uVar6 | *puVar9;
          }
          *puVar9 = uVar4;
          if (iVar7 != 0x3f) break;
          puVar11 = puVar11 + 1;
          puVar9 = puVar9 + 1;
          iVar7 = 0;
          iVar3 = 1;
          uVar8 = uVar8 - 1;
          if (uVar8 == 0) goto LAB_000189b3;
        }
        iVar3 = iVar7 + 2;
        iVar7 = iVar7 + 1;
        uVar8 = uVar8 - 1;
      } while (uVar8 != 0);
LAB_000189b3:
      if (iVar7 == 0x3f) {
        uVar8 = 0x8000000000000000;
        iVar3 = 0;
        puVar11 = puVar9 + 1;
      }
      else {
        uVar8 = 1L << ((byte)iVar7 & 0x3f);
        puVar11 = puVar9;
      }
    }
    uVar4 = ~uVar8 & *puVar9;
    if (param_4 != '\0') {
      uVar4 = uVar8 | *puVar9;
    }
    *puVar9 = uVar4;
    lVar10 = ((ulong)*(uint *)(param_1 + 3) + (param_1[2] - (long)param_2) * 8) - uVar5;
    if (0 < lVar10) {
      do {
        while( true ) {
          uVar4 = 1L << ((byte)iVar3 & 0x3f);
          uVar8 = ~uVar4 & *puVar11;
          if ((*param_2 & 1L << ((byte)uVar5 & 0x3f)) != 0) {
            uVar8 = *puVar11 | uVar4;
          }
          *puVar11 = uVar8;
          if ((int)uVar5 != 0x3f) break;
          param_2 = param_2 + 1;
          uVar5 = 0;
          if (iVar3 != 0x3f) goto LAB_00018a18;
LAB_00018a61:
          puVar11 = puVar11 + 1;
          iVar3 = 0;
          lVar10 = lVar10 + -1;
          if (lVar10 == 0) goto LAB_00018a6d;
        }
        uVar5 = (ulong)((int)uVar5 + 1);
        if (iVar3 == 0x3f) goto LAB_00018a61;
LAB_00018a18:
        iVar3 = iVar3 + 1;
        lVar10 = lVar10 + -1;
      } while (lVar10 != 0);
    }
LAB_00018a6d:
    if (puVar2 != (ulong *)0x0) {
      thunk_FUN_000d36e0(puVar2,param_1[4] - (long)puVar2);
    }
    *param_1 = (long)__dest;
    *(undefined4 *)(param_1 + 1) = 0;
    param_1[2] = (long)puVar11;
    param_1[4] = local_58 + (long)__dest;
    *(int *)(param_1 + 3) = iVar3;
    return;
  }
  uVar12 = (uint)(uVar8 + 1) & 0x3f;
  puVar9 = puVar2 + ((long)(uVar8 + 1) >> 6);
  lVar10 = (uVar8 + ((long)puVar2 - (long)param_2) * 8) - uVar5;
  puVar11 = puVar2;
  uVar13 = uVar1;
  if (0 < lVar10) {
    do {
      if (uVar13 == 0) {
        puVar11 = puVar11 + -1;
        uVar13 = 0x3f;
        uVar8 = 0x8000000000000000;
        uVar5 = 0x8000000000000000;
        if (uVar12 != 0) goto LAB_000187d9;
LAB_0001881c:
        puVar9 = puVar9 + -1;
        uVar12 = 0x3f;
        uVar4 = 0x8000000000000000;
        uVar8 = uVar5;
      }
      else {
        uVar13 = uVar13 - 1;
        uVar8 = 1L << ((byte)uVar13 & 0x3f);
        uVar5 = uVar8;
        if (uVar12 == 0) goto LAB_0001881c;
LAB_000187d9:
        uVar12 = uVar12 - 1;
        uVar4 = 1L << ((byte)uVar12 & 0x3f);
      }
      uVar5 = ~uVar4 & *puVar9;
      if ((uVar8 & *puVar11) != 0) {
        uVar5 = *puVar9 | uVar4;
      }
      *puVar9 = uVar5;
      lVar10 = lVar10 + -1;
    } while (lVar10 != 0);
  }
  uVar5 = 1L << ((byte)param_3 & 0x3f);
  uVar8 = uVar5 | *param_2;
  if (param_4 == '\0') {
    uVar8 = ~uVar5 & *param_2;
  }
  *param_2 = uVar8;
  if (uVar1 == 0x3f) {
    *(undefined4 *)(param_1 + 3) = 0;
    param_1[2] = (long)(puVar2 + 1);
    return;
  }
  *(uint *)(param_1 + 3) = uVar1 + 1;
  return;
}


