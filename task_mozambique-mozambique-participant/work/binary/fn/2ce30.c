// ===== FUNC 2ce30 size=218

void FUN_0002ce30(char *param_1,ulong *param_2)

{
  double dVar1;
  char cVar2;
  ulong uVar3;
  undefined8 uVar4;
  long in_FS_OFFSET;
  undefined local_48 [40];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  cVar2 = *param_1;
  if (cVar2 != '\x06') {
    if (cVar2 == '\a') {
      dVar1 = *(double *)(param_1 + 8);
      if (dVar1 < DAT_000e2e38) {
        uVar3 = (ulong)dVar1;
      }
      else {
        uVar3 = (long)(dVar1 - DAT_000e2e38) ^ 0x8000000000000000;
      }
      goto LAB_0002ce88;
    }
    if (cVar2 != '\x05') {
      uVar4 = FUN_00040f40(0x20);
      FUN_000137b8(*param_1,"type must be number, but is ");
                    /* try { // try from 0002cee2 to 0002cee6 has its CatchHandler @ 0002cf15 */
      FUN_0001df60(local_48);
                    /* try { // try from 0002cef2 to 0002cef6 has its CatchHandler @ 0002cf1a */
      FUN_00013cc9(uVar4,0x12e,local_48);
      FUN_000b07c0(local_48);
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(uVar4,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
    }
  }
  uVar3 = *(ulong *)(param_1 + 8);
LAB_0002ce88:
  *param_2 = uVar3;
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


