// ===== FUNC 40b00 size=125

undefined8 FUN_00040b00(long param_1,long *param_2,undefined8 param_3,uint param_4)

{
  char *__s1;
  char *pcVar1;
  int iVar2;
  undefined8 uVar3;
  
  __s1 = *(char **)(param_1 + 8);
  pcVar1 = (char *)param_2[1];
  if (__s1 == pcVar1) {
    return 1;
  }
  if ((*__s1 != '*') && (iVar2 = strcmp(__s1,pcVar1 + (*pcVar1 == '*')), iVar2 == 0)) {
    return 1;
  }
  if (3 < param_4) {
    return 0;
  }
                    /* WARNING: Could not recover jumptable at 0x00040b6f. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  uVar3 = (**(code **)(*param_2 + 0x28))(param_2,param_1,param_3);
  return uVar3;
}


