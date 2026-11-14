// ===== FUNC 19a20 size=728

undefined8 * FUN_00019a20(undefined8 *param_1,undefined8 *param_2,undefined8 *param_3)

{
  void *__s2;
  size_t __n;
  char cVar1;
  int iVar2;
  long lVar3;
  undefined8 *puVar4;
  undefined8 *local_40;
  
  lVar3 = ((long)param_2 - (long)param_1 >> 3) * 0x6db6db6db6db6db7;
  if (0 < lVar3 >> 2) {
    __s2 = (void *)*param_3;
    __n = param_3[1];
    puVar4 = param_1 + (lVar3 >> 2) * 0x1c;
    do {
      if ((((param_1[1] == __n) &&
           (((__n == 0 || (iVar2 = memcmp((void *)*param_1,__s2,__n), iVar2 == 0)) &&
            (*(int *)(param_1 + 4) == *(int *)(param_3 + 4))))) &&
          (((*(int *)((long)param_1 + 0x24) == *(int *)((long)param_3 + 0x24) &&
            (*(int *)(param_1 + 5) == *(int *)(param_3 + 5))) &&
           (*(int *)((long)param_1 + 0x2c) == *(int *)((long)param_3 + 0x2c))))) &&
         (*(int *)(param_1 + 6) == *(int *)(param_3 + 6))) {
        return param_1;
      }
      if (((__n == param_1[8]) &&
          ((__n == 0 || (iVar2 = memcmp((void *)param_1[7],__s2,__n), iVar2 == 0)))) &&
         ((*(int *)(param_1 + 0xb) == *(int *)(param_3 + 4) &&
          ((((*(int *)((long)param_1 + 0x5c) == *(int *)((long)param_3 + 0x24) &&
             (*(int *)(param_1 + 0xc) == *(int *)(param_3 + 5))) &&
            (*(int *)((long)param_1 + 100) == *(int *)((long)param_3 + 0x2c))) &&
           (*(int *)(param_1 + 0xd) == *(int *)(param_3 + 6))))))) {
        return param_1 + 7;
      }
      if ((((__n == param_1[0xf]) &&
           ((__n == 0 || (iVar2 = memcmp((void *)param_1[0xe],__s2,__n), iVar2 == 0)))) &&
          (*(int *)(param_1 + 0x12) == *(int *)(param_3 + 4))) &&
         (((*(int *)((long)param_1 + 0x94) == *(int *)((long)param_3 + 0x24) &&
           (*(int *)(param_1 + 0x13) == *(int *)(param_3 + 5))) &&
          ((*(int *)((long)param_1 + 0x9c) == *(int *)((long)param_3 + 0x2c) &&
           (*(int *)(param_1 + 0x14) == *(int *)(param_3 + 6))))))) {
        return param_1 + 0xe;
      }
      if (((__n == param_1[0x16]) &&
          (((__n == 0 || (iVar2 = memcmp((void *)param_1[0x15],__s2,__n), iVar2 == 0)) &&
           (*(int *)(param_1 + 0x19) == *(int *)(param_3 + 4))))) &&
         (((*(int *)((long)param_1 + 0xcc) == *(int *)((long)param_3 + 0x24) &&
           (*(int *)(param_1 + 0x1a) == *(int *)(param_3 + 5))) &&
          ((*(int *)((long)param_1 + 0xd4) == *(int *)((long)param_3 + 0x2c) &&
           (*(int *)(param_1 + 0x1b) == *(int *)(param_3 + 6))))))) {
        return param_1 + 0x15;
      }
      param_1 = param_1 + 0x1c;
    } while (param_1 != puVar4);
    lVar3 = ((long)param_2 - (long)param_1 >> 3) * 0x6db6db6db6db6db7;
  }
  if (lVar3 != 2) {
    if (lVar3 != 3) {
      if (lVar3 != 1) {
        return param_2;
      }
      goto LAB_00019cae;
    }
    cVar1 = FUN_0001c570(param_1,param_3);
    if (cVar1 != '\0') {
      return param_1;
    }
    param_1 = param_1 + 7;
  }
  cVar1 = FUN_0001c570(param_1,param_3);
  if (cVar1 != '\0') {
    return param_1;
  }
  param_1 = param_1 + 7;
LAB_00019cae:
  cVar1 = FUN_0001c570(param_1,param_3);
  local_40 = param_1;
  if (cVar1 == '\0') {
    local_40 = param_2;
  }
  return local_40;
}


