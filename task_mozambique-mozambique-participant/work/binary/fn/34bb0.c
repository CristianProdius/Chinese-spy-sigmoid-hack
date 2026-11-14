// ===== FUNC 34bb0 size=1714

/* WARNING: Type propagation algorithm not settling */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00034bb0(undefined8 *param_1)

{
  undefined8 *puVar1;
  byte *pbVar2;
  byte bVar3;
  char cVar4;
  int iVar5;
  uint uVar6;
  long lVar7;
  char *pcVar8;
  undefined8 uVar9;
  char cVar10;
  long lVar11;
  undefined4 *puVar12;
  undefined *puVar13;
  long in_FS_OFFSET;
  byte local_36;
  undefined local_35 [4];
  undefined local_31;
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  lVar7 = param_1[4];
  if (lVar7 == 0) {
    iVar5 = FUN_00033c00();
    if (iVar5 != 0xef) {
      *(undefined *)(param_1 + 3) = 1;
      lVar7 = param_1[4] + -1;
      param_1[4] = lVar7;
      if (param_1[5] == 0) {
        lVar11 = 0;
        if (param_1[6] != 0) {
          param_1[6] = param_1[6] + -1;
        }
      }
      else {
        lVar11 = param_1[5] + -1;
        param_1[5] = lVar11;
      }
      if (*(int *)((long)param_1 + 0x14) != -1) {
        param_1[8] = param_1[8] + -1;
      }
      cVar4 = '\x01';
      goto LAB_00034c3a;
    }
    iVar5 = FUN_00033c00(param_1);
    if ((iVar5 == 0xbb) && (iVar5 = FUN_00033c00(param_1), iVar5 == 0xbf)) {
      lVar7 = param_1[4];
      goto LAB_00034c32;
    }
    pcVar8 = "invalid BOM; must be 0xEF 0xBB 0xBF if given";
LAB_00034ecf:
    param_1[0xe] = pcVar8;
    uVar9 = 0xe;
    goto LAB_00034ed8;
  }
LAB_00034c32:
  lVar11 = param_1[5];
  cVar4 = *(char *)(param_1 + 3);
LAB_00034c3a:
LAB_00034c67:
  param_1[4] = lVar7 + 1;
  param_1[5] = lVar11 + 1;
  if (cVar4 != '\0') {
    uVar6 = *(uint *)((long)param_1 + 0x14);
    *(undefined *)(param_1 + 3) = 0;
    if (uVar6 == 0xffffffff) goto LAB_00034cee;
    local_36 = (byte)uVar6;
    puVar13 = (undefined *)param_1[8];
    if (puVar13 == (undefined *)param_1[9]) goto LAB_00034cd4;
LAB_00034c97:
    *puVar13 = (char)uVar6;
    param_1[8] = param_1[8] + 1;
LAB_00034c9e:
    uVar6 = *(uint *)((long)param_1 + 0x14);
    if (uVar6 == 10) {
      param_1[6] = param_1[6] + 1;
      lVar11 = 0;
    }
    else {
      if (((uVar6 & 0xfffffffb) != 9) && (uVar6 != 0x20)) goto LAB_00034cee;
      lVar11 = param_1[5];
    }
    lVar7 = param_1[4];
    cVar4 = *(char *)(param_1 + 3);
    goto LAB_00034c67;
  }
  pbVar2 = (byte *)*param_1;
  if (pbVar2 != (byte *)param_1[1]) {
    local_36 = *pbVar2;
    uVar6 = (uint)local_36;
    puVar13 = (undefined *)param_1[8];
    *param_1 = pbVar2 + 1;
    *(uint *)((long)param_1 + 0x14) = (uint)local_36;
    if (puVar13 != (undefined *)param_1[9]) goto LAB_00034c97;
LAB_00034cd4:
    FUN_00033ab0(param_1 + 7,puVar13,&local_36);
    goto LAB_00034c9e;
  }
  *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
  uVar6 = 0xffffffff;
LAB_00034cee:
  cVar4 = *(char *)(param_1 + 2);
  bVar3 = local_36;
  cVar10 = cVar4;
  while ((cVar10 != '\0' && (local_36 = (byte)uVar6, uVar6 == 0x2f))) {
    lVar7 = param_1[5] + _UNK_000e2ec8;
    param_1[4] = param_1[4] + _DAT_000e2ec0;
    param_1[5] = lVar7;
    if (*(char *)(param_1 + 3) == '\0') {
      pbVar2 = (byte *)*param_1;
      if (pbVar2 != (byte *)param_1[1]) {
        local_36 = *pbVar2;
        *param_1 = pbVar2 + 1;
        *(uint *)((long)param_1 + 0x14) = (uint)local_36;
        goto LAB_00034d2a;
      }
      *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
      local_36 = bVar3;
LAB_00034ffd:
      pcVar8 = "invalid comment; expecting \'/\' or \'*\' after \'/\'";
      goto LAB_00034ecf;
    }
    *(undefined *)(param_1 + 3) = 0;
LAB_00034d2a:
    pbVar2 = (byte *)param_1[8];
    puVar1 = param_1 + 7;
    if (pbVar2 == (byte *)param_1[9]) {
      FUN_00033ab0(puVar1,pbVar2,&local_36);
    }
    else {
      *pbVar2 = local_36;
      param_1[8] = param_1[8] + 1;
    }
    uVar6 = *(uint *)((long)param_1 + 0x14);
    if (uVar6 == 10) {
      param_1[6] = param_1[6] + 1;
      param_1[5] = 0;
      goto LAB_00034ffd;
    }
    if (uVar6 == 0x2a) {
LAB_00034d5c:
      do {
        lVar7 = param_1[4];
        lVar11 = param_1[5];
        cVar10 = *(char *)(param_1 + 3);
LAB_00034d68:
        param_1[4] = lVar7 + 1;
        param_1[5] = lVar11 + 1;
        if (cVar10 != '\0') {
          uVar6 = *(uint *)((long)param_1 + 0x14);
          *(undefined *)(param_1 + 3) = 0;
          if (uVar6 != 0xffffffff) {
            local_36 = (byte)uVar6;
            puVar13 = (undefined *)param_1[8];
            if (puVar13 == (undefined *)param_1[9]) goto LAB_0003506d;
LAB_00034da2:
            *puVar13 = (char)uVar6;
            param_1[8] = param_1[8] + 1;
            goto LAB_00034da9;
          }
LAB_00034fe0:
          pcVar8 = "invalid comment; missing closing \'*/\'";
          goto LAB_00034ecf;
        }
        pbVar2 = (byte *)*param_1;
        if (pbVar2 == (byte *)param_1[1]) {
          *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
          pcVar8 = "invalid comment; missing closing \'*/\'";
          goto LAB_00034ecf;
        }
        local_36 = *pbVar2;
        uVar6 = (uint)local_36;
        puVar13 = (undefined *)param_1[8];
        *param_1 = pbVar2 + 1;
        *(uint *)((long)param_1 + 0x14) = uVar6;
        if (puVar13 != (undefined *)param_1[9]) goto LAB_00034da2;
LAB_0003506d:
        FUN_00033ab0(puVar1,puVar13,&local_36);
LAB_00034da9:
        iVar5 = *(int *)((long)param_1 + 0x14);
        if (iVar5 != 10) {
          if (iVar5 < 1) {
            if (-2 < iVar5) goto LAB_00034fe0;
            goto LAB_00034d5c;
          }
          if (iVar5 != 0x2a) goto LAB_00034d5c;
          iVar5 = FUN_00033c00(param_1);
          if (iVar5 == 0x2f) goto LAB_00034dd3;
          *(undefined *)(param_1 + 3) = 1;
          lVar7 = param_1[4] + -1;
          param_1[4] = lVar7;
          if (param_1[5] == 0) {
            lVar11 = 0;
            if (param_1[6] != 0) {
              param_1[6] = param_1[6] + -1;
            }
          }
          else {
            lVar11 = param_1[5] + -1;
            param_1[5] = lVar11;
          }
          cVar10 = cVar4;
          if (*(int *)((long)param_1 + 0x14) != -1) {
            param_1[8] = param_1[8] + -1;
          }
          goto LAB_00034d68;
        }
        param_1[6] = param_1[6] + 1;
        param_1[5] = 0;
      } while( true );
    }
    if (uVar6 != 0x2f) goto LAB_00034ffd;
LAB_00034f20:
    do {
      lVar7 = param_1[4] + 1;
      param_1[4] = lVar7;
      lVar11 = param_1[5] + 1;
      param_1[5] = lVar11;
      if (*(char *)(param_1 + 3) == '\0') {
        pbVar2 = (byte *)*param_1;
        if (pbVar2 == (byte *)param_1[1]) {
          *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
          goto LAB_00034de0;
        }
        local_36 = *pbVar2;
        uVar6 = (uint)local_36;
        *param_1 = pbVar2 + 1;
        puVar13 = (undefined *)param_1[8];
        *(uint *)((long)param_1 + 0x14) = uVar6;
        if (puVar13 != (undefined *)param_1[9]) goto LAB_00034f59;
LAB_00034fc8:
        FUN_00033ab0(puVar1,puVar13,&local_36);
      }
      else {
        *(undefined *)(param_1 + 3) = 0;
        if (uVar6 == 0xffffffff) goto LAB_00034de0;
        local_36 = (byte)uVar6;
        puVar13 = (undefined *)param_1[8];
        if (puVar13 == (undefined *)param_1[9]) goto LAB_00034fc8;
LAB_00034f59:
        *puVar13 = (char)uVar6;
        param_1[8] = param_1[8] + 1;
      }
      uVar6 = *(uint *)((long)param_1 + 0x14);
      if (uVar6 == 10) {
        param_1[6] = param_1[6] + 1;
        lVar7 = param_1[4];
        lVar11 = 0;
        goto LAB_00034de0;
      }
      if (0 < (int)uVar6) {
        if (uVar6 == 0xd) break;
        goto LAB_00034f20;
      }
    } while ((int)uVar6 < -1);
LAB_00034dd3:
    lVar7 = param_1[4];
    lVar11 = param_1[5];
LAB_00034de0:
LAB_00034e0b:
    param_1[4] = lVar7 + 1;
    param_1[5] = lVar11 + 1;
    if (*(char *)(param_1 + 3) != '\0') {
      uVar6 = *(uint *)((long)param_1 + 0x14);
      *(undefined *)(param_1 + 3) = 0;
      if (uVar6 == 0xffffffff) goto LAB_00034e9c;
      local_36 = (byte)uVar6;
      puVar13 = (undefined *)param_1[8];
      if (puVar13 == (undefined *)param_1[9]) goto LAB_00034e7c;
LAB_00034e3d:
      *puVar13 = (char)uVar6;
      param_1[8] = param_1[8] + 1;
LAB_00034e44:
      uVar6 = *(uint *)((long)param_1 + 0x14);
      if (uVar6 == 10) {
        param_1[6] = param_1[6] + 1;
        lVar11 = 0;
      }
      else {
        if (((uVar6 & 0xfffffffb) != 9) && (uVar6 != 0x20)) goto LAB_00034e9c;
        lVar11 = param_1[5];
      }
      lVar7 = param_1[4];
      goto LAB_00034e0b;
    }
    pbVar2 = (byte *)*param_1;
    if (pbVar2 != (byte *)param_1[1]) {
      local_36 = *pbVar2;
      uVar6 = (uint)local_36;
      puVar13 = (undefined *)param_1[8];
      *param_1 = pbVar2 + 1;
      *(uint *)((long)param_1 + 0x14) = (uint)local_36;
      if (puVar13 != (undefined *)param_1[9]) goto LAB_00034e3d;
LAB_00034e7c:
      FUN_00033ab0(puVar1,puVar13,&local_36);
      goto LAB_00034e44;
    }
    *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
    uVar6 = 0xffffffff;
LAB_00034e9c:
    cVar10 = *(char *)(param_1 + 2);
    bVar3 = local_36;
  }
  if (0x3a < (int)uVar6) {
    local_36 = bVar3;
    switch(uVar6) {
    case 0x5b:
      uVar9 = 8;
      break;
    default:
      goto switchD_00034ec1_caseD_5c;
    case 0x5d:
      uVar9 = 10;
      break;
    case 0x66:
      local_31 = 0x65;
      puVar12 = (undefined4 *)local_35;
      local_35 = (undefined  [4])0x736c6166;
      do {
        cVar4 = FUN_00033c00(param_1);
        if (*(char *)((long)puVar12 + 1) != cVar4) goto switchD_00034ec1_caseD_5c;
        puVar12 = (undefined4 *)((long)puVar12 + 1);
      } while ((undefined4 *)&local_31 != puVar12);
      uVar9 = 2;
      break;
    case 0x6e:
      local_35 = (undefined  [4])0x6c6c756e;
      puVar12 = (undefined4 *)local_35;
      do {
        cVar4 = FUN_00033c00(param_1);
        if (*(char *)((long)puVar12 + 1) != cVar4) goto switchD_00034ec1_caseD_5c;
        puVar12 = (undefined4 *)((long)puVar12 + 1);
      } while ((undefined4 *)((long)local_35 + 3) != puVar12);
      uVar9 = 3;
      break;
    case 0x74:
      local_35 = (undefined  [4])0x65757274;
      puVar12 = (undefined4 *)local_35;
      do {
        cVar4 = FUN_00033c00(param_1);
        if (*(char *)((long)puVar12 + 1) != cVar4) goto switchD_00034ec1_caseD_5c;
        puVar12 = (undefined4 *)((long)puVar12 + 1);
      } while ((undefined4 *)((long)local_35 + 3) != puVar12);
      uVar9 = 1;
      break;
    case 0x7b:
      uVar9 = 9;
      break;
    case 0x7d:
      uVar9 = 0xb;
    }
    goto LAB_00034ed8;
  }
  local_36 = bVar3;
  if ((int)uVar6 < -1) {
switchD_00034ec1_caseD_5c:
    pcVar8 = "invalid literal";
    goto LAB_00034ecf;
  }
  switch(uVar6) {
  default:
    goto switchD_00034ec1_caseD_5c;
  case 0x22:
    if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
      uVar9 = FUN_00034530(param_1);
      return uVar9;
    }
    goto LAB_00035294;
  case 0x2c:
    uVar9 = 0xd;
    break;
  case 0x2d:
  case 0x30:
  case 0x31:
  case 0x32:
  case 0x33:
  case 0x34:
  case 0x35:
  case 0x36:
  case 0x37:
  case 0x38:
  case 0x39:
    if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
      uVar9 = FUN_00033cd0(param_1);
      return uVar9;
    }
    goto LAB_00035294;
  case 0x3a:
    uVar9 = 0xc;
    break;
  case 0xffffffff:
  case 0:
    uVar9 = 0xf;
  }
LAB_00034ed8:
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar9;
  }
LAB_00035294:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


