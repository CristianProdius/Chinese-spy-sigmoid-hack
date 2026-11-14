// ===== FUNC 409e0 size=90

bool FUN_000409e0(long *param_1,undefined8 param_2,undefined8 *param_3)

{
  bool bVar1;
  undefined8 local_28;
  undefined8 local_20;
  undefined8 local_18;
  
  local_20 = 0x1000000000;
  local_28 = 0;
  local_18 = 0;
  (**(code **)(*param_1 + 0x30))(param_1,param_2,*param_3,&local_28);
  bVar1 = ((uint)local_20 & 6) == 6;
  if (bVar1) {
    *param_3 = local_28;
  }
  return bVar1;
}


