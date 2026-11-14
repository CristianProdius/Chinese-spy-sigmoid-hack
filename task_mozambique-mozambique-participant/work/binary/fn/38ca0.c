// ===== FUNC 38ca0 size=785

undefined8 * FUN_00038ca0(long param_1,long param_2,undefined8 *param_3)

{
  undefined uVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  long lVar4;
  long lVar5;
  long *plVar6;
  long *plVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  long lVar11;
  long *plVar12;
  undefined8 *puVar13;
  
  param_1 = param_2 - param_1;
  lVar11 = (param_1 >> 5) * 0x2e8ba2e8ba2e8ba3;
  puVar13 = param_3;
  if (0 < param_1) {
    do {
      lVar4 = puVar13[-0x2a];
      uVar8 = *(undefined8 *)(param_2 + -0x150);
      uVar9 = *(undefined8 *)(param_2 + -0x148);
      lVar5 = puVar13[-0x28];
      puVar13[-0x2c] = *(undefined8 *)(param_2 + -0x160);
      uVar3 = *(undefined4 *)(param_2 + -0x158);
      puVar13[-0x2a] = uVar8;
      puVar13[-0x29] = uVar9;
      *(undefined4 *)(puVar13 + -0x2b) = uVar3;
      puVar13[-0x28] = *(undefined8 *)(param_2 + -0x140);
      *(undefined8 *)(param_2 + -0x140) = 0;
      *(undefined (*) [16])(param_2 + -0x150) = (undefined  [16])0x0;
      if (lVar4 != 0) {
        thunk_FUN_000d36e0(lVar4,lVar5 - lVar4);
      }
      uVar8 = *(undefined8 *)(param_2 + -0xb4);
      uVar9 = *(undefined8 *)(param_2 + -0xac);
      uVar10 = *(undefined8 *)(param_2 + -0x130);
      puVar13[-0x27] = *(undefined8 *)(param_2 + -0x138);
      puVar13[-0x26] = uVar10;
      uVar10 = *(undefined8 *)(param_2 + -0x120);
      puVar13[-0x25] = *(undefined8 *)(param_2 + -0x128);
      puVar13[-0x24] = uVar10;
      uVar10 = *(undefined8 *)(param_2 + -0x110);
      puVar13[-0x23] = *(undefined8 *)(param_2 + -0x118);
      puVar13[-0x22] = uVar10;
      uVar10 = *(undefined8 *)(param_2 + -0x100);
      puVar13[-0x21] = *(undefined8 *)(param_2 + -0x108);
      puVar13[-0x20] = uVar10;
      uVar10 = *(undefined8 *)(param_2 + -0xf0);
      puVar13[-0x1f] = *(undefined8 *)(param_2 + -0xf8);
      puVar13[-0x1e] = uVar10;
      uVar10 = *(undefined8 *)(param_2 + -0xe0);
      puVar13[-0x1d] = *(undefined8 *)(param_2 + -0xe8);
      puVar13[-0x1c] = uVar10;
      uVar10 = *(undefined8 *)(param_2 + -0xd0);
      puVar13[-0x1b] = *(undefined8 *)(param_2 + -0xd8);
      puVar13[-0x1a] = uVar10;
      puVar13[-0x19] = *(undefined8 *)(param_2 + -200);
      puVar13[-0x18] = *(undefined8 *)(param_2 + -0xc0);
      uVar2 = *(undefined2 *)(param_2 + -0xb8);
      *(undefined8 *)((long)puVar13 + -0xb4) = uVar8;
      *(undefined8 *)((long)puVar13 + -0xac) = uVar9;
      uVar8 = *(undefined8 *)(param_2 + -0xa4);
      uVar9 = *(undefined8 *)(param_2 + -0x9c);
      *(undefined2 *)(puVar13 + -0x17) = uVar2;
      *(undefined8 *)((long)puVar13 + -0xa4) = uVar8;
      *(undefined8 *)((long)puVar13 + -0x9c) = uVar9;
      *(undefined8 *)((long)puVar13 + -0x94) = *(undefined8 *)(param_2 + -0x94);
      uVar8 = *(undefined8 *)(param_2 + -0x80);
      puVar13[-0x11] = *(undefined8 *)(param_2 + -0x88);
      puVar13[-0x10] = uVar8;
      uVar8 = *(undefined8 *)(param_2 + -0x70);
      puVar13[-0xf] = *(undefined8 *)(param_2 + -0x78);
      puVar13[-0xe] = uVar8;
      puVar13[-0xd] = *(undefined8 *)(param_2 + -0x68);
      uVar10 = *(undefined8 *)(param_2 + -0x58);
      uVar8 = *(undefined8 *)(param_2 + -0x38);
      uVar9 = *(undefined8 *)(param_2 + -0x30);
      plVar6 = (long *)puVar13[-7];
      puVar13[-0xc] = *(undefined8 *)(param_2 + -0x60);
      puVar13[-0xb] = uVar10;
      plVar7 = (long *)puVar13[-6];
      uVar10 = *(undefined8 *)(param_2 + -0x48);
      puVar13[-10] = *(undefined8 *)(param_2 + -0x50);
      puVar13[-9] = uVar10;
      *(undefined4 *)(puVar13 + -8) = *(undefined4 *)(param_2 + -0x40);
      uVar1 = *(undefined *)(param_2 + -0x3c);
      puVar13[-7] = uVar8;
      puVar13[-6] = uVar9;
      *(undefined *)((long)puVar13 + -0x3c) = uVar1;
      lVar4 = puVar13[-5];
      puVar13[-5] = *(undefined8 *)(param_2 + -0x28);
      *(undefined8 *)(param_2 + -0x28) = 0;
      *(undefined (*) [16])(param_2 + -0x38) = (undefined  [16])0x0;
      for (plVar12 = plVar6; plVar12 != plVar7; plVar12 = plVar12 + 7) {
        if ((long *)*plVar12 != plVar12 + 2) {
          thunk_FUN_000d36e0((long *)*plVar12,plVar12[2] + 1);
        }
      }
      if (plVar6 != (long *)0x0) {
        thunk_FUN_000d36e0(plVar6,lVar4 - (long)plVar6);
      }
      uVar8 = *(undefined8 *)(param_2 + -0x18);
      lVar4 = puVar13[-4];
      lVar5 = puVar13[-2];
      puVar13[-4] = *(undefined8 *)(param_2 + -0x20);
      puVar13[-3] = uVar8;
      puVar13[-2] = *(undefined8 *)(param_2 + -0x10);
      *(undefined8 *)(param_2 + -0x10) = 0;
      *(undefined (*) [16])(param_2 + -0x20) = (undefined  [16])0x0;
      if (lVar4 != 0) {
        thunk_FUN_000d36e0(lVar4,lVar5 - lVar4);
      }
      puVar13[-1] = *(undefined8 *)(param_2 + -8);
      lVar11 = lVar11 + -1;
      puVar13 = puVar13 + -0x2c;
      param_2 = param_2 + -0x160;
    } while (lVar11 != 0);
    lVar11 = (param_1 >> 5) * -0x20;
    if (param_1 < 1) {
      lVar11 = -0x160;
    }
    return (undefined8 *)((long)param_3 + lVar11);
  }
  return param_3;
}


