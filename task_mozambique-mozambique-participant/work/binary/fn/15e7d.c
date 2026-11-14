// ===== FUNC 15e7d size=64

void FUN_00015e7d(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015ea2 to 00015ea6 has its CatchHandler @ 00015ebd */
  FUN_00053200(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d458,FUN_000498f0);
}


