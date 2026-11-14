// ===== FUNC 2edc0 size=292

long FUN_0002edc0(long *param_1,undefined *param_2)

{
  undefined uVar1;
  char *pcVar2;
  undefined *puVar3;
  undefined8 uVar4;
  long lVar5;
  long in_FS_OFFSET;
  undefined8 local_30 [2];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_1[1] == param_1[2]) {
    uVar1 = *param_2;
    FUN_000210f0(local_30);
    puVar3 = (undefined *)*param_1;
    *puVar3 = uVar1;
    uVar4 = *(undefined8 *)(puVar3 + 8);
    *(undefined8 *)(puVar3 + 8) = local_30[0];
    local_30[0] = uVar4;
    FUN_00024620(local_30);
    lVar5 = *param_1;
  }
  else {
    pcVar2 = *(char **)(param_1[2] + -8);
    if (*pcVar2 == '\x02') {
      lVar5 = *(long *)(pcVar2 + 8);
      puVar3 = *(undefined **)(lVar5 + 8);
      if (puVar3 == *(undefined **)(lVar5 + 0x10)) {
        FUN_0002ebf0(lVar5,puVar3,param_2);
      }
      else {
        *puVar3 = *param_2;
        FUN_000210f0();
        *(long *)(lVar5 + 8) = *(long *)(lVar5 + 8) + 0x10;
      }
      lVar5 = *(long *)(*(long *)(*(long *)(param_1[2] + -8) + 8) + 8) + -0x10;
    }
    else {
      uVar1 = *param_2;
      FUN_000210f0(local_30);
      puVar3 = (undefined *)param_1[4];
      *puVar3 = uVar1;
      uVar4 = *(undefined8 *)(puVar3 + 8);
      *(undefined8 *)(puVar3 + 8) = local_30[0];
      local_30[0] = uVar4;
      FUN_00024620(local_30);
      lVar5 = param_1[4];
    }
  }
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return lVar5;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


