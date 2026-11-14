// ===== FUNC 25c50 size=844

undefined8 * FUN_00025c50(undefined8 *param_1,char *param_2,undefined8 *param_3)

{
  char cVar1;
  undefined uVar2;
  undefined *puVar3;
  undefined *puVar4;
  undefined8 uVar5;
  long lVar6;
  undefined8 uVar7;
  char *__s;
  size_t sVar8;
  undefined *puVar9;
  undefined *puVar10;
  long *plVar11;
  long lVar12;
  long in_FS_OFFSET;
  undefined8 uStack_70;
  undefined *local_68;
  undefined8 local_60;
  undefined local_58 [24];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if ((char *)*param_3 != param_2) {
    uVar7 = FUN_00040f40(0x20);
                    /* try { // try from 00025f97 to 00025f9b has its CatchHandler @ 00025fbc */
    FUN_00018b10(&local_68,"iterator does not fit current value");
                    /* try { // try from 00025fa7 to 00025fab has its CatchHandler @ 00025fba */
    FUN_0001394e(uVar7,0xca,&local_68);
LAB_00025ece:
    FUN_000b07c0(&local_68);
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar7,&PTR_PTR_FUN_0011cc58,FUN_0001aa80);
  }
  *param_1 = param_2;
  param_1[3] = 0x8000000000000000;
  cVar1 = *param_2;
  param_1[1] = 0;
  param_1[2] = 0;
  if (cVar1 == '\x01') {
    lVar12 = *(long *)(param_2 + 8);
    lVar6 = lVar12 + 8;
    param_1[1] = lVar6;
    uVar7 = param_3[1];
    uVar5 = FUN_00049c90(uVar7);
    lVar6 = FUN_0004a190(uVar7,lVar6);
    FUN_00024620(lVar6 + 0x48,*(undefined *)(lVar6 + 0x40));
    if (*(long *)(lVar6 + 0x20) != lVar6 + 0x30) {
      thunk_FUN_000d36e0(*(long *)(lVar6 + 0x20),*(long *)(lVar6 + 0x30) + 1);
    }
    thunk_FUN_000d36e0(lVar6,0x50);
    plVar11 = (long *)(lVar12 + 0x28);
    *plVar11 = *plVar11 + -1;
    param_1[1] = uVar5;
  }
  else if (cVar1 == '\x02') {
    lVar6 = *(long *)(param_2 + 8);
    param_1[2] = 0;
    puVar3 = *(undefined **)(lVar6 + 8);
    param_1[2] = puVar3;
    puVar4 = (undefined *)param_3[2];
    puVar9 = puVar4 + 0x10;
    puVar10 = puVar9;
    if ((puVar3 != puVar9) &&
       (lVar12 = (long)puVar3 - (long)puVar9 >> 4, puVar10 = puVar3, 0 < (long)puVar3 - (long)puVar9
       )) {
      puVar9 = puVar4;
      do {
        uVar7 = *(undefined8 *)(puVar9 + 0x18);
        uVar2 = puVar9[0x10];
        puVar9[0x10] = 0;
        *(undefined8 *)(puVar9 + 0x18) = 0;
        *puVar9 = uVar2;
        uStack_70 = *(undefined8 *)(puVar9 + 8);
        *(undefined8 *)(puVar9 + 8) = uVar7;
        FUN_00024620(&uStack_70);
        lVar12 = lVar12 + -1;
        puVar9 = puVar9 + 0x10;
      } while (lVar12 != 0);
      puVar10 = *(undefined **)(lVar6 + 8);
    }
    uVar2 = puVar10[-0x10];
    *(undefined **)(lVar6 + 8) = puVar10 + -0x10;
    FUN_00024620(puVar10 + -8,uVar2);
    param_1[2] = puVar4;
  }
  else {
    param_1[3] = 1;
    if (5 < (byte)(cVar1 - 3U)) {
      uVar7 = FUN_00040f40(0x20);
      __s = (char *)FUN_000137b8(*param_2);
      local_58[0] = 0;
      local_68 = local_58;
      local_60 = 0;
      sVar8 = strlen(__s);
                    /* try { // try from 00025f2e to 00025f4c has its CatchHandler @ 00025fb6 */
      FUN_000b1110(&local_68,sVar8 + 0x18);
      FUN_00017ba0(&local_68,"cannot use erase() with ");
      FUN_00017ba0(&local_68,__s);
                    /* try { // try from 00025f58 to 00025f5c has its CatchHandler @ 00025fb1 */
      FUN_00013ba0(uVar7,0x133,&local_68);
      FUN_000b07c0(&local_68);
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(uVar7,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
    }
    if (param_3[3] != 0) {
      uVar7 = FUN_00040f40(0x20);
                    /* try { // try from 00025eb9 to 00025ebd has its CatchHandler @ 00025fc1 */
      FUN_00018b10(&local_68,"iterator out of range");
                    /* try { // try from 00025ec9 to 00025ecd has its CatchHandler @ 00025fb8 */
      FUN_0001394e(uVar7,0xcd,&local_68);
      goto LAB_00025ece;
    }
    if (cVar1 == '\x03') {
      FUN_000b07c0(*(undefined8 *)(param_2 + 8));
      thunk_FUN_000d36e0(*(undefined8 *)(param_2 + 8),0x20);
      param_2[8] = '\0';
      param_2[9] = '\0';
      param_2[10] = '\0';
      param_2[0xb] = '\0';
      param_2[0xc] = '\0';
      param_2[0xd] = '\0';
      param_2[0xe] = '\0';
      param_2[0xf] = '\0';
    }
    else if (cVar1 == '\b') {
      plVar11 = *(long **)(param_2 + 8);
      lVar6 = *plVar11;
      if (lVar6 != 0) {
        thunk_FUN_000d36e0(lVar6,plVar11[2] - lVar6);
        plVar11 = *(long **)(param_2 + 8);
      }
      thunk_FUN_000d36e0(plVar11,0x28);
      param_2[8] = '\0';
      param_2[9] = '\0';
      param_2[10] = '\0';
      param_2[0xb] = '\0';
      param_2[0xc] = '\0';
      param_2[0xd] = '\0';
      param_2[0xe] = '\0';
      param_2[0xf] = '\0';
    }
    *param_2 = '\0';
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


