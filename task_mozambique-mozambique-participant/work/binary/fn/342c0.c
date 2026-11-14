// ===== FUNC 342c0 size=575

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_000342c0(undefined8 *param_1,int *param_2,long param_3)

{
  int *piVar1;
  undefined4 uVar2;
  long lVar3;
  byte *pbVar4;
  int iVar5;
  uint uVar6;
  undefined8 *puVar7;
  undefined8 uVar8;
  ulong uVar9;
  undefined *puVar10;
  long in_FS_OFFSET;
  long lVar11;
  long lVar12;
  byte local_41;
  long local_40;
  
  lVar3 = param_1[0xb];
  uVar2 = *(undefined4 *)((long)param_1 + 0x14);
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  puVar7 = (undefined8 *)param_1[10];
  if (puVar7 == param_1 + 0xc) {
    uVar9 = 0xf;
  }
  else {
    uVar9 = param_1[0xc];
  }
  if (uVar9 < lVar3 + 1U) {
    FUN_000b0b90(param_1 + 10,lVar3,0,0,1);
    puVar7 = (undefined8 *)param_1[10];
  }
  *(char *)((long)puVar7 + lVar3) = (char)uVar2;
  piVar1 = param_2 + param_3;
  param_1[0xb] = lVar3 + 1U;
  lVar12 = _UNK_000e2ec8;
  lVar11 = _DAT_000e2ec0;
  *(undefined *)(param_1[10] + 1 + lVar3) = 0;
  if (param_2 != piVar1) {
    do {
      param_1[4] = param_1[4] + lVar11;
      param_1[5] = param_1[5] + lVar12;
      if (*(char *)(param_1 + 3) == '\0') {
        pbVar4 = (byte *)*param_1;
        if (pbVar4 == (byte *)param_1[1]) {
          *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
          goto LAB_000344cf;
        }
        local_41 = *pbVar4;
        uVar6 = (uint)local_41;
        puVar10 = (undefined *)param_1[8];
        *param_1 = pbVar4 + 1;
        *(uint *)((long)param_1 + 0x14) = uVar6;
        if (puVar10 == (undefined *)param_1[9]) goto LAB_0003442c;
LAB_0003437e:
        *puVar10 = (char)uVar6;
        param_1[8] = param_1[8] + 1;
LAB_00034385:
        iVar5 = *(int *)((long)param_1 + 0x14);
        if (iVar5 == 10) {
          param_1[6] = param_1[6] + 1;
          param_1[5] = 0;
        }
      }
      else {
        uVar6 = *(uint *)((long)param_1 + 0x14);
        *(undefined *)(param_1 + 3) = 0;
        if (uVar6 != 0xffffffff) {
          local_41 = (byte)uVar6;
          puVar10 = (undefined *)param_1[8];
          if (puVar10 != (undefined *)param_1[9]) goto LAB_0003437e;
LAB_0003442c:
          FUN_00033ab0(param_1 + 7,puVar10,&local_41);
          lVar11 = _DAT_000e2ec0;
          lVar12 = _UNK_000e2ec8;
          goto LAB_00034385;
        }
LAB_000344cf:
        iVar5 = -1;
      }
      if ((iVar5 < *param_2) || (param_2[1] < iVar5)) {
        param_1[0xe] = "invalid string: ill-formed UTF-8 byte";
        uVar8 = 0;
        goto LAB_00034495;
      }
      lVar3 = param_1[0xb];
      puVar7 = (undefined8 *)param_1[10];
      if (param_1 + 0xc == puVar7) {
        uVar9 = 0xf;
      }
      else {
        uVar9 = param_1[0xc];
      }
      if (uVar9 < lVar3 + 1U) {
        FUN_000b0b90(param_1 + 10,lVar3,0,0,1);
        puVar7 = (undefined8 *)param_1[10];
        lVar11 = _DAT_000e2ec0;
        lVar12 = _UNK_000e2ec8;
      }
      *(char *)((long)puVar7 + lVar3) = (char)iVar5;
      param_2 = param_2 + 2;
      param_1[0xb] = lVar3 + 1U;
      *(undefined *)(param_1[10] + 1 + lVar3) = 0;
    } while (param_2 != piVar1);
  }
  uVar8 = 1;
LAB_00034495:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar8;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


