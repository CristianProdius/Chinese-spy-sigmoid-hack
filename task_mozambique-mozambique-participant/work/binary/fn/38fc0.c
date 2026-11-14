// ===== FUNC 38fc0 size=747

undefined8 * FUN_00038fc0(undefined8 *param_1,long param_2,undefined8 *param_3)

{
  undefined8 *puVar1;
  undefined uVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  long lVar5;
  long lVar6;
  long *plVar7;
  long *plVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  long *plVar12;
  long lVar13;
  undefined8 *puVar14;
  
  param_2 = param_2 - (long)param_1;
  lVar13 = (param_2 >> 5) * 0x2e8ba2e8ba2e8ba3;
  puVar14 = param_3;
  if (0 < param_2) {
    do {
      uVar9 = param_1[2];
      uVar10 = param_1[3];
      lVar5 = puVar14[2];
      lVar6 = puVar14[4];
      *puVar14 = *param_1;
      uVar4 = *(undefined4 *)(param_1 + 1);
      puVar14[2] = uVar9;
      puVar14[3] = uVar10;
      *(undefined4 *)(puVar14 + 1) = uVar4;
      puVar14[4] = param_1[4];
      param_1[4] = 0;
      *(undefined (*) [16])(param_1 + 2) = (undefined  [16])0x0;
      if (lVar5 != 0) {
        thunk_FUN_000d36e0(lVar5,lVar6 - lVar5);
      }
      uVar9 = *(undefined8 *)((long)param_1 + 0xac);
      uVar10 = *(undefined8 *)((long)param_1 + 0xb4);
      uVar11 = param_1[6];
      puVar14[5] = param_1[5];
      puVar14[6] = uVar11;
      uVar11 = param_1[8];
      puVar14[7] = param_1[7];
      puVar14[8] = uVar11;
      uVar11 = param_1[10];
      puVar14[9] = param_1[9];
      puVar14[10] = uVar11;
      uVar11 = param_1[0xc];
      puVar14[0xb] = param_1[0xb];
      puVar14[0xc] = uVar11;
      uVar11 = param_1[0xe];
      puVar14[0xd] = param_1[0xd];
      puVar14[0xe] = uVar11;
      uVar11 = param_1[0x10];
      puVar14[0xf] = param_1[0xf];
      puVar14[0x10] = uVar11;
      uVar11 = param_1[0x12];
      puVar14[0x11] = param_1[0x11];
      puVar14[0x12] = uVar11;
      puVar14[0x13] = param_1[0x13];
      puVar14[0x14] = param_1[0x14];
      uVar3 = *(undefined2 *)(param_1 + 0x15);
      *(undefined8 *)((long)puVar14 + 0xac) = uVar9;
      *(undefined8 *)((long)puVar14 + 0xb4) = uVar10;
      uVar9 = *(undefined8 *)((long)param_1 + 0xbc);
      uVar10 = *(undefined8 *)((long)param_1 + 0xc4);
      *(undefined2 *)(puVar14 + 0x15) = uVar3;
      *(undefined8 *)((long)puVar14 + 0xbc) = uVar9;
      *(undefined8 *)((long)puVar14 + 0xc4) = uVar10;
      *(undefined8 *)((long)puVar14 + 0xcc) = *(undefined8 *)((long)param_1 + 0xcc);
      uVar9 = param_1[0x1c];
      puVar14[0x1b] = param_1[0x1b];
      puVar14[0x1c] = uVar9;
      uVar9 = param_1[0x1e];
      puVar14[0x1d] = param_1[0x1d];
      puVar14[0x1e] = uVar9;
      puVar14[0x1f] = param_1[0x1f];
      uVar11 = param_1[0x21];
      uVar9 = param_1[0x25];
      uVar10 = param_1[0x26];
      lVar5 = puVar14[0x27];
      puVar14[0x20] = param_1[0x20];
      puVar14[0x21] = uVar11;
      plVar7 = (long *)puVar14[0x25];
      uVar11 = param_1[0x23];
      plVar8 = (long *)puVar14[0x26];
      puVar14[0x22] = param_1[0x22];
      puVar14[0x23] = uVar11;
      *(undefined4 *)(puVar14 + 0x24) = *(undefined4 *)(param_1 + 0x24);
      uVar2 = *(undefined *)((long)param_1 + 0x124);
      puVar14[0x25] = uVar9;
      puVar14[0x26] = uVar10;
      *(undefined *)((long)puVar14 + 0x124) = uVar2;
      puVar14[0x27] = param_1[0x27];
      param_1[0x27] = 0;
      *(undefined (*) [16])(param_1 + 0x25) = (undefined  [16])0x0;
      for (plVar12 = plVar7; plVar12 != plVar8; plVar12 = plVar12 + 7) {
        if ((long *)*plVar12 != plVar12 + 2) {
          thunk_FUN_000d36e0((long *)*plVar12,plVar12[2] + 1);
        }
      }
      if (plVar7 != (long *)0x0) {
        thunk_FUN_000d36e0(plVar7,lVar5 - (long)plVar7);
      }
      uVar9 = param_1[0x29];
      lVar5 = puVar14[0x28];
      lVar6 = puVar14[0x2a];
      puVar14[0x28] = param_1[0x28];
      puVar14[0x29] = uVar9;
      puVar14[0x2a] = param_1[0x2a];
      param_1[0x2a] = 0;
      *(undefined (*) [16])(param_1 + 0x28) = (undefined  [16])0x0;
      if (lVar5 != 0) {
        thunk_FUN_000d36e0(lVar5,lVar6 - lVar5);
      }
      puVar1 = param_1 + 0x2b;
      param_1 = param_1 + 0x2c;
      puVar14[0x2b] = *puVar1;
      lVar13 = lVar13 + -1;
      puVar14 = puVar14 + 0x2c;
    } while (lVar13 != 0);
    if (param_2 < 1) {
      param_2 = 0x160;
    }
    return (undefined8 *)((long)param_3 + param_2);
  }
  return param_3;
}


