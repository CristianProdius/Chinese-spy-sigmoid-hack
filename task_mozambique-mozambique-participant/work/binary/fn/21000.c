// ===== FUNC 21000 size=214

long * FUN_00021000(long *param_1,undefined8 *param_2,undefined8 *param_3,undefined8 *param_4)

{
  long lVar1;
  
  param_1[1] = 0;
  *(undefined *)(param_1 + 2) = 0;
  lVar1 = param_4[1];
  *param_1 = (long)(param_1 + 2);
                    /* try { // try from 00021035 to 000210d5 has its CatchHandler @ 000210d6 */
  FUN_000b1110(param_1,lVar1 + param_3[1] + param_2[1]);
  if (0x3fffffffffffffffU - param_1[1] < (ulong)param_2[1]) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",*param_2);
  }
  FUN_000b2500(param_1);
  if ((ulong)param_3[1] <= 0x3fffffffffffffffU - param_1[1]) {
    FUN_000b2500(param_1);
    if ((ulong)param_4[1] <= 0x3fffffffffffffffU - param_1[1]) {
      FUN_000b2500(param_1);
      return param_1;
    }
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append",*param_4);
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append",*param_3);
}


