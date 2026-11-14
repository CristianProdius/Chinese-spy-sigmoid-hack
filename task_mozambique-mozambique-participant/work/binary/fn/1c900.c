// ===== FUNC 1c900 size=377

void FUN_0001c900(long param_1)

{
  undefined8 *puVar1;
  undefined8 uVar2;
  long *plVar3;
  undefined8 *puVar4;
  long *plVar5;
  long lVar6;
  long in_FS_OFFSET;
  undefined8 local_68;
  undefined8 uStack_60;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  undefined8 uStack_40;
  undefined8 local_38;
  undefined8 uStack_30;
  long local_20;
  
  lVar6 = *(long *)(param_1 + 0x758);
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  if (lVar6 != 0) {
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0x768) - lVar6);
  }
  local_68 = *(undefined8 *)(param_1 + 0x738);
  uStack_60 = *(undefined8 *)(param_1 + 0x740);
  local_58 = *(undefined8 *)(param_1 + 0x748);
  uStack_50 = *(undefined8 *)(param_1 + 0x750);
  local_48 = *(undefined8 *)(param_1 + 0x718);
  uStack_40 = *(undefined8 *)(param_1 + 0x720);
  local_38 = *(undefined8 *)(param_1 + 0x728);
  uStack_30 = *(undefined8 *)(param_1 + 0x730);
  FUN_000181d0(&local_48,&local_68);
  lVar6 = *(long *)(param_1 + 0x708);
  if (lVar6 != 0) {
    puVar4 = *(undefined8 **)(param_1 + 0x730);
    puVar1 = (undefined8 *)(*(long *)(param_1 + 0x750) + 8);
    if (puVar4 < puVar1) {
      do {
        uVar2 = *puVar4;
        puVar4 = puVar4 + 1;
        thunk_FUN_000d36e0(uVar2,0x1f8);
      } while (puVar4 < puVar1);
      lVar6 = *(long *)(param_1 + 0x708);
    }
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0x710) * 8);
  }
  plVar3 = *(long **)(param_1 + 0x6c8);
  plVar5 = *(long **)(param_1 + 0x6c0);
  if (plVar3 != plVar5) {
    do {
      if ((long *)*plVar5 != plVar5 + 2) {
        thunk_FUN_000d36e0((long *)*plVar5,plVar5[2] + 1);
      }
      plVar5 = plVar5 + 7;
    } while (plVar3 != plVar5);
    plVar5 = *(long **)(param_1 + 0x6c0);
  }
  if (plVar5 != (long *)0x0) {
    thunk_FUN_000d36e0(plVar5,*(long *)(param_1 + 0x6d0) - (long)plVar5);
  }
  lVar6 = *(long *)(param_1 + 0x5a8);
  if (lVar6 == 0) {
    if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
      return;
    }
  }
  else if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0x5b8) - lVar6);
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


