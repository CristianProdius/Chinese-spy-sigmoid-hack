// ===== FUNC 16765 size=124

void FUN_00016765(undefined8 param_1)

{
  undefined8 *puVar1;
  undefined8 uVar2;
  undefined4 local_28 [2];
  undefined8 local_20;
  
  puVar1 = (undefined8 *)FUN_00040f40(0x30);
  uVar2 = gettext(param_1);
  local_20 = FUN_000da4c0();
  local_28[0] = 1;
                    /* try { // try from 000167a4 to 000167a8 has its CatchHandler @ 000167f2 */
  FUN_000da540(puVar1,uVar2,local_28);
  *puVar1 = &PTR_FUN_00122250;
  uVar2 = FUN_00049780(puVar1);
                    /* try { // try from 000167c6 to 000167ca has its CatchHandler @ 000167e1 */
  FUN_000db0b0(puVar1 + 4,uVar2);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(puVar1,&PTR_PTR_FUN_00122188,FUN_000d9d80);
}


