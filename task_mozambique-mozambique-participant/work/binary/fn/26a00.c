// ===== FUNC 26a00 size=598

void FUN_00026a00(undefined8 *param_1,undefined8 *param_2)

{
  undefined uVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  undefined8 *puVar4;
  undefined8 *puVar5;
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
  undefined8 uVar18;
  undefined8 uVar19;
  undefined8 *puVar20;
  long lVar21;
  undefined8 uVar22;
  undefined8 *puVar23;
  undefined8 *puVar24;
  undefined8 *puVar25;
  ulong uVar26;
  
  uVar26 = param_2[3] - param_2[2];
  *param_1 = *param_2;
  uVar3 = *(undefined4 *)(param_2 + 1);
  param_1[4] = 0;
  *(undefined4 *)(param_1 + 1) = uVar3;
  *(undefined (*) [16])(param_1 + 2) = (undefined  [16])0x0;
  if (uVar26 == 0) {
    uVar26 = 0;
    puVar20 = (undefined8 *)0x0;
  }
  else {
    if (0x7ffffffffffffff8 < uVar26) {
      FUN_00015c88();
      goto LAB_00026c49;
    }
    puVar20 = (undefined8 *)FUN_00041fe0(uVar26);
  }
  param_1[4] = uVar26 + (long)puVar20;
  param_1[2] = puVar20;
  param_1[3] = puVar20;
  puVar4 = (undefined8 *)param_2[3];
  puVar5 = (undefined8 *)param_2[2];
  puVar23 = puVar20;
  puVar24 = puVar5;
  if (puVar4 != puVar5) {
    do {
      uVar22 = puVar24[1];
      puVar25 = puVar24 + 3;
      *puVar23 = *puVar24;
      puVar23[1] = uVar22;
      puVar23[2] = puVar24[2];
      puVar23 = puVar23 + 3;
      puVar24 = puVar25;
    } while (puVar4 != puVar25);
    puVar20 = (undefined8 *)
              ((long)puVar20 + ((long)puVar4 + (-0x18 - (long)puVar5) & 0xfffffffffffffff8U) + 0x18)
    ;
  }
  param_1[3] = puVar20;
  uVar6 = param_2[5];
  uVar7 = param_2[6];
  uVar8 = param_2[7];
  uVar9 = param_2[8];
  param_1[0x13] = param_2[0x13];
  uVar22 = param_2[0x14];
  uVar10 = param_2[9];
  uVar11 = param_2[10];
  uVar12 = param_2[0xb];
  uVar13 = param_2[0xc];
  param_1[5] = uVar6;
  param_1[6] = uVar7;
  uVar14 = param_2[0xd];
  uVar15 = param_2[0xe];
  uVar16 = param_2[0xf];
  uVar17 = param_2[0x10];
  param_1[0x14] = uVar22;
  uVar2 = *(undefined2 *)(param_2 + 0x15);
  uVar18 = param_2[0x11];
  uVar19 = param_2[0x12];
  param_1[7] = uVar8;
  param_1[8] = uVar9;
  param_1[9] = uVar10;
  param_1[10] = uVar11;
  uVar6 = *(undefined8 *)((long)param_2 + 0xac);
  uVar7 = *(undefined8 *)((long)param_2 + 0xb4);
  uVar8 = *(undefined8 *)((long)param_2 + 0xbc);
  uVar9 = *(undefined8 *)((long)param_2 + 0xc4);
  *(undefined2 *)(param_1 + 0x15) = uVar2;
  uVar22 = *(undefined8 *)((long)param_2 + 0xcc);
  param_1[0xb] = uVar12;
  param_1[0xc] = uVar13;
  uVar10 = param_2[0x1b];
  uVar11 = param_2[0x1c];
  *(undefined8 *)((long)param_1 + 0xcc) = uVar22;
  uVar22 = param_2[0x1f];
  param_1[0xd] = uVar14;
  param_1[0xe] = uVar15;
  uVar12 = param_2[0x1d];
  uVar13 = param_2[0x1e];
  param_1[0xf] = uVar16;
  param_1[0x10] = uVar17;
  param_1[0x11] = uVar18;
  param_1[0x12] = uVar19;
  *(undefined8 *)((long)param_1 + 0xac) = uVar6;
  *(undefined8 *)((long)param_1 + 0xb4) = uVar7;
  *(undefined8 *)((long)param_1 + 0xbc) = uVar8;
  *(undefined8 *)((long)param_1 + 0xc4) = uVar9;
  param_1[0x1b] = uVar10;
  param_1[0x1c] = uVar11;
  param_1[0x1d] = uVar12;
  param_1[0x1e] = uVar13;
  param_1[0x1f] = uVar22;
  uVar22 = param_2[0x20];
  uVar6 = param_2[0x21];
  uVar7 = param_2[0x22];
  uVar8 = param_2[0x23];
  *(undefined4 *)(param_1 + 0x24) = *(undefined4 *)(param_2 + 0x24);
  uVar1 = *(undefined *)((long)param_2 + 0x124);
  uVar26 = param_2[0x26] - param_2[0x25];
  param_1[0x20] = uVar22;
  param_1[0x21] = uVar6;
  *(undefined *)((long)param_1 + 0x124) = uVar1;
  param_1[0x27] = 0;
  param_1[0x22] = uVar7;
  param_1[0x23] = uVar8;
  *(undefined (*) [16])(param_1 + 0x25) = (undefined  [16])0x0;
  if (uVar26 == 0) {
    lVar21 = 0;
  }
  else {
    if (0x7ffffffffffffff8 < uVar26) {
LAB_00026c49:
                    /* try { // try from 00026c49 to 00026c4d has its CatchHandler @ 00026c4e */
      uVar22 = FUN_00015c88();
                    /* catch() { ... } // from try @ 00026be7 with catch @ 00026c4e
                       catch() { ... } // from try @ 00026c49 with catch @ 00026c4e */
      FUN_0001cb50(param_1 + 2);
                    /* WARNING: Subroutine does not return */
      FUN_000ddde0(uVar22);
    }
                    /* try { // try from 00026be7 to 00026beb has its CatchHandler @ 00026c4e */
    lVar21 = FUN_00041fe0(uVar26);
  }
  param_1[0x27] = uVar26 + lVar21;
  param_1[0x25] = lVar21;
  param_1[0x26] = lVar21;
                    /* try { // try from 00026c17 to 00026c1b has its CatchHandler @ 00026c53 */
  uVar22 = FUN_000268c0(param_2[0x25],param_2[0x26]);
  param_1[0x26] = uVar22;
  return;
}


