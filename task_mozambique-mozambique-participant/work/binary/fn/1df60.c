// ===== FUNC 1df60 size=195

long * FUN_0001df60(long *param_1,char *param_2,undefined8 *param_3)

{
  char *__s;
  size_t sVar1;
  size_t sVar2;
  
  *param_1 = (long)(param_1 + 2);
  param_1[1] = 0;
  *(undefined *)(param_1 + 2) = 0;
  sVar1 = strlen(param_2);
  sVar2 = strlen((char *)*param_3);
                    /* try { // try from 0001dfa2 to 0001e022 has its CatchHandler @ 0001e023 */
  FUN_000b1110(param_1,sVar1 + sVar2);
  sVar1 = strlen(param_2);
  if (0x3fffffffffffffffU - param_1[1] < sVar1) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(param_1,param_2);
  __s = (char *)*param_3;
  sVar1 = strlen(__s);
  if (sVar1 <= 0x3fffffffffffffffU - param_1[1]) {
    FUN_000b2500(param_1,__s);
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append");
}


