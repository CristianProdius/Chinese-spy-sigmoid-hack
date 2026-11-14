// ===== FUNC 40b90 size=190

undefined8
FUN_00040b90(long param_1,undefined8 param_2,undefined4 param_3,long param_4,long param_5,
            long param_6,long param_7,long *param_8)

{
  char *__s1;
  int iVar1;
  char *pcVar2;
  
  __s1 = *(char **)(param_1 + 8);
  if (param_5 == param_7) {
    pcVar2 = *(char **)(param_6 + 8);
    if (__s1 == pcVar2) {
LAB_00040c50:
      *(undefined4 *)((long)param_8 + 0xc) = param_3;
      return 0;
    }
    if (*__s1 == '*') {
      if (__s1 != *(char **)(param_4 + 8)) {
        return 0;
      }
      goto LAB_00040bda;
    }
    iVar1 = strcmp(__s1,pcVar2 + (*pcVar2 == '*'));
    if (iVar1 == 0) goto LAB_00040c50;
    pcVar2 = *(char **)(param_4 + 8);
    if (__s1 == pcVar2) goto LAB_00040bda;
  }
  else {
    pcVar2 = *(char **)(param_4 + 8);
    if (__s1 == pcVar2) goto LAB_00040bda;
    if (*__s1 == '*') {
      return 0;
    }
  }
  iVar1 = strcmp(__s1,pcVar2 + (*pcVar2 == '*'));
  if (iVar1 != 0) {
    return 0;
  }
LAB_00040bda:
  *param_8 = param_5;
  *(undefined4 *)(param_8 + 1) = param_3;
  *(undefined4 *)(param_8 + 2) = 1;
  return 0;
}


