// ===== FUNC 33cd0 size=1065

int FUN_00033cd0(long param_1)

{
  undefined4 uVar1;
  undefined *puVar2;
  long lVar3;
  undefined uVar4;
  int iVar5;
  uint uVar6;
  int *piVar7;
  long lVar8;
  ulonglong uVar9;
  longlong lVar10;
  char *pcVar11;
  ulong uVar12;
  long lVar13;
  long in_FS_OFFSET;
  double dVar14;
  char *local_48;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  *(undefined8 *)(param_1 + 0x58) = 0;
  **(undefined **)(param_1 + 0x50) = 0;
  puVar2 = *(undefined **)(param_1 + 0x38);
  if (puVar2 != *(undefined **)(param_1 + 0x40)) {
    *(undefined **)(param_1 + 0x40) = puVar2;
  }
  *(undefined8 *)(param_1 + 0x98) = 0xffffffffffffffff;
  uVar4 = (undefined)*(undefined4 *)(param_1 + 0x14);
  local_48 = (char *)CONCAT71(local_48._1_7_,uVar4);
  if (puVar2 == *(undefined **)(param_1 + 0x48)) {
    FUN_00033ab0(param_1 + 0x38,puVar2,&local_48);
  }
  else {
    *puVar2 = uVar4;
    *(long *)(param_1 + 0x40) = *(long *)(param_1 + 0x40) + 1;
  }
  iVar5 = *(int *)(param_1 + 0x14);
  if (iVar5 == 0x30) {
    iVar5 = 5;
    FUN_000b1530(param_1 + 0x50,0x30);
LAB_00033ee7:
    uVar6 = FUN_00033c00(param_1);
    if ((uVar6 & 0xffffffdf) != 0x45) {
LAB_00033da2:
      if (uVar6 == 0x2e) {
        FUN_000b1530(param_1 + 0x50,(int)*(char *)(param_1 + 0x90));
        *(long *)(param_1 + 0x98) = *(long *)(param_1 + 0x58) + -1;
        iVar5 = FUN_00033c00(param_1);
        pcVar11 = "invalid number; expected digit after \'.\'";
        if (9 < iVar5 - 0x30U) goto LAB_00033de4;
        do {
          FUN_000b1530(param_1 + 0x50,(int)*(char *)(param_1 + 0x14));
          iVar5 = FUN_00033c00(param_1);
          if (iVar5 == 0x45) goto LAB_00033efd;
          if (0x45 < iVar5) {
            if (iVar5 == 0x65) goto LAB_00033efd;
            break;
          }
        } while (iVar5 - 0x30U < 10);
LAB_00033f50:
        iVar5 = 7;
      }
LAB_00033e53:
      *(long *)(param_1 + 0x20) = *(long *)(param_1 + 0x20) + -1;
      *(undefined *)(param_1 + 0x18) = 1;
      if (*(long *)(param_1 + 0x28) == 0) {
        if (*(long *)(param_1 + 0x30) != 0) {
          *(long *)(param_1 + 0x30) = *(long *)(param_1 + 0x30) + -1;
        }
      }
      else {
        *(long *)(param_1 + 0x28) = *(long *)(param_1 + 0x28) + -1;
      }
      if (*(int *)(param_1 + 0x14) != -1) {
        *(long *)(param_1 + 0x40) = *(long *)(param_1 + 0x40) + -1;
      }
      local_48 = (char *)0x0;
      piVar7 = __errno_location();
      pcVar11 = *(char **)(param_1 + 0x50);
      *piVar7 = 0;
      if (iVar5 == 5) {
        uVar9 = strtoull(pcVar11,&local_48,10);
        if (*piVar7 != 0x22) {
          *(ulonglong *)(param_1 + 0x80) = uVar9;
          goto LAB_00033dee;
        }
LAB_00034113:
        pcVar11 = *(char **)(param_1 + 0x50);
      }
      else if (iVar5 == 6) {
        lVar10 = strtoll(pcVar11,&local_48,10);
        if (*piVar7 != 0x22) {
          *(longlong *)(param_1 + 0x78) = lVar10;
          goto LAB_00033dee;
        }
        goto LAB_00034113;
      }
      iVar5 = 7;
      dVar14 = strtod(pcVar11,&local_48);
      *(double *)(param_1 + 0x88) = dVar14;
      goto LAB_00033dee;
    }
LAB_00033efd:
    lVar13 = param_1 + 0x50;
    FUN_000b1530(lVar13,(int)*(char *)(param_1 + 0x14));
    iVar5 = FUN_00033c00(param_1);
    if (iVar5 == 0x2d) {
LAB_00034030:
      FUN_000b1530(lVar13,(int)*(char *)(param_1 + 0x14));
      iVar5 = FUN_00033c00(param_1);
      pcVar11 = "invalid number; expected digit after exponent sign";
      if (iVar5 - 0x30U < 10) {
LAB_00033f2c:
        FUN_000b1530(lVar13,(int)*(char *)(param_1 + 0x14));
        iVar5 = FUN_00033c00(param_1);
        while (iVar5 - 0x30U < 10) {
          lVar3 = *(long *)(param_1 + 0x58);
          lVar8 = *(long *)(param_1 + 0x50);
          uVar1 = *(undefined4 *)(param_1 + 0x14);
          if (lVar8 == param_1 + 0x60) {
            uVar12 = 0xf;
          }
          else {
            uVar12 = *(ulong *)(param_1 + 0x60);
          }
          if (uVar12 < lVar3 + 1U) {
            FUN_000b0b90(lVar13,lVar3,0,0,1);
            lVar8 = *(long *)(param_1 + 0x50);
          }
          *(char *)(lVar8 + lVar3) = (char)uVar1;
          *(ulong *)(param_1 + 0x58) = lVar3 + 1U;
          *(undefined *)(*(long *)(param_1 + 0x50) + 1 + lVar3) = 0;
          iVar5 = FUN_00033c00(param_1);
        }
        goto LAB_00033f50;
      }
    }
    else {
      if (iVar5 < 0x2e) {
        if (iVar5 == 0x2b) goto LAB_00034030;
      }
      else if (iVar5 - 0x30U < 10) goto LAB_00033f2c;
      pcVar11 = "invalid number; expected \'+\', \'-\', or digit after exponent";
    }
  }
  else {
    if (0x30 < iVar5) {
      if (8 < iVar5 - 0x31U) goto LAB_00033d55;
      iVar5 = 5;
      FUN_000b1530(param_1 + 0x50);
      uVar6 = FUN_00033c00(param_1);
joined_r0x00033e41:
      while ((int)uVar6 < 0x3a) {
        if ((int)uVar6 < 0x30) goto LAB_00033da2;
        FUN_000b1530(param_1 + 0x50,(int)*(char *)(param_1 + 0x14));
        uVar6 = FUN_00033c00(param_1);
      }
      if ((uVar6 & 0xffffffdf) != 0x45) goto LAB_00033e53;
      goto LAB_00033efd;
    }
    if (iVar5 == 0x2d) {
      FUN_000b1530(param_1 + 0x50,0x2d);
    }
LAB_00033d55:
    iVar5 = FUN_00033c00(param_1);
    if (iVar5 == 0x30) {
      iVar5 = 6;
      FUN_000b1530(param_1 + 0x50,(int)*(char *)(param_1 + 0x14));
      goto LAB_00033ee7;
    }
    if (iVar5 - 0x31U < 9) {
      iVar5 = 6;
      FUN_000b1530(param_1 + 0x50,(int)*(char *)(param_1 + 0x14));
      uVar6 = FUN_00033c00(param_1);
      goto joined_r0x00033e41;
    }
    pcVar11 = "invalid number; expected digit after \'-\'";
  }
LAB_00033de4:
  *(char **)(param_1 + 0x70) = pcVar11;
  iVar5 = 0xe;
LAB_00033dee:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return iVar5;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


