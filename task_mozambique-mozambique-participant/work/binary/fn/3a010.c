// ===== FUNC 3a010 size=3302

void FUN_0003a010(undefined8 *param_1,undefined8 *param_2,undefined8 *param_3,long param_4,
                 long param_5,undefined8 *param_6,long param_7)

{
  double *pdVar1;
  double dVar2;
  undefined uVar3;
  undefined2 uVar4;
  undefined4 uVar5;
  bool bVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 *puVar11;
  undefined8 uVar12;
  undefined8 *puVar13;
  long lVar14;
  long lVar15;
  long in_FS_OFFSET;
  undefined8 *local_80;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  long local_40;
  
  while( true ) {
    local_40 = *(long *)(in_FS_OFFSET + 0x28);
    lVar14 = param_7;
    if (param_5 <= param_7) {
      lVar14 = param_5;
    }
    if (param_4 <= lVar14) {
      puVar11 = (undefined8 *)FUN_00038fc0(param_1,param_2,param_6);
      if (param_6 == puVar11) goto LAB_0003a8e8;
      goto LAB_0003a651;
    }
    if (param_5 <= param_7) break;
    if (param_5 < param_4) {
      lVar14 = param_4 / 2;
      puVar11 = param_1 + lVar14 * 0x2c;
      local_80 = (undefined8 *)FUN_0001a930(param_2,param_3,puVar11);
      lVar15 = ((long)local_80 - (long)param_2 >> 5) * 0x2e8ba2e8ba2e8ba3;
    }
    else {
      lVar15 = param_5 / 2;
      local_80 = param_2 + lVar15 * 0x2c;
      puVar11 = (undefined8 *)FUN_0001a9c0(param_1,param_2,local_80);
      lVar14 = ((long)puVar11 - (long)param_1 >> 5) * 0x2e8ba2e8ba2e8ba3;
    }
    param_4 = param_4 - lVar14;
    if ((lVar15 < param_4) && (lVar15 <= param_7)) {
      puVar13 = puVar11;
      if (lVar15 != 0) {
        uVar12 = FUN_00038fc0(param_2,local_80,param_6);
        FUN_00038ca0(puVar11,param_2,local_80);
        puVar13 = (undefined8 *)FUN_00038fc0(param_6,uVar12,puVar11);
      }
    }
    else if (param_7 < param_4) {
      puVar13 = (undefined8 *)FUN_0002ca30(puVar11,param_2,local_80);
    }
    else {
      puVar13 = local_80;
      if (param_4 != 0) {
        uVar12 = FUN_00038fc0(puVar11,param_2,param_6);
        FUN_00038fc0(param_2,local_80,puVar11);
        puVar13 = (undefined8 *)FUN_00038ca0(param_6,uVar12,local_80);
      }
    }
    FUN_0003a010(param_1,puVar11,puVar13,lVar14,lVar15,param_6,param_7);
    if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) goto LAB_0003ad32;
    param_5 = param_5 - lVar15;
    param_2 = local_80;
    param_1 = puVar13;
  }
  puVar11 = (undefined8 *)FUN_00038fc0(param_2,param_3,param_6);
  if (param_1 != param_2) {
    if (param_6 == puVar11) goto LAB_0003a8e8;
    param_2 = param_2 + -0x2c;
    puVar11 = puVar11 + -0x2c;
    puVar13 = param_3;
    goto LAB_0003a3e4;
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) goto LAB_0003ad02;
  goto LAB_0003ad32;
LAB_0003a3e4:
  param_3 = puVar13 + -0x2c;
  if ((double)puVar11[0x2b] == (double)param_2[0x2b]) {
    bVar6 = *(int *)(puVar11 + 0x24) < *(int *)(param_2 + 0x24);
  }
  else {
    bVar6 = (double)param_2[0x2b] < (double)puVar11[0x2b];
  }
  lVar14 = puVar13[-0x2a];
  lVar15 = puVar13[-0x28];
  if (bVar6) {
    uVar12 = param_2[2];
    uVar7 = param_2[3];
    *param_3 = *param_2;
    uVar5 = *(undefined4 *)(param_2 + 1);
    puVar13[-0x2a] = uVar12;
    puVar13[-0x29] = uVar7;
    *(undefined4 *)(puVar13 + -0x2b) = uVar5;
    puVar13[-0x28] = param_2[4];
    param_2[4] = 0;
    *(undefined (*) [16])(param_2 + 2) = (undefined  [16])0x0;
    if (lVar14 != 0) {
      thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
    }
    uVar12 = param_2[6];
    uVar7 = *(undefined8 *)((long)param_2 + 0xac);
    uVar8 = *(undefined8 *)((long)param_2 + 0xb4);
    puVar13[-0x27] = param_2[5];
    puVar13[-0x26] = uVar12;
    uVar12 = param_2[8];
    puVar13[-0x25] = param_2[7];
    puVar13[-0x24] = uVar12;
    uVar12 = param_2[10];
    puVar13[-0x23] = param_2[9];
    puVar13[-0x22] = uVar12;
    uVar12 = param_2[0xc];
    puVar13[-0x21] = param_2[0xb];
    puVar13[-0x20] = uVar12;
    uVar12 = param_2[0xe];
    puVar13[-0x1f] = param_2[0xd];
    puVar13[-0x1e] = uVar12;
    uVar12 = param_2[0x10];
    puVar13[-0x1d] = param_2[0xf];
    puVar13[-0x1c] = uVar12;
    uVar12 = param_2[0x12];
    puVar13[-0x1b] = param_2[0x11];
    puVar13[-0x1a] = uVar12;
    puVar13[-0x19] = param_2[0x13];
    puVar13[-0x18] = param_2[0x14];
    uVar4 = *(undefined2 *)(param_2 + 0x15);
    *(undefined8 *)((long)puVar13 + -0xb4) = uVar7;
    *(undefined8 *)((long)puVar13 + -0xac) = uVar8;
    uVar12 = *(undefined8 *)((long)param_2 + 0xbc);
    uVar7 = *(undefined8 *)((long)param_2 + 0xc4);
    *(undefined2 *)(puVar13 + -0x17) = uVar4;
    *(undefined8 *)((long)puVar13 + -0xa4) = uVar12;
    *(undefined8 *)((long)puVar13 + -0x9c) = uVar7;
    *(undefined8 *)((long)puVar13 + -0x94) = *(undefined8 *)((long)param_2 + 0xcc);
    uVar12 = param_2[0x1c];
    puVar13[-0x11] = param_2[0x1b];
    puVar13[-0x10] = uVar12;
    uVar12 = param_2[0x1e];
    puVar13[-0xf] = param_2[0x1d];
    puVar13[-0xe] = uVar12;
    puVar13[-0xd] = param_2[0x1f];
    uVar12 = param_2[0x21];
    uVar5 = *(undefined4 *)(param_2 + 0x24);
    uVar7 = param_2[0x25];
    uVar8 = param_2[0x26];
    local_58 = puVar13[-7];
    uStack_50 = puVar13[-6];
    puVar13[-0xc] = param_2[0x20];
    puVar13[-0xb] = uVar12;
    uVar9 = param_2[0x22];
    uVar10 = param_2[0x23];
    *(undefined4 *)(puVar13 + -8) = uVar5;
    uVar3 = *(undefined *)((long)param_2 + 0x124);
    puVar13[-7] = uVar7;
    puVar13[-6] = uVar8;
    uVar12 = param_2[0x27];
    *(undefined *)((long)puVar13 + -0x3c) = uVar3;
    local_48 = puVar13[-5];
    puVar13[-10] = uVar9;
    puVar13[-9] = uVar10;
    puVar13[-5] = uVar12;
    param_2[0x27] = 0;
    *(undefined (*) [16])(param_2 + 0x25) = (undefined  [16])0x0;
    FUN_0001cf40(&local_58);
    lVar14 = puVar13[-4];
    uVar12 = param_2[0x29];
    lVar15 = puVar13[-2];
    puVar13[-4] = param_2[0x28];
    puVar13[-3] = uVar12;
    puVar13[-2] = param_2[0x2a];
    param_2[0x2a] = 0;
    *(undefined (*) [16])(param_2 + 0x28) = (undefined  [16])0x0;
    if (lVar14 != 0) {
      thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
    }
    puVar13[-1] = param_2[0x2b];
    if (param_1 == param_2) {
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        puVar11 = puVar11 + 0x2c;
LAB_0003ad02:
        FUN_00038ca0(param_6,puVar11,param_3);
        return;
      }
      goto LAB_0003ad32;
    }
    param_2 = param_2 + -0x2c;
    puVar13 = param_3;
    goto LAB_0003a3e4;
  }
  uVar12 = puVar11[2];
  uVar7 = puVar11[3];
  *param_3 = *puVar11;
  uVar5 = *(undefined4 *)(puVar11 + 1);
  puVar13[-0x2a] = uVar12;
  puVar13[-0x29] = uVar7;
  *(undefined4 *)(puVar13 + -0x2b) = uVar5;
  puVar13[-0x28] = puVar11[4];
  puVar11[4] = 0;
  *(undefined (*) [16])(puVar11 + 2) = (undefined  [16])0x0;
  if (lVar14 != 0) {
    thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
  }
  uVar12 = puVar11[6];
  puVar13[-0x27] = puVar11[5];
  puVar13[-0x26] = uVar12;
  uVar8 = puVar11[8];
  uVar12 = *(undefined8 *)((long)puVar11 + 0xac);
  uVar7 = *(undefined8 *)((long)puVar11 + 0xb4);
  puVar13[-0x25] = puVar11[7];
  puVar13[-0x24] = uVar8;
  uVar8 = puVar11[10];
  puVar13[-0x23] = puVar11[9];
  puVar13[-0x22] = uVar8;
  uVar8 = puVar11[0xc];
  puVar13[-0x21] = puVar11[0xb];
  puVar13[-0x20] = uVar8;
  uVar8 = puVar11[0xe];
  puVar13[-0x1f] = puVar11[0xd];
  puVar13[-0x1e] = uVar8;
  uVar8 = puVar11[0x10];
  puVar13[-0x1d] = puVar11[0xf];
  puVar13[-0x1c] = uVar8;
  uVar8 = puVar11[0x12];
  puVar13[-0x1b] = puVar11[0x11];
  puVar13[-0x1a] = uVar8;
  puVar13[-0x19] = puVar11[0x13];
  puVar13[-0x18] = puVar11[0x14];
  uVar4 = *(undefined2 *)(puVar11 + 0x15);
  *(undefined8 *)((long)puVar13 + -0xb4) = uVar12;
  *(undefined8 *)((long)puVar13 + -0xac) = uVar7;
  uVar12 = *(undefined8 *)((long)puVar11 + 0xbc);
  uVar7 = *(undefined8 *)((long)puVar11 + 0xc4);
  *(undefined2 *)(puVar13 + -0x17) = uVar4;
  *(undefined8 *)((long)puVar13 + -0xa4) = uVar12;
  *(undefined8 *)((long)puVar13 + -0x9c) = uVar7;
  *(undefined8 *)((long)puVar13 + -0x94) = *(undefined8 *)((long)puVar11 + 0xcc);
  uVar12 = puVar11[0x1c];
  puVar13[-0x11] = puVar11[0x1b];
  puVar13[-0x10] = uVar12;
  uVar12 = puVar11[0x1e];
  puVar13[-0xf] = puVar11[0x1d];
  puVar13[-0xe] = uVar12;
  puVar13[-0xd] = puVar11[0x1f];
  uVar12 = puVar11[0x21];
  uVar5 = *(undefined4 *)(puVar11 + 0x24);
  local_58 = puVar13[-7];
  uStack_50 = puVar13[-6];
  uVar7 = puVar11[0x25];
  uVar8 = puVar11[0x26];
  puVar13[-0xc] = puVar11[0x20];
  puVar13[-0xb] = uVar12;
  uVar9 = puVar11[0x22];
  uVar10 = puVar11[0x23];
  *(undefined4 *)(puVar13 + -8) = uVar5;
  uVar3 = *(undefined *)((long)puVar11 + 0x124);
  puVar13[-7] = uVar7;
  puVar13[-6] = uVar8;
  uVar12 = puVar11[0x27];
  *(undefined *)((long)puVar13 + -0x3c) = uVar3;
  local_48 = puVar13[-5];
  puVar13[-10] = uVar9;
  puVar13[-9] = uVar10;
  puVar13[-5] = uVar12;
  puVar11[0x27] = 0;
  *(undefined (*) [16])(puVar11 + 0x25) = (undefined  [16])0x0;
  FUN_0001cf40(&local_58);
  lVar14 = puVar13[-4];
  uVar12 = puVar11[0x29];
  lVar15 = puVar13[-2];
  puVar13[-4] = puVar11[0x28];
  puVar13[-3] = uVar12;
  puVar13[-2] = puVar11[0x2a];
  puVar11[0x2a] = 0;
  *(undefined (*) [16])(puVar11 + 0x28) = (undefined  [16])0x0;
  if (lVar14 != 0) {
    thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
  }
  puVar13[-1] = puVar11[0x2b];
  if (param_6 == puVar11) goto LAB_0003a8e8;
  puVar11 = puVar11 + -0x2c;
  puVar13 = param_3;
  goto LAB_0003a3e4;
LAB_0003a651:
  do {
    if (param_3 == param_2) {
      if (puVar11 != param_6) {
        if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
          FUN_00038fc0(param_6,puVar11,param_1);
          return;
        }
        goto LAB_0003ad32;
      }
      break;
    }
    dVar2 = (double)param_2[0x2b];
    pdVar1 = (double *)(param_6 + 0x2b);
    if (NAN(dVar2) || NAN(*pdVar1)) {
LAB_0003a67c:
      uVar12 = param_6[2];
      uVar7 = param_6[3];
      lVar14 = param_1[2];
      lVar15 = param_1[4];
      *param_1 = *param_6;
      uVar5 = *(undefined4 *)(param_6 + 1);
      param_1[2] = uVar12;
      param_1[3] = uVar7;
      *(undefined4 *)(param_1 + 1) = uVar5;
      param_1[4] = param_6[4];
      param_6[4] = 0;
      *(undefined (*) [16])(param_6 + 2) = (undefined  [16])0x0;
      if (lVar14 != 0) {
        thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
      }
      uVar12 = param_6[6];
      param_1[5] = param_6[5];
      param_1[6] = uVar12;
      uVar8 = param_6[8];
      uVar12 = *(undefined8 *)((long)param_6 + 0xac);
      uVar7 = *(undefined8 *)((long)param_6 + 0xb4);
      param_1[7] = param_6[7];
      param_1[8] = uVar8;
      uVar8 = param_6[10];
      param_1[9] = param_6[9];
      param_1[10] = uVar8;
      uVar8 = param_6[0xc];
      param_1[0xb] = param_6[0xb];
      param_1[0xc] = uVar8;
      uVar8 = param_6[0xe];
      param_1[0xd] = param_6[0xd];
      param_1[0xe] = uVar8;
      uVar8 = param_6[0x10];
      param_1[0xf] = param_6[0xf];
      param_1[0x10] = uVar8;
      uVar8 = param_6[0x12];
      param_1[0x11] = param_6[0x11];
      param_1[0x12] = uVar8;
      param_1[0x13] = param_6[0x13];
      param_1[0x14] = param_6[0x14];
      uVar4 = *(undefined2 *)(param_6 + 0x15);
      *(undefined8 *)((long)param_1 + 0xac) = uVar12;
      *(undefined8 *)((long)param_1 + 0xb4) = uVar7;
      uVar12 = *(undefined8 *)((long)param_6 + 0xbc);
      uVar7 = *(undefined8 *)((long)param_6 + 0xc4);
      *(undefined2 *)(param_1 + 0x15) = uVar4;
      *(undefined8 *)((long)param_1 + 0xbc) = uVar12;
      *(undefined8 *)((long)param_1 + 0xc4) = uVar7;
      *(undefined8 *)((long)param_1 + 0xcc) = *(undefined8 *)((long)param_6 + 0xcc);
      uVar12 = param_6[0x1c];
      param_1[0x1b] = param_6[0x1b];
      param_1[0x1c] = uVar12;
      uVar12 = param_6[0x1e];
      param_1[0x1d] = param_6[0x1d];
      param_1[0x1e] = uVar12;
      param_1[0x1f] = param_6[0x1f];
      uVar12 = param_6[0x21];
      uVar5 = *(undefined4 *)(param_6 + 0x24);
      uVar7 = param_6[0x25];
      uVar8 = param_6[0x26];
      local_58 = param_1[0x25];
      uStack_50 = param_1[0x26];
      param_1[0x20] = param_6[0x20];
      param_1[0x21] = uVar12;
      uVar9 = param_6[0x22];
      uVar10 = param_6[0x23];
      *(undefined4 *)(param_1 + 0x24) = uVar5;
      uVar3 = *(undefined *)((long)param_6 + 0x124);
      param_1[0x25] = uVar7;
      param_1[0x26] = uVar8;
      uVar12 = param_6[0x27];
      *(undefined *)((long)param_1 + 0x124) = uVar3;
      local_48 = param_1[0x27];
      param_1[0x22] = uVar9;
      param_1[0x23] = uVar10;
      param_1[0x27] = uVar12;
      param_6[0x27] = 0;
      *(undefined (*) [16])(param_6 + 0x25) = (undefined  [16])0x0;
      FUN_0001cf40(&local_58);
      lVar14 = param_1[0x28];
      uVar12 = param_6[0x29];
      lVar15 = param_1[0x2a];
      param_1[0x28] = param_6[0x28];
      param_1[0x29] = uVar12;
      param_1[0x2a] = param_6[0x2a];
      param_6[0x2a] = 0;
      *(undefined (*) [16])(param_6 + 0x28) = (undefined  [16])0x0;
      if (lVar14 != 0) {
        thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
      }
      uVar12 = param_6[0x2b];
      param_6 = param_6 + 0x2c;
    }
    else {
      if (dVar2 == *pdVar1) {
        if (*(int *)(param_6 + 0x24) <= *(int *)(param_2 + 0x24)) goto LAB_0003a67c;
      }
      else if (dVar2 < *pdVar1 || dVar2 == *pdVar1) goto LAB_0003a67c;
      uVar12 = param_2[2];
      uVar7 = param_2[3];
      lVar14 = param_1[2];
      lVar15 = param_1[4];
      *param_1 = *param_2;
      uVar5 = *(undefined4 *)(param_2 + 1);
      param_1[2] = uVar12;
      param_1[3] = uVar7;
      *(undefined4 *)(param_1 + 1) = uVar5;
      param_1[4] = param_2[4];
      param_2[4] = 0;
      *(undefined (*) [16])(param_2 + 2) = (undefined  [16])0x0;
      if (lVar14 != 0) {
        thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
      }
      uVar12 = param_2[6];
      param_1[5] = param_2[5];
      param_1[6] = uVar12;
      uVar8 = param_2[8];
      uVar12 = *(undefined8 *)((long)param_2 + 0xac);
      uVar7 = *(undefined8 *)((long)param_2 + 0xb4);
      param_1[7] = param_2[7];
      param_1[8] = uVar8;
      uVar8 = param_2[10];
      param_1[9] = param_2[9];
      param_1[10] = uVar8;
      uVar8 = param_2[0xc];
      param_1[0xb] = param_2[0xb];
      param_1[0xc] = uVar8;
      uVar8 = param_2[0xe];
      param_1[0xd] = param_2[0xd];
      param_1[0xe] = uVar8;
      uVar8 = param_2[0x10];
      param_1[0xf] = param_2[0xf];
      param_1[0x10] = uVar8;
      uVar8 = param_2[0x12];
      param_1[0x11] = param_2[0x11];
      param_1[0x12] = uVar8;
      param_1[0x13] = param_2[0x13];
      param_1[0x14] = param_2[0x14];
      uVar4 = *(undefined2 *)(param_2 + 0x15);
      *(undefined8 *)((long)param_1 + 0xac) = uVar12;
      *(undefined8 *)((long)param_1 + 0xb4) = uVar7;
      uVar12 = *(undefined8 *)((long)param_2 + 0xbc);
      uVar7 = *(undefined8 *)((long)param_2 + 0xc4);
      *(undefined2 *)(param_1 + 0x15) = uVar4;
      *(undefined8 *)((long)param_1 + 0xbc) = uVar12;
      *(undefined8 *)((long)param_1 + 0xc4) = uVar7;
      *(undefined8 *)((long)param_1 + 0xcc) = *(undefined8 *)((long)param_2 + 0xcc);
      uVar12 = param_2[0x1c];
      param_1[0x1b] = param_2[0x1b];
      param_1[0x1c] = uVar12;
      uVar12 = param_2[0x1e];
      param_1[0x1d] = param_2[0x1d];
      param_1[0x1e] = uVar12;
      param_1[0x1f] = param_2[0x1f];
      uVar12 = param_2[0x21];
      uVar5 = *(undefined4 *)(param_2 + 0x24);
      uVar7 = param_2[0x25];
      uVar8 = param_2[0x26];
      local_58 = param_1[0x25];
      uStack_50 = param_1[0x26];
      param_1[0x20] = param_2[0x20];
      param_1[0x21] = uVar12;
      uVar9 = param_2[0x22];
      uVar10 = param_2[0x23];
      *(undefined4 *)(param_1 + 0x24) = uVar5;
      uVar3 = *(undefined *)((long)param_2 + 0x124);
      param_1[0x25] = uVar7;
      param_1[0x26] = uVar8;
      uVar12 = param_2[0x27];
      *(undefined *)((long)param_1 + 0x124) = uVar3;
      local_48 = param_1[0x27];
      param_1[0x22] = uVar9;
      param_1[0x23] = uVar10;
      param_1[0x27] = uVar12;
      param_2[0x27] = 0;
      *(undefined (*) [16])(param_2 + 0x25) = (undefined  [16])0x0;
      FUN_0001cf40(&local_58);
      lVar14 = param_1[0x28];
      uVar12 = param_2[0x29];
      lVar15 = param_1[0x2a];
      param_1[0x28] = param_2[0x28];
      param_1[0x29] = uVar12;
      param_1[0x2a] = param_2[0x2a];
      param_2[0x2a] = 0;
      *(undefined (*) [16])(param_2 + 0x28) = (undefined  [16])0x0;
      if (lVar14 != 0) {
        thunk_FUN_000d36e0(lVar14,lVar15 - lVar14);
      }
      uVar12 = param_2[0x2b];
      param_2 = param_2 + 0x2c;
    }
    param_1[0x2b] = uVar12;
    param_1 = param_1 + 0x2c;
  } while (puVar11 != param_6);
LAB_0003a8e8:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_0003ad32:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


