// ===== FUNC 1a1c0 size=548

void FUN_0001a1c0(long param_1,long param_2,int param_3,int param_4)

{
  int iVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined auVar4 [16];
  long lVar5;
  long lVar6;
  long in_FS_OFFSET;
  long *local_78 [2];
  long local_68 [2];
  undefined local_58 [16];
  undefined8 local_48;
  long local_40;
  
  uVar2 = DAT_000e2e80;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (*(char *)(param_2 + 0x124) != '\0') {
    lVar6 = (long)param_3 * 0x18;
    do {
      uVar3 = DAT_000e2e80;
      lVar5 = *(long *)(param_2 + 0x10);
      if (*(int *)(lVar5 + 8 + lVar6) == 0) {
        if (*(char *)(param_2 + 0x124) != '\0') goto LAB_0001a2a0;
        break;
      }
      local_58._8_8_ = 0xffffffff;
      local_58._0_8_ = uVar2;
      local_48 = 0xffffffff;
      local_78[0] = local_68;
      FUN_00017bf0(local_78,&DAT_000e0454);
                    /* try { // try from 0001a254 to 0001a258 has its CatchHandler @ 0001a3ee */
      FUN_00019ec0(param_1,param_2,local_78,0);
      if (local_78[0] != local_68) {
        thunk_FUN_000d36e0(local_78[0],local_68[0] + 1);
      }
    } while (*(char *)(param_2 + 0x124) != '\0');
  }
LAB_0001a3ae:
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
LAB_0001a2a0:
  auVar4 = local_58;
  local_58 = auVar4;
  if (*(int *)(lVar5 + lVar6) == param_4) goto LAB_0001a3ae;
  iVar1 = *(int *)(param_1 + 0x368 + (long)*(int *)(lVar5 + lVar6) * 0x28 + (long)param_4 * 4);
  local_58._4_4_ = iVar1;
  local_58._0_4_ = param_3;
  uVar2 = local_58._0_8_;
  if (iVar1 < 0) {
    *(undefined *)(param_2 + 0x124) = 0;
    goto LAB_0001a3ae;
  }
  local_48 = 0xffffffff;
  local_58._0_12_ = ZEXT412(0xffffffff) << 0x40;
  local_58._12_4_ = 0;
  local_78[0] = local_68;
  FUN_00017bf0(local_78,&DAT_000e0459);
  local_58 = CONCAT88(local_58._8_8_,uVar2);
                    /* try { // try from 0001a337 to 0001a33b has its CatchHandler @ 0001a3fe */
  FUN_00019ec0(param_1,param_2,local_78,0);
  while( true ) {
    if (local_78[0] != local_68) {
      thunk_FUN_000d36e0(local_78[0],local_68[0] + 1);
    }
    if (*(char *)(param_2 + 0x124) == '\0') goto LAB_0001a3ae;
    lVar5 = *(long *)(param_2 + 0x10);
    if (*(int *)(lVar5 + 8 + lVar6) == 0) break;
    local_58._8_8_ = 0xffffffff;
    local_58._0_8_ = uVar3;
    local_48 = 0xffffffff;
    local_78[0] = local_68;
    FUN_00017bf0(local_78,&DAT_000e0454);
                    /* try { // try from 0001a388 to 0001a38c has its CatchHandler @ 0001a3f6 */
    FUN_00019ec0(param_1,param_2,local_78,0);
  }
  if (*(char *)(param_2 + 0x124) == '\0') goto LAB_0001a3ae;
  goto LAB_0001a2a0;
}


