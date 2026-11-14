// ===== FUNC 40aa0 size=87

undefined8 FUN_00040aa0(long param_1,long param_2,undefined8 param_3,undefined8 *param_4)

{
  char *__s1;
  char *pcVar1;
  int iVar2;
  
  __s1 = *(char **)(param_1 + 8);
  pcVar1 = *(char **)(param_2 + 8);
  if (__s1 != pcVar1) {
    if (*__s1 == '*') {
      return 0;
    }
    iVar2 = strcmp(__s1,pcVar1 + (*pcVar1 == '*'));
    if (iVar2 != 0) {
      return 0;
    }
  }
  *param_4 = param_3;
  param_4[2] = 0x10;
  *(undefined4 *)(param_4 + 1) = 6;
  return 1;
}


