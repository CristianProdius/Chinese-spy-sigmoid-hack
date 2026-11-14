// ===== FUNC 15d21 size=64

void FUN_00015d21(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015d46 to 00015d4a has its CatchHandler @ 00015d61 */
  FUN_000530c0(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d3f8,FUN_00049790);
}


