// ===== FUNC 168fd size=133

void FUN_000168fd(undefined4 param_1)

{
  undefined8 *puVar1;
  undefined *local_48 [2];
  undefined local_38 [16];
  
  puVar1 = (undefined8 *)FUN_00040f40(0x20);
                    /* try { // try from 00016935 to 00016937 has its CatchHandler @ 00016999 */
  (**(code **)(PTR_PTR_FUN_00123160 + 0x20))(local_48,&PTR_PTR_FUN_00123160,param_1);
                    /* try { // try from 00016943 to 00016947 has its CatchHandler @ 00016982 */
  FUN_000da640(puVar1,local_48);
  if (local_48[0] != local_38) {
    FUN_000d36e0();
  }
  *(undefined4 *)(puVar1 + 2) = param_1;
  puVar1[3] = &PTR_PTR_FUN_00123160;
  *puVar1 = &PTR_FUN_00122418;
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(puVar1,&PTR_PTR_FUN_001222d0,FUN_000da810);
}


