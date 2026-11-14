// ===== FUNC 1d970 size=205

void FUN_0001d970(long *param_1)

{
  long lVar1;
  undefined8 uVar2;
  undefined8 *puVar3;
  long lVar4;
  long in_FS_OFFSET;
  long local_68;
  long lStack_60;
  long local_58;
  long lStack_50;
  long local_48;
  long lStack_40;
  long local_38;
  long lStack_30;
  long local_20;
  
  local_68 = param_1[6];
  lStack_60 = param_1[7];
  local_58 = param_1[8];
  lStack_50 = param_1[9];
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  local_48 = param_1[2];
  lStack_40 = param_1[3];
  local_38 = param_1[4];
  lStack_30 = param_1[5];
  FUN_000181d0(&local_48,&local_68);
  lVar4 = *param_1;
  if (lVar4 == 0) {
    if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
      return;
    }
  }
  else {
    lVar1 = param_1[9];
    puVar3 = (undefined8 *)param_1[5];
    if (puVar3 < (undefined8 *)(lVar1 + 8U)) {
      do {
        uVar2 = *puVar3;
        puVar3 = puVar3 + 1;
        thunk_FUN_000d36e0(uVar2,0x1f8);
      } while (puVar3 < (undefined8 *)(lVar1 + 8U));
      lVar4 = *param_1;
    }
    if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
      thunk_FUN_000d36e0(lVar4,param_1[1] << 3);
      return;
    }
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail(lVar4);
}


