// ===== FUNC 1a8e0 size=67

long FUN_0001a8e0(long param_1,undefined *param_2)

{
  char *__s1;
  int iVar1;
  
  if ((param_2 != &DAT_000e2d90) &&
     (__s1 = *(char **)(param_2 + 8), __s1 != "St19_Sp_make_shared_tag")) {
    if (*__s1 == '*') {
      return 0;
    }
    iVar1 = strcmp(__s1,"St19_Sp_make_shared_tag");
    if (iVar1 != 0) {
      return 0;
    }
  }
  return param_1 + 0x10;
}


