// ===== FUNC 2cf40 size=1689

void FUN_0002cf40(ulong param_1,long param_2,int *param_3,int *param_4)

{
  char *pcVar1;
  undefined8 uVar2;
  uint uVar3;
  byte bVar4;
  int iVar5;
  ulong uVar6;
  uint uVar7;
  uint uVar8;
  ulong uVar9;
  int iVar10;
  long lVar11;
  ulong uVar12;
  ulong uVar13;
  int iVar14;
  ulong uVar15;
  ulong uVar16;
  long lVar17;
  ulong uVar18;
  ulong uVar19;
  ulong uVar20;
  bool bVar21;
  ulong local_48;
  
  uVar6 = param_1 & 0xfffffffffffff;
  if (param_1 >> 0x34 == 0) {
    uVar6 = uVar6 * 2;
    iVar10 = -0x433;
    uVar13 = uVar6 + 1;
  }
  else {
    uVar3 = (uint)(param_1 >> 0x20);
    iVar10 = (uVar3 >> 0x14) - 0x434;
    uVar13 = (uVar6 + 0x10000000000000) * 2 + 1;
    if ((uVar6 == 0) && (1 < param_1 >> 0x34)) {
      lVar11 = 0x3fffffffffffff;
      uVar6 = 0x20000000000000;
      iVar5 = (uVar3 >> 0x14) - 0x435;
      goto LAB_0002cfc0;
    }
    uVar6 = (uVar6 + 0x10000000000000) * 2;
  }
  lVar11 = uVar6 - 1;
  iVar5 = iVar10;
LAB_0002cfc0:
  do {
    iVar10 = iVar10 + -1;
    uVar13 = uVar13 * 2;
  } while (-1 < (long)uVar13);
  uVar12 = lVar11 << ((char)iVar5 - (char)iVar10 & 0x3fU);
  for (; -1 < (long)uVar6; uVar6 = uVar6 * 2) {
  }
  iVar14 = (-0x3d - iVar10) * 0x13441;
  iVar5 = iVar14 + 0x3ffff;
  if (-1 < iVar14) {
    iVar5 = iVar14;
  }
  iVar14 = (iVar5 >> 0x12) + (uint)(0 < -0x3d - iVar10);
  iVar5 = iVar14 + 0x133;
  if (iVar5 < 0) {
    iVar5 = iVar14 + 0x13a;
  }
  lVar11 = (long)(iVar5 >> 3) * 0x10;
  uVar2 = *(undefined8 *)(&DAT_000e28a8 + lVar11);
  uVar9 = *(ulong *)(&DAT_000e28a0 + lVar11) & 0xffffffff;
  uVar15 = *(ulong *)(&DAT_000e28a0 + lVar11) >> 0x20;
  uVar16 = (uVar6 & 0xffffffff) * uVar15;
  uVar18 = (uVar6 >> 0x20) * uVar9;
  lVar11 = (((uVar6 & 0xffffffff) * uVar9 >> 0x20) + (uVar16 & 0xffffffff) + 0x80000000 +
            (uVar18 & 0xffffffff) >> 0x20) +
           (uVar6 >> 0x20) * uVar15 + (uVar16 >> 0x20) + (uVar18 >> 0x20);
  uVar16 = uVar12 & 0xffffffff;
  uVar12 = uVar12 >> 0x20;
  uVar19 = uVar16 * uVar15;
  uVar6 = (uVar13 >> 0x20) * uVar9;
  uVar18 = uVar12 * uVar9;
  uVar20 = (uVar13 & 0xffffffff) * uVar15;
  uVar6 = (((uVar13 & 0xffffffff) * uVar9 >> 0x20) + (uVar20 & 0xffffffff) + 0x80000000 +
           (uVar6 & 0xffffffff) >> 0x20) +
          (uVar13 >> 0x20) * uVar15 + -1 + (uVar20 >> 0x20) + (uVar6 >> 0x20);
  local_48._0_4_ = (int)((ulong)uVar2 >> 0x20);
  *param_4 = -(int)local_48;
  uVar13 = ((((uVar6 - uVar12 * uVar15) + -1) - (uVar18 >> 0x20)) - (uVar19 >> 0x20)) -
           ((uVar16 * uVar9 >> 0x20) + (uVar19 & 0xffffffff) + 0x80000000 + (uVar18 & 0xffffffff) >>
           0x20);
  uVar12 = uVar6 - lVar11;
  bVar4 = -((char)iVar10 + (char)uVar2) - 0x40;
  uVar9 = 1L << (bVar4 & 0x3f);
  uVar15 = uVar6 >> (bVar4 & 0x3f);
  uVar3 = (uint)uVar15;
  uVar16 = uVar6 & uVar9 - 1;
  if (uVar3 < 1000000000) {
    if (uVar3 < 100000000) {
      if (uVar3 < 10000000) {
        if (uVar3 < 1000000) {
          if (uVar3 < 100000) {
            if (uVar3 < 10000) {
              if (uVar3 < 1000) {
                if (uVar3 < 100) {
                  if (uVar3 < 10) {
                    local_48 = 1;
                    iVar10 = 0;
                    uVar7 = 0;
                    uVar15 = uVar16;
                    uVar8 = uVar3;
                  }
                  else {
                    local_48 = 10;
                    uVar8 = (uint)((uVar15 & 0xffffffff) / 10);
                    uVar7 = uVar3 + (int)((uVar15 & 0xffffffff) / 10) * -10;
                    iVar10 = 1;
                    uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
                  }
                }
                else {
                  local_48 = 100;
                  uVar8 = (uint)((uVar15 & 0xffffffff) / 100);
                  uVar7 = uVar3 + (int)((uVar15 & 0xffffffff) / 100) * -100;
                  iVar10 = 2;
                  uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
                }
              }
              else {
                local_48 = 1000;
                uVar8 = (uint)((uVar15 & 0xffffffff) / 1000);
                uVar7 = uVar3 + (int)((uVar15 & 0xffffffff) / 1000) * -1000;
                iVar10 = 3;
                uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
              }
            }
            else {
              local_48 = 10000;
              uVar8 = (uint)((uVar15 & 0xffffffff) / 10000);
              uVar7 = uVar3 + (int)((uVar15 & 0xffffffff) / 10000) * -10000;
              iVar10 = 4;
              uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
            }
          }
          else {
            local_48 = 100000;
            uVar15 = uVar15 >> 5 & 0x7ffffff;
            uVar8 = (uint)(uVar15 / 0xc35);
            uVar7 = uVar3 + (int)(uVar15 / 0xc35) * -100000;
            iVar10 = 5;
            uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
          }
        }
        else {
          local_48 = 1000000;
          uVar8 = (uint)((uVar15 & 0xffffffff) / 1000000);
          uVar7 = uVar3 + (int)((uVar15 & 0xffffffff) / 1000000) * -1000000;
          iVar10 = 6;
          uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
        }
      }
      else {
        local_48 = 10000000;
        uVar8 = (uint)((uVar15 & 0xffffffff) / 10000000);
        uVar7 = uVar3 + (int)((uVar15 & 0xffffffff) / 10000000) * -10000000;
        iVar10 = 7;
        uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
      }
    }
    else {
      local_48 = 100000000;
      uVar8 = (uint)((uVar15 & 0xffffffff) / 100000000);
      uVar7 = uVar3 + (int)((uVar15 & 0xffffffff) / 100000000) * -100000000;
      iVar10 = 8;
      uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
    }
  }
  else {
    local_48 = 1000000000;
    uVar7 = (uint)((uVar15 >> 9 & 0x7fffff) * 0x44b83 >> 0x20);
    uVar8 = uVar7 >> 7;
    uVar7 = uVar3 + (uVar7 >> 7) * -1000000000;
    iVar10 = 9;
    uVar15 = ((ulong)uVar7 << (bVar4 & 0x3f)) + uVar16;
  }
  iVar5 = *param_3;
  *param_3 = iVar5 + 1;
  *(char *)(param_2 + iVar5) = (char)uVar8 + '0';
  if (uVar13 < uVar15) {
    do {
      uVar18 = local_48;
      lVar17 = (long)*param_3;
      local_48 = uVar18 / 10;
      if (iVar10 == 0) {
        iVar10 = 0;
        while( true ) {
          iVar10 = iVar10 + 1;
          uVar6 = uVar16 * 10;
          *param_3 = (int)lVar17 + 1;
          uVar16 = uVar9 - 1 & uVar6;
          uVar13 = uVar13 * 10;
          *(char *)(param_2 + lVar17) = (char)(uVar6 >> (bVar4 & 0x3f)) + '0';
          uVar6 = uVar12 * 10;
          if (uVar16 <= uVar13) break;
          lVar17 = (long)*param_3;
          uVar12 = uVar6;
        }
        *param_4 = *param_4 - iVar10;
        iVar10 = *param_3;
        if (uVar6 <= uVar16) {
          return;
        }
        if (uVar13 - uVar16 < uVar9) {
          return;
        }
        pcVar1 = (char *)(param_2 + -1 + (long)iVar10);
        uVar13 = (uVar13 - uVar9) - uVar16;
        while (uVar15 = uVar16 + uVar9, uVar15 < uVar6) {
          *pcVar1 = *pcVar1 + -1;
          bVar21 = uVar13 < uVar9;
          uVar13 = uVar13 - uVar9;
          uVar16 = uVar15;
          if (bVar21) {
            return;
          }
        }
        if (uVar6 - uVar16 <= uVar15 + uVar12 * -10) {
          return;
        }
        pcVar1 = (char *)(param_2 + -1 + (long)iVar10);
        *pcVar1 = *pcVar1 + -1;
        return;
      }
      *param_3 = *param_3 + 1;
      iVar10 = iVar10 + -1;
      uVar15 = (ulong)uVar7;
      uVar19 = uVar15 % local_48;
      uVar7 = (uint)uVar19;
      *(char *)(lVar17 + param_2) = (char)(uVar15 / local_48) + '0';
      uVar15 = (uVar19 << (bVar4 & 0x3f)) + uVar16;
    } while (uVar13 < uVar15);
    local_48 = uVar18 / 10;
  }
  *param_4 = *param_4 + iVar10;
  local_48 = local_48 << (bVar4 & 0x3f);
  iVar10 = *param_3;
  if ((uVar15 < uVar12) && (local_48 <= uVar13 - uVar15)) {
    pcVar1 = (char *)(param_2 + -1 + (long)iVar10);
    uVar13 = (uVar13 - uVar15) - local_48;
    do {
      uVar16 = uVar15 + local_48;
      if (uVar12 <= uVar16) {
        if (uVar12 - uVar15 <= uVar16 + (lVar11 - uVar6)) {
          return;
        }
        pcVar1 = (char *)(param_2 + -1 + (long)iVar10);
        *pcVar1 = *pcVar1 + -1;
        return;
      }
      *pcVar1 = *pcVar1 + -1;
      bVar21 = local_48 <= uVar13;
      uVar15 = uVar16;
      uVar13 = uVar13 - local_48;
    } while (bVar21);
  }
  return;
}


