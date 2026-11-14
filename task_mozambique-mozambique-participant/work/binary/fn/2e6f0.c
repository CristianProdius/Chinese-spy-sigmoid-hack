// ===== FUNC 2e6f0 size=733

long * FUN_0002e6f0(long *param_1,undefined8 param_2,int param_3,char param_4,undefined param_5,
                   undefined4 param_6)

{
  long *plVar1;
  int iVar2;
  long *plVar3;
  long lVar4;
  undefined8 *puVar5;
  long in_FS_OFFSET;
  bool bVar6;
  byte bVar7;
  long *local_2c8;
  long *local_2c0;
  undefined local_2b8 [16];
  undefined local_2a8 [16];
  undefined local_298 [16];
  undefined local_288 [16];
  lconv *local_278;
  char local_270;
  char local_26f;
  undefined local_26e [504];
  undefined8 local_76;
  char local_6e;
  long *local_68 [2];
  long local_58 [2];
  undefined4 local_48;
  long local_40;
  
  bVar7 = 0;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  param_1[1] = 0;
  *param_1 = (long)(param_1 + 2);
  *(undefined *)(param_1 + 2) = 0;
                    /* try { // try from 0002e747 to 0002e74b has its CatchHandler @ 0002e9f7 */
  plVar3 = (long *)FUN_00041fe0(0x20);
  lVar4 = DAT_000e2dc0;
  plVar1 = plVar3 + 1;
  bVar6 = __libc_single_threaded == '\0';
  plVar3[3] = (long)param_1;
  plVar3[1] = lVar4;
  *plVar3 = (long)&PTR_FUN_0011bb68;
  plVar3[2] = (long)&PTR_FUN_0011bb38;
  local_2c8 = plVar3 + 2;
  if (bVar6) {
    LOCK();
    *(int *)(plVar3 + 1) = *(int *)(plVar3 + 1) + 1;
    UNLOCK();
  }
  else {
    *(undefined4 *)(plVar3 + 1) = 2;
  }
  local_2b8 = (undefined  [16])0x0;
  local_2a8 = (undefined  [16])0x0;
  local_298 = (undefined  [16])0x0;
  local_288 = (undefined  [16])0x0;
  local_2c0 = plVar3;
  local_278 = localeconv();
  local_270 = '\0';
  if (local_278->thousands_sep != (char *)0x0) {
    local_270 = *local_278->thousands_sep;
  }
  local_26f = '\0';
  if (local_278->decimal_point != (char *)0x0) {
    local_26f = *local_278->decimal_point;
  }
  local_26e._0_8_ = 0;
  local_76 = 0;
  puVar5 = (undefined8 *)(local_26e + 6);
  for (lVar4 = 0x3f; lVar4 != 0; lVar4 = lVar4 + -1) {
    *puVar5 = 0;
    puVar5 = puVar5 + (ulong)bVar7 * -2 + 1;
  }
  local_6e = param_4;
  local_68[0] = local_58;
                    /* try { // try from 0002e833 to 0002e837 has its CatchHandler @ 0002e9f2 */
  FUN_000b0800(local_68,0x200,(int)param_4);
  local_48 = param_6;
  if (plVar3[1] == 0x100000001) {
    plVar3[1] = 0;
    (**(code **)(*plVar3 + 0x10))(plVar3);
    (**(code **)(*plVar3 + 0x18))(plVar3);
  }
  else {
    if (__libc_single_threaded == '\0') {
      LOCK();
      iVar2 = *(int *)plVar1;
      *(int *)plVar1 = *(int *)plVar1 + -1;
      UNLOCK();
    }
    else {
      iVar2 = *(int *)(plVar3 + 1);
      *(int *)(plVar3 + 1) = iVar2 + -1;
    }
    if (iVar2 == 1) {
      FUN_0001ca80(plVar3);
    }
  }
  if (param_3 < 0) {
    FUN_0002d610(&local_2c8,param_2,0,param_5,0,0);
  }
  else {
                    /* try { // try from 0002e89b to 0002e941 has its CatchHandler @ 0002e9fc */
    FUN_0002d610(&local_2c8,param_2,1,param_5,param_3,0);
  }
  if (local_68[0] != local_58) {
    thunk_FUN_000d36e0(local_68[0],local_58[0] + 1);
  }
  plVar1 = local_2c0;
  if (local_2c0 != (long *)0x0) {
    plVar3 = local_2c0 + 1;
    if (local_2c0[1] == 0x100000001) {
      local_2c0[1] = 0;
      (**(code **)(*local_2c0 + 0x10))(local_2c0);
      (**(code **)(*plVar1 + 0x18))(plVar1);
    }
    else {
      if (__libc_single_threaded == '\0') {
        LOCK();
        iVar2 = *(int *)plVar3;
        *(int *)plVar3 = *(int *)plVar3 + -1;
        UNLOCK();
      }
      else {
        iVar2 = *(int *)(local_2c0 + 1);
        *(int *)(local_2c0 + 1) = iVar2 + -1;
      }
      if (iVar2 == 1) {
        FUN_0001ca80(local_2c0);
      }
    }
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


