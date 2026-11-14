// ===== FUNC 1bf10 size=44

void FUN_0001bf10(undefined8 *param_1,undefined4 param_2,undefined8 param_3)

{
  *param_1 = &PTR_FUN_0011ba70;
  *(undefined4 *)(param_1 + 1) = param_2;
                    /* try { // try from 0001bf30 to 0001bf34 has its CatchHandler @ 0001bf3c */
  FUN_00053220(param_1 + 2,param_3);
  return;
}


