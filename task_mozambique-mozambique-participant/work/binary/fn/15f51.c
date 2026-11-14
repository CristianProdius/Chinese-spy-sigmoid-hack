// ===== FUNC 15f51 size=64

void FUN_00015f51(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015f76 to 00015f7a has its CatchHandler @ 00015f91 */
  FUN_00053300(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d488,FUN_000499d0);
}


