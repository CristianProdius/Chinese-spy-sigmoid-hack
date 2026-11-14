// ===== FUNC 392b0 size=1372

void FUN_000392b0(undefined8 *param_1,undefined8 *param_2,undefined8 *param_3,undefined8 *param_4,
                 undefined8 *param_5)

{
  double *pdVar1;
  double dVar2;
  undefined2 uVar3;
  undefined4 uVar4;
  long lVar5;
  long lVar6;
  long *plVar7;
  long *plVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  long *plVar14;
  
  if ((param_4 != param_3) && (param_2 != param_1)) {
    do {
      dVar2 = (double)param_3[0x2b];
      pdVar1 = (double *)(param_1 + 0x2b);
      if (NAN(dVar2) || NAN(*pdVar1)) {
LAB_000395c8:
        uVar13 = param_1[2];
        uVar9 = param_1[3];
        lVar5 = param_5[2];
        lVar6 = param_5[4];
        *param_5 = *param_1;
        uVar4 = *(undefined4 *)(param_1 + 1);
        param_5[2] = uVar13;
        param_5[3] = uVar9;
        *(undefined4 *)(param_5 + 1) = uVar4;
        param_5[4] = param_1[4];
        param_1[4] = 0;
        *(undefined (*) [16])(param_1 + 2) = (undefined  [16])0x0;
        if (lVar5 != 0) {
          thunk_FUN_000d36e0(lVar5,lVar6 - lVar5);
        }
        uVar13 = *(undefined8 *)((long)param_1 + 0xac);
        uVar9 = *(undefined8 *)((long)param_1 + 0xb4);
        uVar10 = param_1[6];
        param_5[5] = param_1[5];
        param_5[6] = uVar10;
        uVar10 = param_1[8];
        param_5[7] = param_1[7];
        param_5[8] = uVar10;
        uVar10 = param_1[10];
        param_5[9] = param_1[9];
        param_5[10] = uVar10;
        uVar10 = param_1[0xc];
        param_5[0xb] = param_1[0xb];
        param_5[0xc] = uVar10;
        uVar10 = param_1[0xe];
        param_5[0xd] = param_1[0xd];
        param_5[0xe] = uVar10;
        uVar10 = param_1[0x10];
        param_5[0xf] = param_1[0xf];
        param_5[0x10] = uVar10;
        uVar10 = param_1[0x12];
        param_5[0x11] = param_1[0x11];
        param_5[0x12] = uVar10;
        param_5[0x13] = param_1[0x13];
        param_5[0x14] = param_1[0x14];
        uVar3 = *(undefined2 *)(param_1 + 0x15);
        *(undefined8 *)((long)param_5 + 0xac) = uVar13;
        *(undefined8 *)((long)param_5 + 0xb4) = uVar9;
        uVar13 = *(undefined8 *)((long)param_1 + 0xbc);
        uVar9 = *(undefined8 *)((long)param_1 + 0xc4);
        *(undefined2 *)(param_5 + 0x15) = uVar3;
        *(undefined8 *)((long)param_5 + 0xbc) = uVar13;
        *(undefined8 *)((long)param_5 + 0xc4) = uVar9;
        *(undefined8 *)((long)param_5 + 0xcc) = *(undefined8 *)((long)param_1 + 0xcc);
        uVar13 = param_1[0x1c];
        param_5[0x1b] = param_1[0x1b];
        param_5[0x1c] = uVar13;
        uVar13 = param_1[0x1e];
        param_5[0x1d] = param_1[0x1d];
        param_5[0x1e] = uVar13;
        param_5[0x1f] = param_1[0x1f];
        uVar13 = param_1[0x21];
        uVar4 = *(undefined4 *)(param_1 + 0x24);
        lVar5 = param_5[0x27];
        uVar9 = param_1[0x25];
        uVar10 = param_1[0x26];
        param_5[0x20] = param_1[0x20];
        param_5[0x21] = uVar13;
        uVar11 = param_1[0x22];
        uVar12 = param_1[0x23];
        *(undefined4 *)(param_5 + 0x24) = uVar4;
        plVar7 = (long *)param_5[0x25];
        plVar8 = (long *)param_5[0x26];
        *(undefined *)((long)param_5 + 0x124) = *(undefined *)((long)param_1 + 0x124);
        param_5[0x25] = uVar9;
        param_5[0x26] = uVar10;
        uVar13 = param_1[0x27];
        param_5[0x22] = uVar11;
        param_5[0x23] = uVar12;
        param_5[0x27] = uVar13;
        param_1[0x27] = 0;
        *(undefined (*) [16])(param_1 + 0x25) = (undefined  [16])0x0;
        for (plVar14 = plVar7; plVar14 != plVar8; plVar14 = plVar14 + 7) {
          if ((long *)*plVar14 != plVar14 + 2) {
            thunk_FUN_000d36e0((long *)*plVar14,plVar14[2] + 1);
          }
        }
        if (plVar7 != (long *)0x0) {
          thunk_FUN_000d36e0(plVar7,lVar5 - (long)plVar7);
        }
        uVar13 = param_1[0x29];
        lVar5 = param_5[0x28];
        lVar6 = param_5[0x2a];
        param_5[0x28] = param_1[0x28];
        param_5[0x29] = uVar13;
        param_5[0x2a] = param_1[0x2a];
        param_1[0x2a] = 0;
        *(undefined (*) [16])(param_1 + 0x28) = (undefined  [16])0x0;
        if (lVar5 != 0) {
          thunk_FUN_000d36e0(lVar5,lVar6 - lVar5);
        }
        uVar13 = param_1[0x2b];
        param_1 = param_1 + 0x2c;
      }
      else {
        if (dVar2 == *pdVar1) {
          if (*(int *)(param_1 + 0x24) <= *(int *)(param_3 + 0x24)) goto LAB_000395c8;
        }
        else if (dVar2 < *pdVar1 || dVar2 == *pdVar1) goto LAB_000395c8;
        uVar13 = param_3[2];
        uVar9 = param_3[3];
        lVar5 = param_5[2];
        lVar6 = param_5[4];
        *param_5 = *param_3;
        uVar4 = *(undefined4 *)(param_3 + 1);
        param_5[2] = uVar13;
        param_5[3] = uVar9;
        *(undefined4 *)(param_5 + 1) = uVar4;
        param_5[4] = param_3[4];
        param_3[4] = 0;
        *(undefined (*) [16])(param_3 + 2) = (undefined  [16])0x0;
        if (lVar5 != 0) {
          thunk_FUN_000d36e0(lVar5,lVar6 - lVar5);
        }
        uVar13 = param_3[6];
        param_5[5] = param_3[5];
        param_5[6] = uVar13;
        uVar13 = param_3[8];
        uVar9 = *(undefined8 *)((long)param_3 + 0xac);
        uVar10 = *(undefined8 *)((long)param_3 + 0xb4);
        param_5[7] = param_3[7];
        param_5[8] = uVar13;
        uVar13 = param_3[10];
        param_5[9] = param_3[9];
        param_5[10] = uVar13;
        uVar13 = param_3[0xc];
        param_5[0xb] = param_3[0xb];
        param_5[0xc] = uVar13;
        uVar13 = param_3[0xe];
        param_5[0xd] = param_3[0xd];
        param_5[0xe] = uVar13;
        uVar13 = param_3[0x10];
        param_5[0xf] = param_3[0xf];
        param_5[0x10] = uVar13;
        uVar13 = param_3[0x12];
        param_5[0x11] = param_3[0x11];
        param_5[0x12] = uVar13;
        param_5[0x13] = param_3[0x13];
        param_5[0x14] = param_3[0x14];
        uVar3 = *(undefined2 *)(param_3 + 0x15);
        *(undefined8 *)((long)param_5 + 0xac) = uVar9;
        *(undefined8 *)((long)param_5 + 0xb4) = uVar10;
        uVar13 = *(undefined8 *)((long)param_3 + 0xbc);
        uVar9 = *(undefined8 *)((long)param_3 + 0xc4);
        *(undefined2 *)(param_5 + 0x15) = uVar3;
        *(undefined8 *)((long)param_5 + 0xbc) = uVar13;
        *(undefined8 *)((long)param_5 + 0xc4) = uVar9;
        *(undefined8 *)((long)param_5 + 0xcc) = *(undefined8 *)((long)param_3 + 0xcc);
        uVar13 = param_3[0x1c];
        param_5[0x1b] = param_3[0x1b];
        param_5[0x1c] = uVar13;
        uVar13 = param_3[0x1e];
        param_5[0x1d] = param_3[0x1d];
        param_5[0x1e] = uVar13;
        param_5[0x1f] = param_3[0x1f];
        uVar13 = param_3[0x21];
        uVar4 = *(undefined4 *)(param_3 + 0x24);
        lVar5 = param_5[0x27];
        uVar11 = param_3[0x25];
        uVar12 = param_3[0x26];
        param_5[0x20] = param_3[0x20];
        param_5[0x21] = uVar13;
        uVar9 = param_3[0x22];
        uVar10 = param_3[0x23];
        *(undefined4 *)(param_5 + 0x24) = uVar4;
        plVar7 = (long *)param_5[0x25];
        plVar8 = (long *)param_5[0x26];
        *(undefined *)((long)param_5 + 0x124) = *(undefined *)((long)param_3 + 0x124);
        param_5[0x25] = uVar11;
        param_5[0x26] = uVar12;
        uVar13 = param_3[0x27];
        param_5[0x22] = uVar9;
        param_5[0x23] = uVar10;
        param_5[0x27] = uVar13;
        param_3[0x27] = 0;
        *(undefined (*) [16])(param_3 + 0x25) = (undefined  [16])0x0;
        for (plVar14 = plVar7; plVar14 != plVar8; plVar14 = plVar14 + 7) {
          if ((long *)*plVar14 != plVar14 + 2) {
            thunk_FUN_000d36e0((long *)*plVar14,plVar14[2] + 1);
          }
        }
        if (plVar7 != (long *)0x0) {
          thunk_FUN_000d36e0(plVar7,lVar5 - (long)plVar7);
        }
        uVar13 = param_3[0x29];
        lVar5 = param_5[0x28];
        lVar6 = param_5[0x2a];
        param_5[0x28] = param_3[0x28];
        param_5[0x29] = uVar13;
        param_5[0x2a] = param_3[0x2a];
        param_3[0x2a] = 0;
        *(undefined (*) [16])(param_3 + 0x28) = (undefined  [16])0x0;
        if (lVar5 != 0) {
          thunk_FUN_000d36e0(lVar5,lVar6 - lVar5);
        }
        uVar13 = param_3[0x2b];
        param_3 = param_3 + 0x2c;
      }
      param_5[0x2b] = uVar13;
      param_5 = param_5 + 0x2c;
    } while ((param_2 != param_1) && (param_4 != param_3));
  }
  uVar13 = FUN_00038fc0(param_1,param_2,param_5);
  FUN_00038fc0(param_3,param_4,uVar13);
  return;
}


