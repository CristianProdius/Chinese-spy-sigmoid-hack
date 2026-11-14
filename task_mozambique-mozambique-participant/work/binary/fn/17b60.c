// ===== FUNC 17b60 size=44

undefined8 FUN_00017b60(undefined8 *param_1,undefined8 *param_2,int param_3)

{
  if (param_3 == 0) {
    *param_1 = &PTR_PTR_FUN_0011ccc0;
    return 0;
  }
  if (param_3 != 1) {
    if (param_3 == 2) {
      *param_1 = *param_2;
    }
    return 0;
  }
  *param_1 = param_2;
  return 0;
}


