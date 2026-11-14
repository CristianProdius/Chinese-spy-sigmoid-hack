// ===== FUNC 18de0 size=419

void FUN_00018de0(long param_1)

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
  
  lVar6 = *(long *)(param_1 + 0xee8);
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  if (lVar6 != 0) {
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0xef8) - lVar6);
  }
  local_68 = *(undefined8 *)(param_1 + 0xec8);
  uStack_60 = *(undefined8 *)(param_1 + 0xed0);
  local_58 = *(undefined8 *)(param_1 + 0xed8);
  uStack_50 = *(undefined8 *)(param_1 + 0xee0);
  local_48 = *(undefined8 *)(param_1 + 0xea8);
  uStack_40 = *(undefined8 *)(param_1 + 0xeb0);
  local_38 = *(undefined8 *)(param_1 + 0xeb8);
  uStack_30 = *(undefined8 *)(param_1 + 0xec0);
  FUN_000181d0(&local_48,&local_68);
  lVar6 = *(long *)(param_1 + 0xe98);
  if (lVar6 != 0) {
    puVar4 = *(undefined8 **)(param_1 + 0xec0);
    puVar1 = (undefined8 *)(*(long *)(param_1 + 0xee0) + 8);
    if (puVar4 < puVar1) {
      do {
        uVar2 = *puVar4;
        puVar4 = puVar4 + 1;
        thunk_FUN_000d36e0(uVar2,0x1f8);
      } while (puVar4 < puVar1);
      lVar6 = *(long *)(param_1 + 0xe98);
    }
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0xea0) * 8);
  }
  plVar3 = *(long **)(param_1 + 0xe58);
  plVar5 = *(long **)(param_1 + 0xe50);
  if (plVar3 != plVar5) {
    do {
      if ((long *)*plVar5 != plVar5 + 2) {
        thunk_FUN_000d36e0((long *)*plVar5,plVar5[2] + 1);
      }
      plVar5 = plVar5 + 7;
    } while (plVar3 != plVar5);
    plVar5 = *(long **)(param_1 + 0xe50);
  }
  if (plVar5 != (long *)0x0) {
    thunk_FUN_000d36e0(plVar5,*(long *)(param_1 + 0xe60) - (long)plVar5);
  }
  lVar6 = *(long *)(param_1 + 0xd38);
  if (lVar6 != 0) {
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0xd48) - lVar6);
  }
  lVar6 = *(long *)(param_1 + 0x680);
  if (lVar6 != 0) {
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0x690) - lVar6);
  }
  lVar6 = *(long *)(param_1 + 0x5a8);
  if (lVar6 != 0) {
    thunk_FUN_000d36e0(lVar6,*(long *)(param_1 + 0x5b8) - lVar6);
  }
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    thunk_FUN_000d36e0(param_1,0xf00);
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


