// ===== FUNC 31ef0 size=816

undefined2 FUN_00031ef0(long param_1,long param_2)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  long *plVar3;
  long *plVar4;
  long *plVar5;
  undefined uVar6;
  uint uVar7;
  long *plVar8;
  undefined4 *puVar9;
  undefined8 uVar10;
  long lVar11;
  int *piVar12;
  int iVar13;
  int *piVar14;
  int *piVar15;
  int *piVar16;
  long in_FS_OFFSET;
  byte bVar17;
  long local_778;
  undefined2 local_732;
  int local_730;
  int local_72c;
  int local_728 [358];
  long local_190;
  long local_180;
  undefined local_68;
  undefined local_60 [8];
  long *local_58;
  long *plStack_50;
  long local_48;
  long local_40;
  
  bVar17 = 0;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (0x4f < *(int *)(param_1 + 0x584)) {
    uVar10 = FUN_00040f40(0x10);
                    /* try { // try from 00032213 to 00032217 has its CatchHandler @ 00032238 */
    FUN_00053220(uVar10,"campaign already finished");
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar10,&PTR_PTR_FUN_0011d470,FUN_00049930);
  }
  iVar13 = 0;
  local_778 = param_2;
  while( true ) {
    FUN_000311e0(local_728,param_1,iVar13);
    lVar11 = local_48;
    plVar5 = plStack_50;
    plVar4 = local_58;
    FUN_00024620(local_60,local_68);
    if (local_190 != 0) {
      thunk_FUN_000d36e0(local_190,local_180 - local_190);
    }
    plVar8 = (long *)FUN_00019a20(plVar4,plVar5,local_778);
    plVar3 = plVar4;
    if (plVar5 == plVar8) {
      uVar10 = FUN_00040f40(0x10);
                    /* try { // try from 000321e1 to 000321e5 has its CatchHandler @ 00032233 */
      FUN_00053220(uVar10,"illegal order");
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 000321f7 to 000321fb has its CatchHandler @ 0003222e */
      FUN_00041f00(uVar10,&PTR_PTR_FUN_0011d470,FUN_00049930);
    }
    for (; plVar3 != plVar5; plVar3 = plVar3 + 7) {
      if ((long *)*plVar3 != plVar3 + 2) {
        thunk_FUN_000d36e0((long *)*plVar3,plVar3[2] + 1);
      }
    }
    if (plVar4 != (long *)0x0) {
      thunk_FUN_000d36e0(plVar4,lVar11 - (long)plVar4);
    }
    local_778 = local_778 + 0x38;
    if (iVar13 != 0) break;
    iVar13 = 1;
  }
  piVar16 = &local_730;
  piVar14 = local_728;
  for (lVar11 = 0xc; lVar11 != 0; lVar11 = lVar11 + -1) {
    piVar14[0] = 0;
    piVar14[1] = 0;
    piVar14 = piVar14 + ((ulong)bVar17 * -2 + 1) * 2;
  }
  local_732 = 0;
  piVar15 = (int *)(param_1 + 0x740);
  local_730 = *(int *)(param_1 + 0x584) % 2;
  *piVar14 = 0;
  local_72c = 1 - local_730;
  do {
    lVar11 = (long)*piVar16;
    piVar16 = piVar16 + 1;
    uVar6 = FUN_00022090(param_1,param_1 + 0x590 + lVar11 * 0xd8,piVar15,(int *)(param_1 + 0x768),
                         lVar11,param_2 + lVar11 * 0x38,local_728);
    *(undefined *)((long)&local_732 + lVar11) = uVar6;
  } while (piVar16 != local_728);
  piVar16 = (int *)(param_1 + 0x638);
  if (piVar15 != (int *)(param_1 + 0x590)) {
    do {
      puVar2 = *(undefined4 **)(piVar16 + -0x24);
      for (puVar9 = *(undefined4 **)(piVar16 + -0x26); puVar9 != puVar2; puVar9 = puVar9 + 6) {
        if ((puVar9[2] != 0) && (iVar13 = puVar9[2] + -1, puVar9[2] = iVar13, iVar13 == 0)) {
          uVar1 = puVar9[1];
          puVar9[1] = 0xffffffff;
          *puVar9 = uVar1;
        }
      }
      piVar14 = piVar16 + -0x1e;
      piVar12 = piVar16;
      do {
        piVar12 = piVar12 + 1;
        if ((*piVar12 != 0) && (iVar13 = *piVar12 + -1, *piVar12 = iVar13, iVar13 == 0)) {
          *piVar14 = *piVar14 + 1;
        }
        piVar14 = piVar14 + 3;
      } while (piVar16 != piVar14);
      piVar16 = piVar16 + 0x36;
    } while (piVar16 != (int *)(param_1 + 0x7e8));
  }
  uVar7 = *(int *)(param_1 + 0x584) + 1;
  *(uint *)(param_1 + 0x584) = uVar7;
  if ((uVar7 & 3) == 0) {
    do {
      if ((uint)piVar15[-0x1cf] < 2) {
        *piVar15 = *piVar15 + 1;
        iVar13 = *piVar15;
        if (6 < iVar13) {
          iVar13 = 6;
        }
        *piVar15 = iVar13;
      }
      piVar15 = piVar15 + 1;
    } while ((int *)(param_1 + 0x768) != piVar15);
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return local_732;
}


