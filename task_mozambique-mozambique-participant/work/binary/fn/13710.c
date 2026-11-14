// ===== FUNC 13710 size=88

void FUN_00013710(long param_1)

{
  undefined8 *puVar1;
  
  puVar1 = (undefined8 *)FUN_00040f40(0x28);
  *puVar1 = &PTR_FUN_0011ba70;
  *(undefined4 *)(puVar1 + 1) = *(undefined4 *)(param_1 + 8);
  FUN_00052fc0(puVar1 + 2,param_1 + 0x10);
  *puVar1 = &PTR_FUN_0011ba98;
  puVar1[4] = *(undefined8 *)(param_1 + 0x20);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(puVar1,&PTR_PTR_FUN_0011cc40,FUN_0001aab0);
}


