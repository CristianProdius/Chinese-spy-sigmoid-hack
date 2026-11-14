// ===== FUNC 34530 size=1611

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00034530(long param_1)

{
  undefined *puVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  uint uVar9;
  long in_FS_OFFSET;
  undefined local_49;
  undefined8 local_48;
  undefined8 uStack_40;
  undefined8 local_38;
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  *(undefined8 *)(param_1 + 0x58) = 0;
  **(undefined **)(param_1 + 0x50) = 0;
  puVar1 = *(undefined **)(param_1 + 0x38);
  if (puVar1 != *(undefined **)(param_1 + 0x40)) {
    *(undefined **)(param_1 + 0x40) = puVar1;
  }
  *(undefined8 *)(param_1 + 0x98) = 0xffffffffffffffff;
  local_49 = (undefined)*(undefined4 *)(param_1 + 0x14);
  if (puVar1 == *(undefined **)(param_1 + 0x48)) {
    FUN_00033ab0(param_1 + 0x38,puVar1,&local_49);
  }
  else {
    *puVar1 = local_49;
    *(long *)(param_1 + 0x40) = *(long *)(param_1 + 0x40) + 1;
  }
LAB_00034592:
  do {
    uVar3 = FUN_00033c00(param_1);
    switch(uVar3) {
    case 0:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0000 (NUL) must be escaped to \\u0000";
      goto LAB_000345db;
    case 1:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0001 (SOH) must be escaped to \\u0001";
      goto LAB_000345db;
    case 2:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0002 (STX) must be escaped to \\u0002";
      goto LAB_000345db;
    case 3:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0003 (ETX) must be escaped to \\u0003";
      goto LAB_000345db;
    case 4:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0004 (EOT) must be escaped to \\u0004";
      goto LAB_000345db;
    case 5:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0005 (ENQ) must be escaped to \\u0005";
      goto LAB_000345db;
    case 6:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0006 (ACK) must be escaped to \\u0006";
      goto LAB_000345db;
    case 7:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0007 (BEL) must be escaped to \\u0007";
      goto LAB_000345db;
    case 8:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0008 (BS) must be escaped to \\u0008 or \\b";
      goto LAB_000345db;
    case 9:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0009 (HT) must be escaped to \\u0009 or \\t";
      goto LAB_000345db;
    case 10:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+000A (LF) must be escaped to \\u000A or \\n";
      goto LAB_000345db;
    case 0xb:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+000B (VT) must be escaped to \\u000B";
      goto LAB_000345db;
    case 0xc:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+000C (FF) must be escaped to \\u000C or \\f";
      goto LAB_000345db;
    case 0xd:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+000D (CR) must be escaped to \\u000D or \\r";
      goto LAB_000345db;
    case 0xe:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+000E (SO) must be escaped to \\u000E";
      goto LAB_000345db;
    case 0xf:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+000F (SI) must be escaped to \\u000F";
      goto LAB_000345db;
    case 0x10:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0010 (DLE) must be escaped to \\u0010";
      goto LAB_000345db;
    case 0x11:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0011 (DC1) must be escaped to \\u0011";
      goto LAB_000345db;
    case 0x12:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0012 (DC2) must be escaped to \\u0012";
      goto LAB_000345db;
    case 0x13:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0013 (DC3) must be escaped to \\u0013";
      goto LAB_000345db;
    case 0x14:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0014 (DC4) must be escaped to \\u0014";
      goto LAB_000345db;
    case 0x15:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0015 (NAK) must be escaped to \\u0015";
      goto LAB_000345db;
    case 0x16:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0016 (SYN) must be escaped to \\u0016";
      goto LAB_000345db;
    case 0x17:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0017 (ETB) must be escaped to \\u0017";
      goto LAB_000345db;
    case 0x18:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0018 (CAN) must be escaped to \\u0018";
      goto LAB_000345db;
    case 0x19:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+0019 (EM) must be escaped to \\u0019";
      goto LAB_000345db;
    case 0x1a:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+001A (SUB) must be escaped to \\u001A";
      goto LAB_000345db;
    case 0x1b:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+001B (ESC) must be escaped to \\u001B";
      goto LAB_000345db;
    case 0x1c:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+001C (FS) must be escaped to \\u001C";
      goto LAB_000345db;
    case 0x1d:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+001D (GS) must be escaped to \\u001D";
      goto LAB_000345db;
    case 0x1e:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+001E (RS) must be escaped to \\u001E";
      goto LAB_000345db;
    case 0x1f:
      *(char **)(param_1 + 0x70) =
           "invalid string: control character U+001F (US) must be escaped to \\u001F";
      goto LAB_000345db;
    case 0x20:
    case 0x21:
    case 0x23:
    case 0x24:
    case 0x25:
    case 0x26:
    case 0x27:
    case 0x28:
    case 0x29:
    case 0x2a:
    case 0x2b:
    case 0x2c:
    case 0x2d:
    case 0x2e:
    case 0x2f:
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
    case 0x3a:
    case 0x3b:
    case 0x3c:
    case 0x3d:
    case 0x3e:
    case 0x3f:
    case 0x40:
    case 0x41:
    case 0x42:
    case 0x43:
    case 0x44:
    case 0x45:
    case 0x46:
    case 0x47:
    case 0x48:
    case 0x49:
    case 0x4a:
    case 0x4b:
    case 0x4c:
    case 0x4d:
    case 0x4e:
    case 0x4f:
    case 0x50:
    case 0x51:
    case 0x52:
    case 0x53:
    case 0x54:
    case 0x55:
    case 0x56:
    case 0x57:
    case 0x58:
    case 0x59:
    case 0x5a:
    case 0x5b:
    case 0x5d:
    case 0x5e:
    case 0x5f:
    case 0x60:
    case 0x61:
    case 0x62:
    case 99:
    case 100:
    case 0x65:
    case 0x66:
    case 0x67:
    case 0x68:
    case 0x69:
    case 0x6a:
    case 0x6b:
    case 0x6c:
    case 0x6d:
    case 0x6e:
    case 0x6f:
    case 0x70:
    case 0x71:
    case 0x72:
    case 0x73:
    case 0x74:
    case 0x75:
    case 0x76:
    case 0x77:
    case 0x78:
    case 0x79:
    case 0x7a:
    case 0x7b:
    case 0x7c:
    case 0x7d:
    case 0x7e:
    case 0x7f:
      FUN_000b1530(param_1 + 0x50,(int)*(char *)(param_1 + 0x14));
      goto LAB_00034592;
    case 0x22:
      uVar6 = 4;
      goto LAB_000345e0;
    case 0x5c:
      iVar4 = FUN_00033c00(param_1);
      if (iVar4 < 0x76) {
        if (iVar4 < 0x5c) {
          if (iVar4 == 0x22) {
            FUN_000b1530(param_1 + 0x50,0x22);
            goto LAB_00034592;
          }
          if (iVar4 == 0x2f) {
            FUN_000b1530(param_1 + 0x50,0x2f);
            goto LAB_00034592;
          }
        }
        else {
          switch(iVar4) {
          case 0x5c:
            FUN_000b1530(param_1 + 0x50,0x5c);
            goto LAB_00034592;
          case 0x62:
            FUN_000b1530(param_1 + 0x50,8);
            goto LAB_00034592;
          case 0x66:
            FUN_000b1530(param_1 + 0x50,0xc);
            goto LAB_00034592;
          case 0x6e:
            FUN_000b1530(param_1 + 0x50,10);
            goto LAB_00034592;
          case 0x72:
            FUN_000b1530(param_1 + 0x50,0xd);
            goto LAB_00034592;
          case 0x74:
            FUN_000b1530(param_1 + 0x50,9);
            goto LAB_00034592;
          case 0x75:
            uVar7 = FUN_00034140(param_1);
            uVar5 = (uint)uVar7;
            uVar7 = uVar7 & 0xffffffff;
            if (uVar5 == 0xffffffff) {
LAB_00034b72:
              *(char **)(param_1 + 0x70) =
                   "invalid string: \'\\u\' must be followed by 4 hex digits";
              goto LAB_000345db;
            }
            if (uVar5 - 0xd800 < 0x400) {
              iVar4 = FUN_00033c00(param_1);
              if ((iVar4 == 0x5c) && (iVar4 = FUN_00033c00(param_1), iVar4 == 0x75)) {
                iVar4 = FUN_00034140(param_1);
                if (iVar4 == -1) goto LAB_00034b72;
                if (iVar4 - 0xdc00U < 0x400) {
                  uVar7 = (ulong)(iVar4 + -0x35fdc00 + uVar5 * 0x400);
                  goto LAB_00034ac8;
                }
              }
              *(char **)(param_1 + 0x70) =
                   "invalid string: surrogate U+D800..U+DBFF must be followed by U+DC00..U+DFFF";
              goto LAB_000345db;
            }
            if (uVar5 - 0xdc00 < 0x400) {
              *(char **)(param_1 + 0x70) =
                   "invalid string: surrogate U+DC00..U+DFFF must follow U+D800..U+DBFF";
              goto LAB_000345db;
            }
            lVar8 = param_1 + 0x50;
            if ((int)uVar5 < 0x80) {
              FUN_000b1530(lVar8,(int)(char)uVar7);
            }
            else {
              uVar9 = uVar5 & 0x3f | 0xffffff80;
              if ((int)uVar5 < 0x800) {
                FUN_000b1530(lVar8,(int)(char)((byte)(uVar7 >> 6) | 0xc0));
                FUN_000b1530(lVar8,uVar9);
              }
              else if ((int)uVar5 < 0x10000) {
                FUN_000b1530(lVar8,(int)(char)((byte)(uVar7 >> 0xc) | 0xe0));
                FUN_000b1530(lVar8,(uint)(uVar7 >> 6) & 0x3f | 0xffffff80);
                FUN_000b1530(lVar8,uVar9);
              }
              else {
LAB_00034ac8:
                lVar8 = param_1 + 0x50;
                FUN_000b1530(lVar8,(int)(char)((byte)(uVar7 >> 0x12) | 0xf0));
                FUN_000b1530(lVar8,(uint)(uVar7 >> 0xc) & 0x3f | 0xffffff80);
                FUN_000b1530(lVar8,(uint)(uVar7 >> 6) & 0x3f | 0xffffff80);
                FUN_000b1530(lVar8,(uint)uVar7 & 0x3f | 0xffffff80);
              }
            }
            goto LAB_00034592;
          }
        }
      }
      *(char **)(param_1 + 0x70) = "invalid string: forbidden character after backslash";
      goto LAB_000345db;
    default:
      *(char **)(param_1 + 0x70) = "invalid string: ill-formed UTF-8 byte";
      goto LAB_000345db;
    case 0xc2:
    case 0xc3:
    case 0xc4:
    case 0xc5:
    case 0xc6:
    case 199:
    case 200:
    case 0xc9:
    case 0xca:
    case 0xcb:
    case 0xcc:
    case 0xcd:
    case 0xce:
    case 0xcf:
    case 0xd0:
    case 0xd1:
    case 0xd2:
    case 0xd3:
    case 0xd4:
    case 0xd5:
    case 0xd6:
    case 0xd7:
    case 0xd8:
    case 0xd9:
    case 0xda:
    case 0xdb:
    case 0xdc:
    case 0xdd:
    case 0xde:
    case 0xdf:
      local_48 = DAT_000e2ef0;
      cVar2 = FUN_000342c0(param_1,&local_48,2);
      goto joined_r0x0003468d;
    case 0xe0:
      local_48 = _DAT_000e2ee0;
      uStack_40 = _UNK_000e2ee8;
      break;
    case 0xe1:
    case 0xe2:
    case 0xe3:
    case 0xe4:
    case 0xe5:
    case 0xe6:
    case 0xe7:
    case 0xe8:
    case 0xe9:
    case 0xea:
    case 0xeb:
    case 0xec:
    case 0xee:
    case 0xef:
      local_48 = DAT_000e2ef0;
      uStack_40 = _UNK_000e2ef8;
      break;
    case 0xed:
      local_48 = _DAT_000e2f00;
      uStack_40 = _UNK_000e2f08;
      break;
    case 0xf0:
      local_48 = _DAT_000e2f10;
      uStack_40 = _UNK_000e2f18;
      goto LAB_00034668;
    case 0xf1:
    case 0xf2:
    case 0xf3:
      local_48 = DAT_000e2ef0;
      uStack_40 = _UNK_000e2ef8;
      goto LAB_00034668;
    case 0xf4:
      local_48 = _DAT_000e2f20;
      uStack_40 = _UNK_000e2f28;
LAB_00034668:
      local_38 = DAT_000e2ef0;
      cVar2 = FUN_000342c0(param_1,&local_48,6);
      goto joined_r0x0003468d;
    case 0xffffffff:
      *(char **)(param_1 + 0x70) = "invalid string: missing closing quote";
      goto LAB_000345db;
    }
    cVar2 = FUN_000342c0(param_1,&local_48,4);
joined_r0x0003468d:
    if (cVar2 == '\0') {
LAB_000345db:
      uVar6 = 0xe;
LAB_000345e0:
      if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
        return uVar6;
      }
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
  } while( true );
}


