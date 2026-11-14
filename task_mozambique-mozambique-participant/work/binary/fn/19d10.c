// ===== FUNC 19d10 size=374

undefined8 FUN_00019d10(long *param_1,int *param_2,char *param_3,char *param_4)

{
  char cVar1;
  long lVar2;
  long lVar3;
  undefined8 uVar4;
  char extraout_DL;
  long in_FS_OFFSET;
  undefined *local_78;
  undefined8 local_70;
  undefined local_68;
  undefined7 uStack_67;
  undefined auStack_58 [40];
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  cVar1 = *param_3;
  if (0x40 < *param_2) {
    uVar4 = FUN_00040f40(0x10);
    FUN_00053220(uVar4,"JSON nesting limit");
                    /* WARNING: Subroutine does not return */
    FUN_00041f00(uVar4,&PTR_PTR_FUN_0011d470,FUN_00049930);
  }
  if (cVar1 == '\0') {
    lVar3 = *param_1;
    lVar2 = *(long *)(lVar3 + 8);
    if (lVar2 == *(long *)(lVar3 + 0x10)) {
      FUN_00020aa0();
    }
    else {
      *(undefined4 *)(lVar2 + 8) = 0;
      *(undefined8 *)(lVar2 + 0x10) = 0;
      *(long *)(lVar2 + 0x18) = lVar2 + 8;
      *(long *)(lVar2 + 0x20) = lVar2 + 8;
      *(undefined8 *)(lVar2 + 0x28) = 0;
      *(long *)(lVar3 + 8) = lVar2 + 0x30;
    }
  }
  else {
    if (cVar1 == '\x04') {
      lVar3 = ((long *)*param_1)[1];
      if (lVar3 != *(long *)*param_1) {
        local_68 = 0;
        local_70 = 0;
        local_78 = &local_68;
        if (*param_4 != '\x03') {
          uVar4 = FUN_00040f40(0x20);
          FUN_000137b8(*param_4,"type must be string, but is ");
          FUN_0001df60(auStack_58);
          FUN_00013cc9(uVar4,0x12e,auStack_58);
          FUN_000b07c0(auStack_58);
                    /* WARNING: Subroutine does not return */
          FUN_00041f00(uVar4,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
        }
                    /* try { // try from 00019dad to 00019db1 has its CatchHandler @ 00019eaf */
        FUN_000b0ad0(&local_78,*(undefined8 *)(param_4 + 8));
                    /* try { // try from 00019db9 to 00019dbd has its CatchHandler @ 00019ea7 */
        FUN_00020da0(lVar3 + -0x30,&local_78);
        if (extraout_DL != '\0') {
          if (local_78 != &local_68) {
            thunk_FUN_000d36e0(local_78,CONCAT71(uStack_67,local_68) + 1);
          }
          goto LAB_00019d4a;
        }
        if (local_78 != &local_68) {
          thunk_FUN_000d36e0(local_78,CONCAT71(uStack_67,local_68) + 1);
        }
      }
      uVar4 = FUN_00040f40(0x10);
                    /* try { // try from 00019e82 to 00019e86 has its CatchHandler @ 00019e9f */
      FUN_00053220(uVar4,"duplicate key");
      uVar4 = FUN_00013ecf();
      return uVar4;
    }
    if (cVar1 == '\x01') {
      lVar3 = *(long *)(*param_1 + 8);
      uVar4 = *(undefined8 *)(lVar3 + -0x20);
      *(long *)(*param_1 + 8) = lVar3 + -0x30;
      FUN_00018460(uVar4);
    }
  }
LAB_00019d4a:
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return 1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


