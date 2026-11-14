// ===== FUNC 15fff size=64

void FUN_00015fff(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00016024 to 00016028 has its CatchHandler @ 0001603f */
  FUN_00053340(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d4b8,FUN_00049a50);
}


