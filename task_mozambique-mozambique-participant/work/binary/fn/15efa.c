// ===== FUNC 15efa size=64

void FUN_00015efa(undefined8 param_1)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  uVar1 = FUN_00040f40(0x10);
  uVar2 = gettext(param_1);
                    /* try { // try from 00015f1f to 00015f23 has its CatchHandler @ 00015f3a */
  FUN_00053220(uVar1,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011d470,FUN_00049930);
}


