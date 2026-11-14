// ===== FUNC 16809 size=144

void FUN_00016809(undefined8 param_1,int param_2)

{
  undefined8 *puVar1;
  undefined8 uVar2;
  int local_28 [2];
  undefined8 local_20;
  
  puVar1 = (undefined8 *)FUN_00040f40(0x30);
  if (param_2 == 0) {
    local_20 = FUN_000da4c0();
    local_28[0] = 1;
  }
  else {
    local_20 = FUN_000daab0();
    local_28[0] = param_2;
  }
  uVar2 = gettext(param_1);
                    /* try { // try from 0001685c to 00016860 has its CatchHandler @ 000168aa */
  FUN_000da540(puVar1,uVar2,local_28);
  *puVar1 = &PTR_FUN_00122250;
  uVar2 = FUN_00049780(puVar1);
                    /* try { // try from 0001687e to 00016882 has its CatchHandler @ 00016899 */
  FUN_000db0b0(puVar1 + 4,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(puVar1,&PTR_PTR_FUN_00122188,FUN_000d9d80);
}


