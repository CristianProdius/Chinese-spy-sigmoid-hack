// ===== FUNC 26770 size=316

long FUN_00026770(long param_1,undefined8 *param_2)

{
  long *plVar1;
  void *__s2;
  ulong uVar2;
  ulong uVar3;
  int iVar4;
  long lVar5;
  long lVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  long in_FS_OFFSET;
  bool bVar10;
  undefined8 *local_48;
  long local_40;
  
  lVar8 = param_1 + 8;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (*(long *)(param_1 + 0x10) != 0) {
    __s2 = (void *)*param_2;
    uVar2 = param_2[1];
    lVar5 = lVar8;
    lVar9 = *(long *)(param_1 + 0x10);
    do {
      while( true ) {
        uVar3 = *(ulong *)(lVar9 + 0x28);
        uVar7 = uVar2;
        if (uVar3 <= uVar2) {
          uVar7 = uVar3;
        }
        if ((uVar7 != 0) && (iVar4 = memcmp(*(void **)(lVar9 + 0x20),__s2,uVar7), iVar4 != 0))
        break;
        lVar6 = uVar3 - uVar2;
        if (lVar6 < 0x80000000) {
          if (-0x80000001 < lVar6) {
            iVar4 = (int)lVar6;
            break;
          }
          goto LAB_000267c0;
        }
LAB_0002680c:
        plVar1 = (long *)(lVar9 + 0x10);
        lVar5 = lVar9;
        lVar9 = *plVar1;
        if (*plVar1 == 0) goto LAB_00026818;
      }
      if (-1 < iVar4) goto LAB_0002680c;
LAB_000267c0:
      lVar9 = *(long *)(lVar9 + 0x18);
    } while (lVar9 != 0);
LAB_00026818:
    bVar10 = lVar8 != lVar5;
    lVar8 = lVar5;
    if (bVar10) {
      uVar3 = *(ulong *)(lVar5 + 0x28);
      uVar7 = uVar2;
      if (uVar3 <= uVar2) {
        uVar7 = uVar3;
      }
      if ((uVar7 == 0) || (iVar4 = memcmp(__s2,*(void **)(lVar5 + 0x20),uVar7), iVar4 == 0)) {
        lVar9 = uVar2 - uVar3;
        if (0x7fffffff < lVar9) goto LAB_00026861;
        if (lVar9 < -0x80000000) goto LAB_0002688d;
        iVar4 = (int)lVar9;
      }
      if (-1 < iVar4) goto LAB_00026861;
    }
  }
LAB_0002688d:
  local_48 = param_2;
  lVar5 = FUN_0001a480(param_1,lVar8,&local_48);
LAB_00026861:
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return lVar5 + 0x40;
}


