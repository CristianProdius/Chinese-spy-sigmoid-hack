// ===== FUNC 1a6f0 size=150

undefined8 FUN_0001a6f0(long *param_1,long *param_2,int param_3)

{
  undefined8 *puVar1;
  undefined8 uVar2;
  undefined8 *puVar3;
  
  if (param_3 == 0) {
    *param_1 = (long)&PTR_PTR_FUN_0011ccb0;
    return 0;
  }
  if (param_3 != 1) {
    if (param_3 == 2) {
      puVar1 = (undefined8 *)*param_2;
      puVar3 = (undefined8 *)FUN_00041fe0(0x48);
      uVar2 = puVar1[1];
      *puVar3 = *puVar1;
      puVar3[1] = uVar2;
      uVar2 = puVar1[3];
      puVar3[2] = puVar1[2];
      puVar3[3] = uVar2;
      uVar2 = puVar1[5];
      puVar3[4] = puVar1[4];
      puVar3[5] = uVar2;
      uVar2 = puVar1[7];
      puVar3[6] = puVar1[6];
      puVar3[7] = uVar2;
      puVar3[8] = puVar1[8];
      *param_1 = (long)puVar3;
    }
    else if ((param_3 == 3) && (*param_1 != 0)) {
      thunk_FUN_000d36e0(*param_1,0x48);
    }
    return 0;
  }
  *param_1 = *param_2;
  return 0;
}


