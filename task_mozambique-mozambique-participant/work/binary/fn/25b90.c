// ===== FUNC 25b90 size=165

long * FUN_00025b90(long *param_1,char *param_2,undefined8 *param_3)

{
  size_t sVar1;
  
  *param_1 = (long)(param_1 + 2);
  param_1[1] = 0;
  *(undefined *)(param_1 + 2) = 0;
  sVar1 = strlen(param_2);
                    /* try { // try from 00025bc3 to 00025c34 has its CatchHandler @ 00025c35 */
  FUN_000b1110(param_1,sVar1 + param_3[1]);
  sVar1 = strlen(param_2);
  if (0x3fffffffffffffffU - param_1[1] < sVar1) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(param_1,param_2);
  if ((ulong)param_3[1] <= 0x3fffffffffffffffU - param_1[1]) {
    FUN_000b2500(param_1);
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append",*param_3);
}


