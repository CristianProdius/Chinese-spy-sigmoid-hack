// ===== FUNC 1a590 size=156

ulong FUN_0001a590(byte *param_1)

{
  byte bVar1;
  undefined8 uVar2;
  ulong uVar3;
  long in_FS_OFFSET;
  ulong local_60 [6];
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  if (*param_1 != 6) {
FUN_00014085:
    uVar2 = FUN_00040f40(0x10);
    FUN_00053220(uVar2,"expected uint32");
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar2,&PTR_PTR_FUN_0011d470,FUN_00049930);
  }
  local_60[0] = 0;
  FUN_0002ce30(param_1,local_60);
  if (0xffffffff < local_60[0]) goto FUN_00014085;
  bVar1 = *param_1;
  if (bVar1 != 6) {
    if (6 < bVar1) {
      if (bVar1 != 7) {
        uVar3 = FUN_000140b7();
        return uVar3;
      }
      uVar3 = (ulong)*(double *)(param_1 + 8);
      goto LAB_0001a5ed;
    }
    if (bVar1 == 4) {
      uVar3 = (ulong)param_1[8];
      goto LAB_0001a5ed;
    }
    if (bVar1 != 5) {
      uVar3 = FUN_000140b7();
      return uVar3;
    }
  }
  uVar3 = (ulong)*(uint *)(param_1 + 8);
LAB_0001a5ed:
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar3;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


