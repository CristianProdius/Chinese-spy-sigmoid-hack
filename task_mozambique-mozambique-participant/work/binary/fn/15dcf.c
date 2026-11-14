// ===== FUNC 15dcf size=64

void FUN_00015dcf(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015df4 to 00015df8 has its CatchHandler @ 00015e0f */
  FUN_000531c0(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d428,FUN_00049870);
}


