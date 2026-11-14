// ===== FUNC 15fa8 size=64

void FUN_00015fa8(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015fcd to 00015fd1 has its CatchHandler @ 00015fe8 */
  FUN_00053320(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d4a0,FUN_00049a10);
}


