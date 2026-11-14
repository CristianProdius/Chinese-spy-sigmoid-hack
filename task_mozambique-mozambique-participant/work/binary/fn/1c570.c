// ===== FUNC 1c570 size=98

bool FUN_0001c570(undefined8 *param_1,undefined8 *param_2)

{
  size_t __n;
  int iVar1;
  bool bVar2;
  
  __n = param_1[1];
  bVar2 = false;
  if (__n == param_2[1]) {
    if ((__n != 0) && (iVar1 = memcmp((void *)*param_1,(void *)*param_2,__n), iVar1 != 0)) {
      return false;
    }
    bVar2 = false;
    if ((((*(int *)(param_1 + 4) == *(int *)(param_2 + 4)) &&
         (*(int *)((long)param_1 + 0x24) == *(int *)((long)param_2 + 0x24))) &&
        (bVar2 = false, *(int *)(param_1 + 5) == *(int *)(param_2 + 5))) &&
       (*(int *)((long)param_1 + 0x2c) == *(int *)((long)param_2 + 0x2c))) {
      bVar2 = *(int *)(param_1 + 6) == *(int *)(param_2 + 6);
    }
  }
  return bVar2;
}


