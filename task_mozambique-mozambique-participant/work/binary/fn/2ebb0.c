// ===== FUNC 2ebb0 size=53

void FUN_0002ebb0(undefined *param_1,undefined *param_2)

{
  undefined *puVar1;
  undefined uVar2;
  
  if (param_1 == param_2) {
    return;
  }
  do {
    uVar2 = *param_1;
    puVar1 = param_1 + 8;
    param_1 = param_1 + 0x10;
    FUN_00024620(puVar1,uVar2);
  } while (param_2 != param_1);
  return;
}


