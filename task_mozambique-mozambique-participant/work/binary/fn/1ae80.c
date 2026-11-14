// ===== FUNC 1ae80 size=3735

void FUN_0001ae80(undefined8 *param_1,undefined8 *param_2)

{
  undefined8 *puVar1;
  double dVar2;
  undefined uVar3;
  undefined2 uVar4;
  int iVar5;
  undefined4 uVar6;
  long lVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  long lVar16;
  undefined8 uVar17;
  long *plVar18;
  long *plVar19;
  bool bVar20;
  undefined8 uVar21;
  undefined8 uVar22;
  undefined8 uVar23;
  undefined8 uVar24;
  undefined8 uVar25;
  undefined8 uVar26;
  undefined8 uVar27;
  undefined8 uVar28;
  undefined8 uVar29;
  undefined8 uVar30;
  undefined8 uVar31;
  undefined8 uVar32;
  undefined8 uVar33;
  undefined8 uVar34;
  undefined8 uVar35;
  undefined8 uVar36;
  undefined8 uVar37;
  undefined8 uVar38;
  undefined8 uVar39;
  undefined8 uVar40;
  undefined8 uVar41;
  undefined8 uVar42;
  undefined8 uVar43;
  undefined8 uVar44;
  undefined8 uVar45;
  undefined8 uVar46;
  undefined8 uVar47;
  undefined8 uVar48;
  undefined8 uVar49;
  undefined8 uVar50;
  undefined8 uVar51;
  undefined8 uVar52;
  undefined8 uVar53;
  long lVar54;
  undefined8 *puVar55;
  long lVar56;
  long *plVar57;
  long in_FS_OFFSET;
  
  lVar7 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_1 != param_2) {
    puVar55 = param_1 + 0x2c;
    while (param_2 != puVar55) {
      dVar2 = (double)puVar55[0x2b];
      iVar5 = *(int *)(puVar55 + 0x24);
      if (dVar2 == (double)param_1[0x2b]) {
        bVar20 = iVar5 < *(int *)(param_1 + 0x24);
      }
      else {
        bVar20 = (double)param_1[0x2b] < dVar2;
      }
      puVar1 = puVar55 + 0x2c;
      uVar8 = puVar55[0x2a];
      uVar26 = puVar55[0x28];
      uVar27 = puVar55[0x29];
      uVar3 = *(undefined *)((long)puVar55 + 0x124);
      uVar22 = puVar55[0x25];
      uVar23 = puVar55[0x26];
      uVar9 = puVar55[0x27];
      uVar10 = *puVar55;
      uVar6 = *(undefined4 *)(puVar55 + 1);
      uVar24 = puVar55[2];
      uVar25 = puVar55[3];
      uVar11 = puVar55[4];
      if (bVar20) {
        uVar28 = puVar55[5];
        uVar29 = puVar55[6];
        uVar12 = puVar55[0x13];
        uVar30 = puVar55[0x11];
        uVar31 = puVar55[0x12];
        uVar32 = *(undefined8 *)((long)puVar55 + 0xac);
        uVar33 = *(undefined8 *)((long)puVar55 + 0xb4);
        puVar55[4] = 0;
        uVar34 = puVar55[7];
        uVar35 = puVar55[8];
        uVar13 = puVar55[0x14];
        uVar36 = puVar55[9];
        uVar37 = puVar55[10];
        uVar4 = *(undefined2 *)(puVar55 + 0x15);
        uVar38 = puVar55[0xb];
        uVar39 = puVar55[0xc];
        uVar14 = *(undefined8 *)((long)puVar55 + 0xcc);
        uVar40 = puVar55[0xd];
        uVar41 = puVar55[0xe];
        uVar42 = puVar55[0x1b];
        uVar43 = puVar55[0x1c];
        uVar44 = puVar55[0xf];
        uVar45 = puVar55[0x10];
        uVar46 = puVar55[0x1d];
        uVar47 = puVar55[0x1e];
        uVar48 = *(undefined8 *)((long)puVar55 + 0xbc);
        uVar49 = *(undefined8 *)((long)puVar55 + 0xc4);
        *(undefined (*) [16])(puVar55 + 2) = (undefined  [16])0x0;
        uVar15 = puVar55[0x1f];
        uVar50 = puVar55[0x20];
        uVar51 = puVar55[0x21];
        uVar52 = puVar55[0x22];
        uVar53 = puVar55[0x23];
        *(undefined (*) [16])(puVar55 + 0x25) = (undefined  [16])0x0;
        *(undefined (*) [16])(puVar55 + 0x27) = (undefined  [16])0x0;
        *(undefined (*) [16])(puVar55 + 0x29) = (undefined  [16])0x0;
        lVar54 = ((long)puVar55 - (long)param_1 >> 5) * 0x2e8ba2e8ba2e8ba3;
        if (0 < (long)puVar55 - (long)param_1) {
          do {
            uVar17 = puVar55[-0x2a];
            lVar56 = puVar55[2];
            lVar16 = puVar55[4];
            *(undefined (*) [16])(puVar55 + -0x2a) = (undefined  [16])0x0;
            *puVar55 = puVar55[-0x2c];
            puVar55[2] = uVar17;
            puVar55[3] = puVar55[-0x29];
            *(undefined4 *)(puVar55 + 1) = *(undefined4 *)(puVar55 + -0x2b);
            uVar17 = puVar55[-0x28];
            puVar55[-0x28] = 0;
            puVar55[4] = uVar17;
            if (lVar56 != 0) {
              thunk_FUN_000d36e0(lVar56,lVar16 - lVar56);
            }
            puVar55[0x13] = puVar55[-0x19];
            puVar55[5] = puVar55[-0x27];
            puVar55[6] = puVar55[-0x26];
            puVar55[0x14] = puVar55[-0x18];
            puVar55[7] = puVar55[-0x25];
            puVar55[8] = puVar55[-0x24];
            *(undefined2 *)(puVar55 + 0x15) = *(undefined2 *)(puVar55 + -0x17);
            puVar55[9] = puVar55[-0x23];
            puVar55[10] = puVar55[-0x22];
            *(undefined8 *)((long)puVar55 + 0xcc) = *(undefined8 *)((long)puVar55 + -0x94);
            puVar55[0xb] = puVar55[-0x21];
            puVar55[0xc] = puVar55[-0x20];
            puVar55[0xd] = puVar55[-0x1f];
            puVar55[0xe] = puVar55[-0x1e];
            puVar55[0xf] = puVar55[-0x1d];
            puVar55[0x10] = puVar55[-0x1c];
            puVar55[0x11] = puVar55[-0x1b];
            puVar55[0x12] = puVar55[-0x1a];
            puVar55[0x1f] = puVar55[-0xd];
            *(undefined8 *)((long)puVar55 + 0xbc) = *(undefined8 *)((long)puVar55 + -0xa4);
            *(undefined8 *)((long)puVar55 + 0xc4) = *(undefined8 *)((long)puVar55 + -0x9c);
            puVar55[0x1b] = puVar55[-0x11];
            puVar55[0x1c] = puVar55[-0x10];
            *(undefined8 *)((long)puVar55 + 0xac) = *(undefined8 *)((long)puVar55 + -0xb4);
            *(undefined8 *)((long)puVar55 + 0xb4) = *(undefined8 *)((long)puVar55 + -0xac);
            puVar55[0x1d] = puVar55[-0xf];
            puVar55[0x1e] = puVar55[-0xe];
            plVar18 = (long *)puVar55[0x25];
            uVar21 = puVar55[-7];
            *(undefined (*) [16])(puVar55 + -7) = (undefined  [16])0x0;
            *(undefined4 *)(puVar55 + 0x24) = *(undefined4 *)(puVar55 + -8);
            plVar19 = (long *)puVar55[0x26];
            puVar55[0x20] = puVar55[-0xc];
            puVar55[0x21] = puVar55[-0xb];
            *(undefined *)((long)puVar55 + 0x124) = *(undefined *)((long)puVar55 + -0x3c);
            uVar17 = puVar55[-5];
            lVar56 = puVar55[0x27];
            puVar55[-5] = 0;
            puVar55[0x27] = uVar17;
            puVar55[0x22] = puVar55[-10];
            puVar55[0x23] = puVar55[-9];
            puVar55[0x25] = uVar21;
            puVar55[0x26] = puVar55[-6];
            for (plVar57 = plVar18; plVar57 != plVar19; plVar57 = plVar57 + 7) {
              if ((long *)*plVar57 != plVar57 + 2) {
                thunk_FUN_000d36e0((long *)*plVar57,plVar57[2] + 1);
              }
            }
            if (plVar18 != (long *)0x0) {
              thunk_FUN_000d36e0(plVar18,lVar56 - (long)plVar18);
            }
            uVar21 = puVar55[-4];
            uVar17 = puVar55[-2];
            puVar55[-2] = 0;
            lVar56 = puVar55[0x28];
            lVar16 = puVar55[0x2a];
            *(undefined (*) [16])(puVar55 + -4) = (undefined  [16])0x0;
            puVar55[0x2a] = uVar17;
            puVar55[0x28] = uVar21;
            puVar55[0x29] = puVar55[-3];
            if (lVar56 != 0) {
              thunk_FUN_000d36e0(lVar56,lVar16 - lVar56);
            }
            puVar55[0x2b] = puVar55[-1];
            lVar54 = lVar54 + -1;
            puVar55 = puVar55 + -0x2c;
          } while (lVar54 != 0);
        }
        lVar54 = param_1[2];
        lVar56 = param_1[4];
        *param_1 = uVar10;
        *(undefined4 *)(param_1 + 1) = uVar6;
        param_1[4] = uVar11;
        param_1[2] = uVar24;
        param_1[3] = uVar25;
        if (lVar54 != 0) {
          thunk_FUN_000d36e0(lVar54,lVar56 - lVar54);
        }
        param_1[5] = uVar28;
        param_1[6] = uVar29;
        param_1[0x13] = uVar12;
        param_1[7] = uVar34;
        param_1[8] = uVar35;
        param_1[0x14] = uVar13;
        param_1[9] = uVar36;
        param_1[10] = uVar37;
        *(undefined2 *)(param_1 + 0x15) = uVar4;
        param_1[0xb] = uVar38;
        param_1[0xc] = uVar39;
        *(undefined8 *)((long)param_1 + 0xcc) = uVar14;
        param_1[0xd] = uVar40;
        param_1[0xe] = uVar41;
        param_1[0x1b] = uVar42;
        param_1[0x1c] = uVar43;
        param_1[0xf] = uVar44;
        param_1[0x10] = uVar45;
        param_1[0x11] = uVar30;
        param_1[0x12] = uVar31;
        *(undefined8 *)((long)param_1 + 0xac) = uVar32;
        *(undefined8 *)((long)param_1 + 0xb4) = uVar33;
        *(undefined8 *)((long)param_1 + 0xbc) = uVar48;
        *(undefined8 *)((long)param_1 + 0xc4) = uVar49;
        param_1[0x1d] = uVar46;
        param_1[0x1e] = uVar47;
        param_1[0x1f] = uVar15;
        plVar18 = (long *)param_1[0x25];
        param_1[0x20] = uVar50;
        param_1[0x21] = uVar51;
        plVar19 = (long *)param_1[0x26];
        param_1[0x22] = uVar52;
        param_1[0x23] = uVar53;
        *(undefined *)((long)param_1 + 0x124) = uVar3;
        *(int *)(param_1 + 0x24) = iVar5;
        lVar54 = param_1[0x27];
        param_1[0x25] = uVar22;
        param_1[0x26] = uVar23;
        param_1[0x27] = uVar9;
        for (plVar57 = plVar18; plVar57 != plVar19; plVar57 = plVar57 + 7) {
          if ((long *)*plVar57 != plVar57 + 2) {
            thunk_FUN_000d36e0((long *)*plVar57,plVar57[2] + 1);
          }
        }
        if (plVar18 != (long *)0x0) {
          thunk_FUN_000d36e0(plVar18,lVar54 - (long)plVar18);
        }
        lVar54 = param_1[0x28];
        lVar56 = param_1[0x2a];
        param_1[0x28] = uVar26;
        param_1[0x29] = uVar27;
        param_1[0x2a] = uVar8;
        if (lVar54 != 0) {
          thunk_FUN_000d36e0(lVar54,lVar56 - lVar54);
        }
        param_1[0x2b] = dVar2;
        puVar55 = puVar1;
      }
      else {
        uVar12 = puVar55[0x13];
        uVar28 = puVar55[5];
        uVar29 = puVar55[6];
        puVar55[4] = 0;
        uVar30 = puVar55[7];
        uVar31 = puVar55[8];
        *(undefined (*) [16])(puVar55 + 2) = (undefined  [16])0x0;
        lVar56 = 0;
        lVar54 = 0;
        uVar32 = puVar55[9];
        uVar33 = puVar55[10];
        uVar13 = puVar55[0x14];
        uVar34 = puVar55[0xb];
        uVar35 = puVar55[0xc];
        uVar36 = puVar55[0xd];
        uVar37 = puVar55[0xe];
        uVar38 = puVar55[0xf];
        uVar39 = puVar55[0x10];
        uVar4 = *(undefined2 *)(puVar55 + 0x15);
        uVar40 = puVar55[0x11];
        uVar41 = puVar55[0x12];
        uVar14 = *(undefined8 *)((long)puVar55 + 0xcc);
        uVar42 = *(undefined8 *)((long)puVar55 + 0xac);
        uVar43 = *(undefined8 *)((long)puVar55 + 0xb4);
        uVar44 = *(undefined8 *)((long)puVar55 + 0xbc);
        uVar45 = *(undefined8 *)((long)puVar55 + 0xc4);
        uVar46 = puVar55[0x1b];
        uVar47 = puVar55[0x1c];
        uVar48 = puVar55[0x1d];
        uVar49 = puVar55[0x1e];
        uVar15 = puVar55[0x1f];
        uVar50 = puVar55[0x20];
        uVar51 = puVar55[0x21];
        uVar52 = puVar55[0x22];
        uVar53 = puVar55[0x23];
        *(undefined (*) [16])(puVar55 + 0x25) = (undefined  [16])0x0;
        *(undefined (*) [16])(puVar55 + 0x27) = (undefined  [16])0x0;
        *(undefined (*) [16])(puVar55 + 0x29) = (undefined  [16])0x0;
        while( true ) {
          if (dVar2 == (double)puVar55[-1]) {
            bVar20 = iVar5 < *(int *)(puVar55 + -8);
          }
          else {
            bVar20 = (double)puVar55[-1] < dVar2;
          }
          if (!bVar20) break;
          uVar17 = puVar55[-0x2a];
          *(undefined (*) [16])(puVar55 + -0x2a) = (undefined  [16])0x0;
          *puVar55 = puVar55[-0x2c];
          puVar55[2] = uVar17;
          puVar55[3] = puVar55[-0x29];
          *(undefined4 *)(puVar55 + 1) = *(undefined4 *)(puVar55 + -0x2b);
          uVar17 = puVar55[-0x28];
          puVar55[-0x28] = 0;
          puVar55[4] = uVar17;
          if (lVar54 != 0) {
            thunk_FUN_000d36e0(lVar54,lVar56 - lVar54);
          }
          puVar55[0x13] = puVar55[-0x19];
          puVar55[5] = puVar55[-0x27];
          puVar55[6] = puVar55[-0x26];
          puVar55[0x14] = puVar55[-0x18];
          puVar55[7] = puVar55[-0x25];
          puVar55[8] = puVar55[-0x24];
          *(undefined2 *)(puVar55 + 0x15) = *(undefined2 *)(puVar55 + -0x17);
          puVar55[9] = puVar55[-0x23];
          puVar55[10] = puVar55[-0x22];
          *(undefined8 *)((long)puVar55 + 0xcc) = *(undefined8 *)((long)puVar55 + -0x94);
          puVar55[0xb] = puVar55[-0x21];
          puVar55[0xc] = puVar55[-0x20];
          puVar55[0xd] = puVar55[-0x1f];
          puVar55[0xe] = puVar55[-0x1e];
          puVar55[0xf] = puVar55[-0x1d];
          puVar55[0x10] = puVar55[-0x1c];
          puVar55[0x1f] = puVar55[-0xd];
          *(undefined8 *)((long)puVar55 + 0xac) = *(undefined8 *)((long)puVar55 + -0xb4);
          *(undefined8 *)((long)puVar55 + 0xb4) = *(undefined8 *)((long)puVar55 + -0xac);
          *(undefined8 *)((long)puVar55 + 0xbc) = *(undefined8 *)((long)puVar55 + -0xa4);
          *(undefined8 *)((long)puVar55 + 0xc4) = *(undefined8 *)((long)puVar55 + -0x9c);
          puVar55[0x1b] = puVar55[-0x11];
          puVar55[0x1c] = puVar55[-0x10];
          puVar55[0x11] = puVar55[-0x1b];
          puVar55[0x12] = puVar55[-0x1a];
          puVar55[0x1d] = puVar55[-0xf];
          puVar55[0x1e] = puVar55[-0xe];
          plVar18 = (long *)puVar55[0x25];
          uVar17 = puVar55[-7];
          *(undefined (*) [16])(puVar55 + -7) = (undefined  [16])0x0;
          *(undefined4 *)(puVar55 + 0x24) = *(undefined4 *)(puVar55 + -8);
          plVar19 = (long *)puVar55[0x26];
          puVar55[0x20] = puVar55[-0xc];
          puVar55[0x21] = puVar55[-0xb];
          *(undefined *)((long)puVar55 + 0x124) = *(undefined *)((long)puVar55 + -0x3c);
          lVar54 = puVar55[0x27];
          puVar55[0x22] = puVar55[-10];
          puVar55[0x23] = puVar55[-9];
          puVar55[0x25] = uVar17;
          puVar55[0x26] = puVar55[-6];
          puVar55[0x27] = puVar55[-5];
          puVar55[-5] = 0;
          for (plVar57 = plVar18; plVar57 != plVar19; plVar57 = plVar57 + 7) {
            if ((long *)*plVar57 != plVar57 + 2) {
              thunk_FUN_000d36e0((long *)*plVar57,plVar57[2] + 1);
            }
          }
          if (plVar18 != (long *)0x0) {
            thunk_FUN_000d36e0(plVar18,lVar54 - (long)plVar18);
          }
          uVar21 = puVar55[-4];
          uVar17 = puVar55[-2];
          puVar55[-2] = 0;
          lVar54 = puVar55[0x28];
          lVar56 = puVar55[0x2a];
          *(undefined (*) [16])(puVar55 + -4) = (undefined  [16])0x0;
          puVar55[0x2a] = uVar17;
          puVar55[0x28] = uVar21;
          puVar55[0x29] = puVar55[-3];
          if (lVar54 != 0) {
            thunk_FUN_000d36e0(lVar54,lVar56 - lVar54);
          }
          lVar54 = puVar55[-0x2a];
          lVar56 = puVar55[-0x28];
          puVar55[0x2b] = puVar55[-1];
          puVar55 = puVar55 + -0x2c;
        }
        *puVar55 = uVar10;
        *(undefined4 *)(puVar55 + 1) = uVar6;
        puVar55[4] = uVar11;
        puVar55[2] = uVar24;
        puVar55[3] = uVar25;
        if (lVar54 != 0) {
          thunk_FUN_000d36e0(lVar54,lVar56 - lVar54);
        }
        puVar55[0x13] = uVar12;
        puVar55[5] = uVar28;
        puVar55[6] = uVar29;
        puVar55[7] = uVar30;
        puVar55[8] = uVar31;
        puVar55[0x14] = uVar13;
        puVar55[9] = uVar32;
        puVar55[10] = uVar33;
        *(undefined2 *)(puVar55 + 0x15) = uVar4;
        puVar55[0xb] = uVar34;
        puVar55[0xc] = uVar35;
        *(undefined8 *)((long)puVar55 + 0xcc) = uVar14;
        puVar55[0xd] = uVar36;
        puVar55[0xe] = uVar37;
        puVar55[0xf] = uVar38;
        puVar55[0x10] = uVar39;
        puVar55[0x1f] = uVar15;
        *(undefined8 *)((long)puVar55 + 0xac) = uVar42;
        *(undefined8 *)((long)puVar55 + 0xb4) = uVar43;
        puVar55[0x11] = uVar40;
        puVar55[0x12] = uVar41;
        *(undefined8 *)((long)puVar55 + 0xbc) = uVar44;
        *(undefined8 *)((long)puVar55 + 0xc4) = uVar45;
        puVar55[0x1b] = uVar46;
        puVar55[0x1c] = uVar47;
        puVar55[0x1d] = uVar48;
        puVar55[0x1e] = uVar49;
        plVar18 = (long *)puVar55[0x25];
        plVar19 = (long *)puVar55[0x26];
        *(undefined *)((long)puVar55 + 0x124) = uVar3;
        *(int *)(puVar55 + 0x24) = iVar5;
        lVar54 = puVar55[0x27];
        puVar55[0x20] = uVar50;
        puVar55[0x21] = uVar51;
        puVar55[0x27] = uVar9;
        puVar55[0x22] = uVar52;
        puVar55[0x23] = uVar53;
        puVar55[0x25] = uVar22;
        puVar55[0x26] = uVar23;
        for (plVar57 = plVar18; plVar57 != plVar19; plVar57 = plVar57 + 7) {
          if ((long *)*plVar57 != plVar57 + 2) {
            thunk_FUN_000d36e0((long *)*plVar57,plVar57[2] + 1);
          }
        }
        if (plVar18 != (long *)0x0) {
          thunk_FUN_000d36e0(plVar18,lVar54 - (long)plVar18);
        }
        lVar54 = puVar55[0x28];
        lVar56 = puVar55[0x2a];
        puVar55[0x28] = uVar26;
        puVar55[0x29] = uVar27;
        puVar55[0x2a] = uVar8;
        if (lVar54 != 0) {
          thunk_FUN_000d36e0(lVar54,lVar56 - lVar54);
        }
        puVar55[0x2b] = dVar2;
        puVar55 = puVar1;
      }
    }
  }
  if (lVar7 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


