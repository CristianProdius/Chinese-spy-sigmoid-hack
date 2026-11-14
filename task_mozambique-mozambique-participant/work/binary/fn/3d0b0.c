// ===== FUNC 3d0b0 size=1497

/* WARNING: Type propagation algorithm not settling */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0003d0b0(int *param_1,char *param_2)

{
  int *piVar1;
  ulong __n;
  undefined *__src;
  undefined8 uVar2;
  long *plVar3;
  undefined auVar4 [16];
  undefined auVar5 [16];
  char cVar6;
  int iVar7;
  undefined *__dest;
  undefined8 uVar8;
  undefined8 *puVar9;
  undefined (*pauVar10) [16];
  long lVar11;
  long in_FS_OFFSET;
  bool bVar12;
  ulong local_ea8 [2];
  long *local_e98;
  size_t local_e90;
  long local_e88 [2];
  undefined8 local_e78;
  undefined8 uStack_e70;
  undefined4 local_e68;
  undefined local_e58 [16];
  undefined local_e48 [16];
  undefined local_e38 [16];
  undefined local_e28 [16];
  undefined local_e18 [1432];
  long local_880;
  long local_870;
  undefined local_758;
  undefined local_750 [8];
  undefined8 *local_748;
  undefined8 *local_740;
  long *local_728;
  size_t sStack_720;
  long local_718 [2];
  undefined8 local_708 [2];
  undefined4 local_6f8 [2];
  long *local_6f0;
  long local_6e0 [170];
  long local_190;
  long local_180;
  undefined local_68;
  undefined local_60 [8];
  undefined local_58 [24];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if ((param_1[0x163] == 0x50) || (*param_2 != '\x01')) {
    uVar8 = FUN_00040f40(0x10);
                    /* try { // try from 0003d714 to 0003d718 has its CatchHandler @ 0003d788 */
    FUN_00053220(uVar8,"invalid action");
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar8,&PTR_PTR_FUN_0011d470,FUN_00049930);
  }
  piVar1 = param_1 + 2;
  FUN_000311e0(local_e18,piVar1,*param_1 % 2);
  local_e58 = (undefined  [16])0x0;
  local_e48 = (undefined  [16])0x0;
  local_e38 = (undefined  [16])0x0;
  local_e28 = (undefined  [16])0x0;
  puVar9 = local_748;
  if (local_748 != local_740) {
    do {
                    /* try { // try from 0003d201 to 0003d205 has its CatchHandler @ 0003d6de */
      FUN_0002e6f0((undefined (*) [16])&local_728,param_2,0xffffffff,0x20,0,0);
      local_ea8[0] = 0;
      local_ea8[1] = 0;
                    /* try { // try from 0003d21e to 0003d222 has its CatchHandler @ 0003d6f5 */
      FUN_000303d0(local_ea8,puVar9);
                    /* try { // try from 0003d23e to 0003d242 has its CatchHandler @ 0003d6e8 */
      FUN_0002e6f0(&local_e98,local_ea8,0xffffffff,0x20);
      plVar3 = local_e98;
      bVar12 = false;
      if ((local_e90 == sStack_720) && (bVar12 = true, local_e90 != 0)) {
        iVar7 = memcmp(local_e98,local_728,local_e90);
        bVar12 = iVar7 == 0;
      }
      if (plVar3 != local_e88) {
        thunk_FUN_000d36e0(plVar3,local_e88[0] + 1);
      }
      FUN_00024620(local_ea8 + 1,local_ea8[0] & 0xff);
      if (local_728 != local_718) {
        thunk_FUN_000d36e0(local_728,local_718[0] + 1);
      }
      if (bVar12) {
        if (local_e28[8] == '\0') {
          __dest = local_e48;
          __n = puVar9[1];
          __src = (undefined *)*puVar9;
          local_ea8[0] = __n;
          local_e58._0_8_ = __dest;
          if (__n < 0x10) {
            if (__n == 1) {
              local_e48[0] = *__src;
            }
            else if (__n != 0) goto LAB_0003d61e;
          }
          else {
                    /* try { // try from 0003d601 to 0003d605 has its CatchHandler @ 0003d6de */
            __dest = (undefined *)FUN_000b0760(local_e58,local_ea8,0);
            local_e48._0_8_ = local_ea8[0];
LAB_0003d61e:
            local_e58._0_8_ = __dest;
            memcpy(__dest,__src,__n);
          }
          local_e58._8_8_ = local_ea8[0];
          *(undefined *)(local_e58._0_8_ + local_ea8[0]) = 0;
          local_e38 = *(undefined (*) [16])(puVar9 + 4);
          local_e28[8] = 1;
          local_e28._0_4_ = *(undefined4 *)(puVar9 + 6);
          goto LAB_0003d2d5;
        }
                    /* try { // try from 0003d2a9 to 0003d2fb has its CatchHandler @ 0003d6de */
        FUN_000b0ad0(local_e58,puVar9);
        auVar4 = local_e28;
        local_e38 = *(undefined (*) [16])(puVar9 + 4);
        local_e28._0_4_ = *(undefined4 *)(puVar9 + 6);
        auVar5 = local_e28;
        local_e28[8] = auVar4[8];
        cVar6 = local_e28[8];
        local_e28 = auVar5;
        break;
      }
      puVar9 = puVar9 + 7;
      cVar6 = local_e28[8];
    } while (local_740 != puVar9);
    if (cVar6 != '\0') {
LAB_0003d2d5:
      iVar7 = -(*param_1 >> 0x1f);
      FUN_000311e0((undefined (*) [16])&local_728,piVar1,(iVar7 - (*param_1 + iVar7 & 1U)) + 1);
                    /* try { // try from 0003d309 to 0003d30d has its CatchHandler @ 0003d6ed */
      FUN_0003ae20(&local_e98,param_1 + 0x1e4,(undefined (*) [16])&local_728);
      FUN_0001cf40(local_58);
      FUN_00024620(local_60,local_68);
      if (local_190 != 0) {
        thunk_FUN_000d36e0(local_190,local_180 - local_190);
      }
      lVar11 = 1;
      pauVar10 = (undefined (*) [16])&local_728;
      do {
        *pauVar10 = (undefined  [16])0x0;
        *(undefined8 *)pauVar10[3] = 0;
        *(undefined (**) [16])*pauVar10 = pauVar10 + 1;
        pauVar10[1] = (undefined  [16])0x0;
        pauVar10[2] = (undefined  [16])0x0;
                    /* try { // try from 0003d385 to 0003d389 has its CatchHandler @ 0003d6e3 */
        FUN_00017bf0(pauVar10,&DAT_000e0454,&DAT_000e0458);
        uVar2 = _UNK_000e2e88;
        uVar8 = DAT_000e2e80;
        *(undefined4 *)pauVar10[3] = 0xffffffff;
        *(undefined8 *)pauVar10[2] = uVar8;
        *(undefined8 *)(pauVar10[2] + 8) = uVar2;
        bVar12 = lVar11 != 0;
        lVar11 = lVar11 + -1;
        pauVar10 = (undefined (*) [16])(pauVar10[3] + 8);
      } while (bVar12);
      lVar11 = (long)(*param_1 % 2);
                    /* try { // try from 0003d3dd to 0003d468 has its CatchHandler @ 0003d67b */
      FUN_000b0ad0((long)&local_728 + lVar11 * 0x38,local_e58);
      local_708[lVar11 * 7] = local_e38._0_8_;
      local_708[lVar11 * 7 + 1] = local_e38._8_8_;
      local_6f8[lVar11 * 0xe] = local_e28._0_4_;
      iVar7 = -(*param_1 >> 0x1f);
      lVar11 = (long)(int)((iVar7 - (*param_1 + iVar7 & 1U)) + 1);
      FUN_000b0ad0((long)&local_728 + lVar11 * 0x38,&local_e98);
      local_708[lVar11 * 7] = local_e78;
      local_708[lVar11 * 7 + 1] = uStack_e70;
      local_6f8[lVar11 * 0xe] = local_e68;
      FUN_00031ef0(piVar1,(undefined (*) [16])&local_728);
      if (local_6f0 != local_6e0) {
        thunk_FUN_000d36e0(local_6f0,local_6e0[0] + 1);
      }
      if (local_728 != local_718) {
        thunk_FUN_000d36e0(local_728,local_718[0] + 1);
      }
      if (local_e98 != local_e88) {
        thunk_FUN_000d36e0(local_e98,local_e88[0] + 1);
      }
      if (local_e28[8] != '\0') {
        local_e28[8] = 0;
        if ((undefined *)local_e58._0_8_ != local_e48) {
          thunk_FUN_000d36e0(local_e58._0_8_,local_e48._0_8_ + 1);
        }
      }
      FUN_0001cf40(&local_748);
      FUN_00024620(local_750,local_758);
      if (local_880 != 0) {
        thunk_FUN_000d36e0(local_880,local_870 - local_880);
      }
      if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
      return;
    }
  }
  uVar8 = FUN_00040f40(0x10);
                    /* try { // try from 0003d660 to 0003d664 has its CatchHandler @ 0003d680 */
  FUN_00053220(uVar8,"illegal action");
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003d676 to 0003d67a has its CatchHandler @ 0003d6de */
  FUN_00041f00(uVar8,&PTR_PTR_FUN_0011d470,FUN_00049930);
}


