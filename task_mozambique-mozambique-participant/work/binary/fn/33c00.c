// ===== FUNC 33c00 size=198

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_00033c00(undefined8 *param_1)

{
  byte *pbVar1;
  int iVar2;
  uint uVar3;
  undefined *puVar4;
  long in_FS_OFFSET;
  long lVar5;
  byte local_11;
  long local_10;
  
  lVar5 = param_1[5] + _UNK_000e2ec8;
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  param_1[4] = param_1[4] + _DAT_000e2ec0;
  param_1[5] = lVar5;
  if (*(char *)(param_1 + 3) == '\0') {
    pbVar1 = (byte *)*param_1;
    if (pbVar1 == (byte *)param_1[1]) {
      *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
      goto LAB_00033cbf;
    }
    local_11 = *pbVar1;
    uVar3 = (uint)local_11;
    puVar4 = (undefined *)param_1[8];
    *param_1 = pbVar1 + 1;
    *(uint *)((long)param_1 + 0x14) = uVar3;
    if (puVar4 == (undefined *)param_1[9]) goto LAB_00033ca4;
LAB_00033c4d:
    *puVar4 = (char)uVar3;
    param_1[8] = param_1[8] + 1;
  }
  else {
    uVar3 = *(uint *)((long)param_1 + 0x14);
    *(undefined *)(param_1 + 3) = 0;
    if (uVar3 == 0xffffffff) {
LAB_00033cbf:
      iVar2 = -1;
      goto LAB_00033c69;
    }
    local_11 = (byte)uVar3;
    puVar4 = (undefined *)param_1[8];
    if (puVar4 != (undefined *)param_1[9]) goto LAB_00033c4d;
LAB_00033ca4:
    FUN_00033ab0(param_1 + 7,puVar4,&local_11);
  }
  iVar2 = *(int *)((long)param_1 + 0x14);
  if (iVar2 == 10) {
    param_1[6] = param_1[6] + 1;
    param_1[5] = 0;
  }
LAB_00033c69:
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return iVar2;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


