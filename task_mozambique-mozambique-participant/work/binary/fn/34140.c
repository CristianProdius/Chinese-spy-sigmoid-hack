// ===== FUNC 34140 size=353

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_00034140(undefined8 *param_1)

{
  undefined4 uVar1;
  byte *pbVar2;
  uint uVar3;
  byte bVar4;
  undefined8 *puVar5;
  int iVar6;
  undefined *puVar7;
  int iVar8;
  long in_FS_OFFSET;
  long lVar9;
  long lVar10;
  byte local_49;
  undefined8 local_48;
  undefined8 uStack_40;
  undefined8 local_38;
  long local_30;
  
  iVar8 = 0;
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  puVar5 = &local_48;
  local_48 = _DAT_000e2ed0;
  uStack_40 = _UNK_000e2ed8;
  lVar9 = _DAT_000e2ec0;
  lVar10 = _UNK_000e2ec8;
  do {
    uVar1 = *(undefined4 *)puVar5;
    param_1[4] = param_1[4] + lVar9;
    param_1[5] = param_1[5] + lVar10;
    bVar4 = (byte)uVar1;
    if (*(char *)(param_1 + 3) != '\0') {
      uVar3 = *(uint *)((long)param_1 + 0x14);
      *(undefined *)(param_1 + 3) = 0;
      if (uVar3 != 0xffffffff) {
        local_49 = (byte)uVar3;
        puVar7 = (undefined *)param_1[8];
        if (puVar7 != (undefined *)param_1[9]) goto LAB_000341b7;
LAB_00034248:
        FUN_00033ab0(param_1 + 7,puVar7,&local_49);
        lVar9 = _DAT_000e2ec0;
        lVar10 = _UNK_000e2ec8;
LAB_000341be:
        iVar6 = *(int *)((long)param_1 + 0x14);
        if (iVar6 != 10) {
          if (iVar6 - 0x30U < 10) {
            iVar8 = iVar8 + (iVar6 - 0x30U << (bVar4 & 0x1f));
          }
          else {
            if (5 < iVar6 - 0x41U) goto LAB_00034294;
            iVar8 = iVar8 + (iVar6 + -0x37 << (bVar4 & 0x1f));
          }
          goto LAB_000341d9;
        }
        param_1[6] = param_1[6] + 1;
        param_1[5] = 0;
      }
LAB_00034215:
      iVar8 = -1;
      break;
    }
    pbVar2 = (byte *)*param_1;
    if (pbVar2 != (byte *)param_1[1]) {
      local_49 = *pbVar2;
      uVar3 = (uint)local_49;
      puVar7 = (undefined *)param_1[8];
      *param_1 = pbVar2 + 1;
      *(uint *)((long)param_1 + 0x14) = uVar3;
      if (puVar7 == (undefined *)param_1[9]) goto LAB_00034248;
LAB_000341b7:
      *puVar7 = (char)uVar3;
      param_1[8] = param_1[8] + 1;
      goto LAB_000341be;
    }
    *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
    iVar6 = -1;
LAB_00034294:
    if (5 < iVar6 - 0x61U) goto LAB_00034215;
    iVar8 = iVar8 + (iVar6 + -0x57 << (bVar4 & 0x1f));
LAB_000341d9:
    puVar5 = (undefined8 *)((long)puVar5 + 4);
  } while (&local_38 != puVar5);
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return iVar8;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


