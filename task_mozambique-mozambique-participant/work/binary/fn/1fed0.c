// ===== FUNC 1fed0 size=1203

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0001fed0(int *param_1,int param_2,ulong param_3,int param_4)

{
  int iVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  ulong uVar6;
  int *piVar7;
  int *piVar8;
  ulong uVar9;
  long lVar10;
  ulong uVar11;
  undefined8 *puVar12;
  long in_FS_OFFSET;
  byte bVar13;
  undefined8 local_5f8;
  undefined8 uStack_5f0;
  undefined8 local_5e8;
  undefined8 uStack_5e0;
  ulong local_5d8;
  undefined8 uStack_5d0;
  undefined8 local_5c8;
  undefined8 uStack_5c0;
  int local_5b8;
  undefined8 local_5b4;
  undefined8 uStack_5ac;
  long local_30;
  
  uStack_5ac = _UNK_000e2e58;
  local_5b4 = _DAT_000e2e50;
  bVar13 = 0;
  uVar9 = 5;
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  *param_1 = param_2;
  local_5b8 = 0;
  uVar11 = param_3 ^ 0x5354594c45534554;
  do {
    uVar11 = uVar11 + 0x9e3779b97f4a7c15;
    uVar6 = (uVar11 >> 0x1e ^ uVar11) * -0x40a7b892e31b1a47;
    uVar6 = (uVar6 >> 0x1b ^ uVar6) * -0x6b2fb644ecceee15;
    uVar6 = (uVar6 >> 0x1f ^ uVar6) % uVar9;
    iVar1 = *(int *)((long)&uStack_5c0 + uVar9 * 4 + 4);
    *(int *)((long)&uStack_5c0 + uVar9 * 4 + 4) = (&local_5b8)[uVar6];
    uVar9 = uVar9 - 1;
    (&local_5b8)[uVar6] = iVar1;
  } while (uVar9 != 1);
  uStack_5d0 = 0;
  param_1[1] = (&local_5b8)[param_4];
  local_5d8 = param_3 ^ 0x43414d504149474e;
  FUN_0001e1b0(&local_5b8,param_2 / 2,&local_5d8);
  FUN_0001cb80(param_1 + 2,&local_5b8,2);
  uVar5 = _UNK_000e2e68;
  uVar3 = _DAT_000e2e60;
  uVar2 = DAT_000e2e10;
  uVar11 = (ulong)param_1[1];
  iVar1 = (int)param_1;
  param_1[0x1f2] = 0;
  param_1[499] = 0;
  *(undefined8 *)(param_1 + 0x1e8) = uVar2;
  *(undefined8 *)(param_1 + 0x1e4) = uVar3;
  *(undefined8 *)(param_1 + 0x1e6) = uVar5;
  *(undefined (*) [16])(param_1 + 0x1ea) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x1ee) = (undefined  [16])0x0;
  uVar3 = DAT_000e2e78;
  uVar2 = _DAT_000e2e70;
  param_1[500] = 0;
  param_1[0x1f5] = 0;
  param_1[0x1f6] = 0;
  param_1[0x1f7] = 0;
  param_1[600] = 0;
  param_1[0x259] = 0;
  puVar12 = (undefined8 *)((ulong)(param_1 + 0x1f8) & 0xfffffffffffffff8);
  for (uVar9 = (ulong)((iVar1 - (int)(undefined8 *)((ulong)(param_1 + 0x1f8) & 0xfffffffffffffff8))
                       + 0x968U >> 3); uVar9 != 0; uVar9 = uVar9 - 1) {
    *puVar12 = 0;
    puVar12 = puVar12 + (ulong)bVar13 * -2 + 1;
  }
  param_1[0x25a] = 0;
  param_1[0x25b] = 0;
  param_1[700] = 0;
  param_1[0x2bd] = 0;
  puVar12 = (undefined8 *)((ulong)(param_1 + 0x25c) & 0xfffffffffffffff8);
  for (uVar9 = (ulong)((iVar1 - (int)(undefined8 *)((ulong)(param_1 + 0x25c) & 0xfffffffffffffff8))
                       + 0xaf8U >> 3); uVar9 != 0; uVar9 = uVar9 - 1) {
    *puVar12 = 0;
    puVar12 = puVar12 + (ulong)bVar13 * -2 + 1;
  }
  param_1[0x2be] = 0;
  param_1[0x2bf] = 0;
  param_1[800] = 0;
  param_1[0x321] = 0;
  puVar12 = (undefined8 *)((ulong)(param_1 + 0x2c0) & 0xfffffffffffffff8);
  for (uVar9 = (ulong)((iVar1 - (int)(undefined8 *)((ulong)(param_1 + 0x2c0) & 0xfffffffffffffff8))
                       + 0xc88U >> 3); uVar9 != 0; uVar9 = uVar9 - 1) {
    *puVar12 = 0;
    puVar12 = puVar12 + (ulong)bVar13 * -2 + 1;
  }
  *(undefined8 *)(param_1 + 0x322) = uVar2;
  *(undefined8 *)(param_1 + 0x324) = uVar3;
  param_1[0x326] = 0x18;
  piVar7 = param_1 + 0x327;
  do {
    piVar7[4] = 0x18;
    piVar8 = piVar7 + 5;
    *(undefined8 *)piVar7 = uVar2;
    *(undefined8 *)(piVar7 + 2) = uVar3;
    piVar7 = piVar8;
  } while (param_1 + 0x34a != piVar8);
  param_1[0x34a] = 0;
  param_1[0x34b] = 0;
  param_1[0x34c] = 0;
  param_1[0x352] = 0;
  param_1[0x353] = 0;
  *(undefined (*) [16])(param_1 + 0x34e) = (undefined  [16])0x0;
  piVar7 = param_1 + 0x354;
  for (lVar10 = 0xf; lVar10 != 0; lVar10 = lVar10 + -1) {
    piVar7[0] = 0;
    piVar7[1] = 0;
    piVar7 = piVar7 + (ulong)bVar13 * -4 + 2;
  }
  *(undefined *)(param_1 + 0x393) = 1;
  *(undefined2 *)(param_1 + 0x374) = 0;
  uVar2 = DAT_000e2e18;
  param_1[0x372] = 0;
  param_1[0x373] = 0;
  param_1[0x37d] = 0;
  param_1[0x37e] = 0;
  param_1[0x388] = 0;
  param_1[0x389] = 0;
  param_1[0x392] = 0;
  param_1[0x398] = 0;
  param_1[0x399] = 0;
  *(undefined8 *)(param_1 + 0x39a) = uVar2;
  param_1[0x3a4] = 0;
  param_1[0x3a5] = 0;
  param_1[0x3a6] = 0;
  param_1[0x3a7] = 0;
  param_1[0x3a8] = 0;
  param_1[0x3a9] = 0;
  *(undefined (*) [16])(param_1 + 0x375) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x379) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x380) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 900) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x38a) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x38e) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x394) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x39c) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x3a0) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x3aa) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x3ae) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x3b2) = (undefined  [16])0x0;
  *(undefined (*) [16])(param_1 + 0x3b6) = (undefined  [16])0x0;
                    /* try { // try from 00020228 to 0002022c has its CatchHandler @ 00020383 */
  FUN_0001fd50(param_1 + 0x3a6,0);
  param_1[0x3be] = 0;
  param_1[0x3bf] = 0;
  param_1[0x39b] = -1;
  *(undefined (*) [16])(param_1 + 0x3ba) = (undefined  [16])0x0;
  uVar2 = DAT_000e2dc8;
  for (piVar7 = param_1 + 0x39c; piVar7 != param_1 + 0x3a6; piVar7 = piVar7 + 2) {
    *(undefined8 *)piVar7 = uVar2;
  }
  uVar9 = *(ulong *)(param_1 + 0x3aa);
  uVar2 = *(undefined8 *)(param_1 + 0x3ac);
  uVar3 = *(undefined8 *)(param_1 + 0x3ae);
  puVar12 = *(undefined8 **)(param_1 + 0x3b0);
  local_5f8 = *(undefined8 *)(param_1 + 0x3b2);
  uStack_5f0 = *(undefined8 *)(param_1 + 0x3b4);
  local_5e8 = *(undefined8 *)(param_1 + 0x3b6);
  uStack_5e0 = *(undefined8 *)(param_1 + 0x3b8);
  local_5d8 = uVar9;
  uStack_5d0 = uVar2;
  local_5c8 = uVar3;
  uStack_5c0 = puVar12;
  FUN_000181d0(&local_5d8,&local_5f8);
  lVar10 = *(long *)(param_1 + 0x3b8);
  puVar4 = puVar12;
  while (puVar4 = puVar4 + 1, puVar4 < (undefined8 *)(lVar10 + 8U)) {
    thunk_FUN_000d36e0(*puVar4,0x1f8);
  }
  *(ulong *)(param_1 + 0x3b2) = uVar9;
  *(undefined8 *)(param_1 + 0x3b4) = uVar2;
  *(undefined8 *)(param_1 + 0x3b6) = uVar3;
  *(undefined8 **)(param_1 + 0x3b8) = puVar12;
  if (*(long *)(param_1 + 0x3ba) != *(long *)(param_1 + 0x3bc)) {
    *(long *)(param_1 + 0x3bc) = *(long *)(param_1 + 0x3ba);
  }
  if (4 < uVar11) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00020379 to 0002037d has its CatchHandler @ 00020388 */
    FUN_0008c960("array::at: __n (which is %zu) >= _Nm (which is %zu)",uVar11,5);
  }
  lVar10 = uVar11 * 0x18;
  uVar2 = *(undefined8 *)(&DAT_000e2820 + lVar10);
  uVar3 = *(undefined8 *)(&UNK_000e2828 + lVar10);
  param_1[0x1e8] = *(int *)(&DAT_000e2830 + lVar10);
  *(undefined8 *)(param_1 + 0x1e4) = uVar3;
  *(undefined8 *)(param_1 + 0x1e6) = uVar2;
  if (local_30 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


