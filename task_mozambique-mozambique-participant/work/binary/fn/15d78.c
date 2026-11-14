// ===== FUNC 15d78 size=64

void FUN_00015d78(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015d9d to 00015da1 has its CatchHandler @ 00015db8 */
  FUN_000531a0(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d410,FUN_00049830);
}


