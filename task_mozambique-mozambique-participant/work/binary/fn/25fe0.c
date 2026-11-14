// ===== FUNC 25fe0 size=152

void FUN_00025fe0(undefined *param_1,long *param_2)

{
  long lVar1;
  long lVar2;
  long *plVar3;
  long in_FS_OFFSET;
  undefined local_49;
  undefined *local_48;
  long *local_40;
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  *param_1 = 0;
  *(undefined8 *)(param_1 + 8) = 0;
                    /* try { // try from 00026014 to 00026025 has its CatchHandler @ 0002607d */
  FUN_00024620(param_1 + 8,0);
  *param_1 = 3;
  plVar3 = (long *)FUN_00041fe0(0x20);
  local_48 = &local_49;
  lVar1 = *param_2;
  lVar2 = param_2[1];
  *plVar3 = (long)(plVar3 + 2);
  local_40 = plVar3;
                    /* try { // try from 0002604f to 00026053 has its CatchHandler @ 00026078 */
  FUN_00017e00(plVar3,lVar1,lVar2 + lVar1);
  *(long **)(param_1 + 8) = plVar3;
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


