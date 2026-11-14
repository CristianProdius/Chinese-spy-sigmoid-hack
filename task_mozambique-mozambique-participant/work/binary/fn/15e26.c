// ===== FUNC 15e26 size=64

void FUN_00015e26(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015e4b to 00015e4f has its CatchHandler @ 00015e66 */
  FUN_000531e0(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d440,FUN_000498b0);
}


