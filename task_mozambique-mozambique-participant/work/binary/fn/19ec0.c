// ===== FUNC 19ec0 size=741

void FUN_00019ec0(long param_1,long param_2,long param_3,char param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  char cVar3;
  int iVar4;
  uint uVar5;
  long lVar6;
  undefined4 *puVar7;
  int *piVar8;
  int *piVar9;
  undefined8 *puVar10;
  long in_FS_OFFSET;
  byte bVar11;
  undefined8 local_c8;
  long local_c0;
  undefined8 local_a8 [13];
  long local_40;
  
  bVar11 = 0;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if ((*(char *)(param_2 + 0x124) == '\0') || (iVar4 = *(int *)(param_2 + 0x120), 0x9f < iVar4)) {
LAB_00019f00:
    *(undefined *)(param_2 + 0x124) = 0;
  }
  else {
    if (param_4 == '\0') {
LAB_00019f58:
      FUN_00021660(&local_c8,param_1 + 0x14,param_2,param_2 + 0xd8,param_2 + 0x100,iVar4);
      lVar6 = FUN_00019a20(local_c8,local_c0,param_3);
      FUN_0001cf40(&local_c8);
      if (local_c0 == lVar6) goto LAB_00019f00;
    }
    else {
      iVar4 = FUN_000b31e0(param_3,"deliver");
      if (iVar4 != 0) {
        iVar4 = *(int *)(param_2 + 0x120);
        goto LAB_00019f58;
      }
      piVar8 = (int *)(*(long *)(param_2 + 0x10) + (long)*(int *)(param_3 + 0x20) * 0x18);
      if ((((piVar8[2] != 0) ||
           (lVar6 = param_1 + (long)*(int *)(param_3 + 0x30) * 0x14,
           *piVar8 != *(int *)(lVar6 + 0x500))) ||
          (piVar8[(long)*(int *)(lVar6 + 0x4f8) + 3] < *(int *)(lVar6 + 0x4fc))) ||
         (*(int *)(param_2 + 0x100 + (long)*(int *)(param_3 + 0x30) * 4) != -1)) goto LAB_00019f00;
    }
    puVar10 = local_a8;
    for (lVar6 = 0xc; lVar6 != 0; lVar6 = lVar6 + -1) {
      *puVar10 = 0;
      puVar10 = puVar10 + (ulong)bVar11 * -2 + 1;
    }
    *(undefined4 *)puVar10 = 0;
    cVar3 = FUN_00022090(param_1 + 0x14,param_2,param_2 + 0xd8,param_2 + 0x100,
                         *(undefined4 *)(param_1 + 0x6d8),param_3);
    if (cVar3 == '\0') goto LAB_00019f00;
    puVar2 = *(undefined4 **)(param_2 + 0x18);
    for (puVar7 = *(undefined4 **)(param_2 + 0x10); puVar7 != puVar2; puVar7 = puVar7 + 6) {
      if ((puVar7[2] != 0) && (iVar4 = puVar7[2] + -1, puVar7[2] = iVar4, iVar4 == 0)) {
        uVar1 = puVar7[1];
        puVar7[1] = 0xffffffff;
        *puVar7 = uVar1;
      }
    }
    piVar9 = (int *)(param_2 + 0xac);
    piVar8 = (int *)(param_2 + 0x30);
    do {
      if ((*piVar9 != 0) && (iVar4 = *piVar9 + -1, *piVar9 = iVar4, iVar4 == 0)) {
        *piVar8 = *piVar8 + 1;
      }
      piVar8 = piVar8 + 3;
      piVar9 = piVar9 + 1;
    } while (piVar8 != (int *)(param_2 + 0xa8));
    uVar5 = *(int *)(param_2 + 0x120) + 1;
    *(uint *)(param_2 + 0x120) = uVar5;
    if ((uVar5 & 3) == 0) {
      lVar6 = 0;
      do {
        if (*(uint *)(param_1 + 0x18 + lVar6) < 2) {
          piVar8 = (int *)(param_2 + 0xd8 + lVar6);
          *piVar8 = *piVar8 + 1;
          iVar4 = *(int *)(param_2 + 0xd8 + lVar6);
          if (6 < iVar4) {
            iVar4 = 6;
          }
          *(int *)(param_2 + 0xd8 + lVar6) = iVar4;
        }
        lVar6 = lVar6 + 4;
      } while (lVar6 != 0x28);
    }
    lVar6 = *(long *)(param_2 + 0x130);
    if (lVar6 == *(long *)(param_2 + 0x138)) {
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        FUN_0001f780(param_2 + 0x128,lVar6,param_3);
        return;
      }
      goto LAB_0001a1b6;
    }
    FUN_0001c780(lVar6,param_3);
    *(long *)(param_2 + 0x130) = *(long *)(param_2 + 0x130) + 0x38;
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_0001a1b6:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


