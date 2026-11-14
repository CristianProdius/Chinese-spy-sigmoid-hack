// ===== FUNC 18bf0 size=486

void FUN_00018bf0(undefined8 *param_1,undefined8 *param_2)

{
  undefined uVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  long lVar4;
  long lVar5;
  undefined8 uVar6;
  long *plVar7;
  long *plVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  long *plVar13;
  
  uVar6 = param_2[2];
  uVar9 = param_2[3];
  *param_1 = *param_2;
  lVar4 = param_1[4];
  *(undefined4 *)(param_1 + 1) = *(undefined4 *)(param_2 + 1);
  lVar5 = param_1[2];
  param_1[2] = uVar6;
  param_1[3] = uVar9;
  param_1[4] = param_2[4];
  param_2[4] = 0;
  *(undefined (*) [16])(param_2 + 2) = (undefined  [16])0x0;
  if (lVar5 != 0) {
    thunk_FUN_000d36e0(lVar5,lVar4 - lVar5);
  }
  uVar6 = param_2[6];
  param_1[5] = param_2[5];
  param_1[6] = uVar6;
  uVar6 = param_2[8];
  uVar9 = *(undefined8 *)((long)param_2 + 0xac);
  uVar10 = *(undefined8 *)((long)param_2 + 0xb4);
  param_1[7] = param_2[7];
  param_1[8] = uVar6;
  uVar6 = param_2[10];
  param_1[9] = param_2[9];
  param_1[10] = uVar6;
  uVar6 = param_2[0xc];
  uVar11 = param_2[0x1b];
  uVar12 = param_2[0x1c];
  param_1[0xb] = param_2[0xb];
  param_1[0xc] = uVar6;
  uVar6 = param_2[0xe];
  param_1[0xd] = param_2[0xd];
  param_1[0xe] = uVar6;
  uVar6 = param_2[0x10];
  param_1[0xf] = param_2[0xf];
  param_1[0x10] = uVar6;
  uVar6 = param_2[0x12];
  param_1[0x11] = param_2[0x11];
  param_1[0x12] = uVar6;
  param_1[0x13] = param_2[0x13];
  param_1[0x14] = param_2[0x14];
  uVar2 = *(undefined2 *)(param_2 + 0x15);
  *(undefined8 *)((long)param_1 + 0xac) = uVar9;
  *(undefined8 *)((long)param_1 + 0xb4) = uVar10;
  uVar6 = *(undefined8 *)((long)param_2 + 0xbc);
  uVar9 = *(undefined8 *)((long)param_2 + 0xc4);
  *(undefined2 *)(param_1 + 0x15) = uVar2;
  *(undefined8 *)((long)param_1 + 0xbc) = uVar6;
  *(undefined8 *)((long)param_1 + 0xc4) = uVar9;
  uVar6 = *(undefined8 *)((long)param_2 + 0xcc);
  param_1[0x1b] = uVar11;
  param_1[0x1c] = uVar12;
  uVar9 = param_2[0x1d];
  uVar10 = param_2[0x1e];
  *(undefined8 *)((long)param_1 + 0xcc) = uVar6;
  param_1[0x1d] = uVar9;
  param_1[0x1e] = uVar10;
  param_1[0x1f] = param_2[0x1f];
  uVar6 = param_2[0x21];
  uVar3 = *(undefined4 *)(param_2 + 0x24);
  uVar9 = param_2[0x25];
  uVar10 = param_2[0x26];
  param_1[0x20] = param_2[0x20];
  param_1[0x21] = uVar6;
  uVar11 = param_2[0x22];
  uVar12 = param_2[0x23];
  plVar7 = (long *)param_1[0x25];
  *(undefined4 *)(param_1 + 0x24) = uVar3;
  uVar1 = *(undefined *)((long)param_2 + 0x124);
  plVar8 = (long *)param_1[0x26];
  param_1[0x25] = uVar9;
  param_1[0x26] = uVar10;
  lVar4 = param_1[0x27];
  *(undefined *)((long)param_1 + 0x124) = uVar1;
  uVar6 = param_2[0x27];
  param_1[0x22] = uVar11;
  param_1[0x23] = uVar12;
  param_1[0x27] = uVar6;
  param_2[0x27] = 0;
  *(undefined (*) [16])(param_2 + 0x25) = (undefined  [16])0x0;
  for (plVar13 = plVar7; plVar13 != plVar8; plVar13 = plVar13 + 7) {
    if ((long *)*plVar13 != plVar13 + 2) {
      thunk_FUN_000d36e0((long *)*plVar13,plVar13[2] + 1);
    }
  }
  if (plVar7 != (long *)0x0) {
    thunk_FUN_000d36e0(plVar7,lVar4 - (long)plVar7);
    return;
  }
  return;
}


