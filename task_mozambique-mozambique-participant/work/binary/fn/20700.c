// ===== FUNC 20700 size=916

void FUN_00020700(long *param_1,ulong param_2)

{
  ulong uVar1;
  undefined uVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  undefined8 uVar16;
  undefined8 uVar17;
  undefined8 *puVar18;
  undefined8 *puVar19;
  ulong uVar20;
  long lVar21;
  ulong uVar22;
  long lVar23;
  undefined8 *puVar24;
  undefined8 *puVar25;
  undefined8 *puVar26;
  undefined8 *puVar27;
  long lVar28;
  byte bVar29;
  
  bVar29 = 0;
  if (param_2 == 0) {
    return;
  }
  puVar25 = (undefined8 *)param_1[1];
  lVar23 = *param_1;
  lVar21 = (long)puVar25 - lVar23 >> 5;
  uVar22 = lVar21 * 0x2e8ba2e8ba2e8ba3;
  if (param_2 <= (ulong)((param_1[2] - (long)puVar25 >> 5) * 0x2e8ba2e8ba2e8ba3)) {
    puVar24 = puVar25;
    do {
      puVar19 = puVar24 + 0x2c;
      puVar26 = puVar24;
      for (lVar23 = 0x2c; lVar23 != 0; lVar23 = lVar23 + -1) {
        *puVar26 = 0;
        puVar26 = puVar26 + 1;
      }
      *(undefined (*) [16])(puVar24 + 2) = (undefined  [16])0x0;
      *(undefined (*) [16])((long)puVar24 + 0xac) = (undefined  [16])0x0;
      *(undefined (*) [16])((long)puVar24 + 0xbc) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar24 + 0x1b) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar24 + 0x1d) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar24 + 0x20) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar24 + 0x22) = (undefined  [16])0x0;
      *(undefined *)((long)puVar24 + 0x124) = 1;
      *(undefined (*) [16])(puVar24 + 0x25) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar24 + 0x27) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar24 + 0x29) = (undefined  [16])0x0;
      puVar24 = puVar19;
    } while (puVar19 != puVar25 + param_2 * 0x2c);
    param_1[1] = (long)puVar19;
    return;
  }
  if (param_2 <= lVar21 * -0x2e8ba2e8ba2e8ba3 + 0x5d1745d1745d17U) {
    uVar1 = param_2 + uVar22;
    if (uVar22 < param_2) {
      uVar22 = 0x5d1745d1745d17;
      if (uVar1 < 0x5d1745d1745d18) {
        uVar22 = uVar1;
      }
      lVar28 = uVar22 * 0x160;
    }
    else {
      lVar28 = 0x7fffffffffffffa0;
      uVar20 = lVar21 * 0x5d1745d1745d1746;
      if (uVar22 <= uVar20) {
        if (0x5d1745d1745d17 < uVar20) {
          uVar20 = 0x5d1745d1745d17;
        }
        lVar28 = uVar20 * 0x160;
      }
    }
    puVar19 = (undefined8 *)FUN_00041fe0(lVar28);
    puVar24 = (undefined8 *)param_1[1];
    puVar26 = (undefined8 *)*param_1;
    lVar21 = param_1[2];
    puVar25 = (undefined8 *)(((long)puVar25 - lVar23) + (long)puVar19);
    do {
      puVar27 = puVar25;
      for (lVar23 = 0x2c; lVar23 != 0; lVar23 = lVar23 + -1) {
        *puVar27 = 0;
        puVar27 = puVar27 + (ulong)bVar29 * -2 + 1;
      }
      *(undefined (*) [16])(puVar25 + 2) = (undefined  [16])0x0;
      *(undefined (*) [16])((long)puVar25 + 0xac) = (undefined  [16])0x0;
      *(undefined (*) [16])((long)puVar25 + 0xbc) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar25 + 0x1b) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar25 + 0x1d) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar25 + 0x20) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar25 + 0x22) = (undefined  [16])0x0;
      *(undefined *)((long)puVar25 + 0x124) = 1;
      *(undefined (*) [16])(puVar25 + 0x25) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar25 + 0x27) = (undefined  [16])0x0;
      *(undefined (*) [16])(puVar25 + 0x29) = (undefined  [16])0x0;
      param_2 = param_2 - 1;
      puVar25 = puVar25 + 0x2c;
      puVar27 = puVar26;
      puVar18 = puVar19;
    } while (param_2 != 0);
    for (; puVar24 != puVar27; puVar27 = puVar27 + 0x2c) {
      uVar5 = puVar27[2];
      uVar6 = puVar27[3];
      uVar7 = puVar27[5];
      uVar8 = puVar27[6];
      uVar9 = puVar27[7];
      uVar10 = puVar27[8];
      *puVar18 = *puVar27;
      uVar4 = *(undefined4 *)(puVar27 + 1);
      uVar11 = puVar27[9];
      uVar12 = puVar27[10];
      uVar13 = puVar27[0xb];
      uVar14 = puVar27[0xc];
      puVar18[2] = uVar5;
      puVar18[3] = uVar6;
      *(undefined4 *)(puVar18 + 1) = uVar4;
      uVar5 = puVar27[4];
      uVar6 = puVar27[0xd];
      uVar15 = puVar27[0xe];
      uVar16 = puVar27[0xf];
      uVar17 = puVar27[0x10];
      puVar18[5] = uVar7;
      puVar18[6] = uVar8;
      puVar18[4] = uVar5;
      uVar5 = puVar27[0x13];
      uVar7 = puVar27[0x11];
      uVar8 = puVar27[0x12];
      puVar18[7] = uVar9;
      puVar18[8] = uVar10;
      uVar9 = *(undefined8 *)((long)puVar27 + 0xac);
      uVar10 = *(undefined8 *)((long)puVar27 + 0xb4);
      puVar18[0x13] = uVar5;
      uVar5 = puVar27[0x14];
      puVar18[9] = uVar11;
      puVar18[10] = uVar12;
      uVar11 = *(undefined8 *)((long)puVar27 + 0xbc);
      uVar12 = *(undefined8 *)((long)puVar27 + 0xc4);
      puVar18[0x14] = uVar5;
      uVar3 = *(undefined2 *)(puVar27 + 0x15);
      puVar18[0xb] = uVar13;
      puVar18[0xc] = uVar14;
      puVar18[0xd] = uVar6;
      puVar18[0xe] = uVar15;
      puVar18[0xf] = uVar16;
      puVar18[0x10] = uVar17;
      puVar18[0x11] = uVar7;
      puVar18[0x12] = uVar8;
      *(undefined8 *)((long)puVar18 + 0xac) = uVar9;
      *(undefined8 *)((long)puVar18 + 0xb4) = uVar10;
      *(undefined8 *)((long)puVar18 + 0xbc) = uVar11;
      *(undefined8 *)((long)puVar18 + 0xc4) = uVar12;
      *(undefined2 *)(puVar18 + 0x15) = uVar3;
      uVar6 = puVar27[0x20];
      uVar7 = puVar27[0x21];
      uVar8 = puVar27[0x22];
      uVar9 = puVar27[0x23];
      *(undefined8 *)((long)puVar18 + 0xcc) = *(undefined8 *)((long)puVar27 + 0xcc);
      uVar5 = puVar27[0x1f];
      uVar10 = puVar27[0x1b];
      uVar11 = puVar27[0x1c];
      uVar12 = puVar27[0x1d];
      uVar13 = puVar27[0x1e];
      puVar18[0x20] = uVar6;
      puVar18[0x21] = uVar7;
      puVar18[0x1f] = uVar5;
      uVar4 = *(undefined4 *)(puVar27 + 0x24);
      puVar18[0x1b] = uVar10;
      puVar18[0x1c] = uVar11;
      *(undefined4 *)(puVar18 + 0x24) = uVar4;
      uVar2 = *(undefined *)((long)puVar27 + 0x124);
      puVar18[0x1d] = uVar12;
      puVar18[0x1e] = uVar13;
      puVar18[0x22] = uVar8;
      puVar18[0x23] = uVar9;
      *(undefined *)((long)puVar18 + 0x124) = uVar2;
      uVar5 = puVar27[0x26];
      uVar6 = puVar27[0x27];
      uVar7 = puVar27[0x28];
      uVar8 = puVar27[0x29];
      uVar9 = puVar27[0x2a];
      puVar18[0x25] = puVar27[0x25];
      puVar18[0x26] = uVar5;
      puVar18[0x27] = uVar6;
      puVar18[0x28] = uVar7;
      puVar18[0x29] = uVar8;
      puVar18[0x2a] = uVar9;
      puVar18[0x2b] = puVar27[0x2b];
      puVar18 = puVar18 + 0x2c;
    }
    if (puVar26 != (undefined8 *)0x0) {
      thunk_FUN_000d36e0(puVar26,lVar21 - (long)puVar26);
    }
    *param_1 = (long)puVar19;
    param_1[2] = lVar28 + (long)puVar19;
    param_1[1] = (long)(puVar19 + uVar1 * 0x2c);
    return;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("vector::_M_default_append");
}


