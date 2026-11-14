// ===== FUNC 1c360 size=490

undefined * FUN_0001c360(undefined2 *param_1,int param_2,int param_3,int param_4,int param_5)

{
  undefined *puVar1;
  uint uVar2;
  size_t __n;
  int iVar3;
  size_t __n_00;
  
  __n = (size_t)param_2;
  iVar3 = param_2 + param_3;
  if ((param_2 <= iVar3) && (iVar3 <= param_5)) {
    memset((void *)((long)param_2 + (long)param_1),0x30,(long)param_3);
    *(undefined2 *)((long)param_1 + (long)iVar3) = DAT_000e2da0;
    return (undefined *)((long)param_1 + (long)iVar3 + 2);
  }
  if ((0 < iVar3) && (iVar3 <= param_5)) {
    puVar1 = (undefined *)((long)param_1 + (long)iVar3);
    memmove((void *)((long)param_1 + (long)iVar3 + 1),puVar1,-(long)param_3);
    *puVar1 = 0x2e;
    return (undefined *)((long)param_1 + __n + 1);
  }
  if ((param_4 < iVar3) && (iVar3 < 1)) {
    __n_00 = (size_t)-iVar3;
    memmove((void *)((long)param_1 + __n_00 + 2),param_1,__n);
    *param_1 = DAT_000e2da2;
    memset(param_1 + 1,0x30,__n_00);
    return (undefined *)(__n + 2 + __n_00 + (long)param_1);
  }
  puVar1 = (undefined *)((long)param_1 + 1);
  if (param_2 == 1) {
    *puVar1 = 0x65;
  }
  else {
    memmove(param_1 + 1,puVar1,__n - 1);
    puVar1 = (undefined *)((long)param_1 + __n + 1);
    *(undefined *)((long)param_1 + 1) = 0x2e;
    *puVar1 = 0x65;
  }
  if (iVar3 + -1 < 0) {
    uVar2 = 1 - iVar3;
    puVar1[1] = 0x2d;
  }
  else {
    uVar2 = iVar3 - 1;
    puVar1[1] = 0x2b;
  }
  if ((int)uVar2 < 10) {
    puVar1[2] = 0x30;
    puVar1[3] = (char)uVar2 + '0';
    return puVar1 + 4;
  }
  if (99 < (int)uVar2) {
    puVar1[2] = (char)(uVar2 / 100) + '0';
    uVar2 = uVar2 % 100;
    puVar1[3] = (char)(uVar2 / 10) + '0';
    puVar1[4] = (char)uVar2 + (char)(uVar2 / 10) * -10 + '0';
    return puVar1 + 5;
  }
  puVar1[2] = (char)(uVar2 / 10) + '0';
  puVar1[3] = (char)uVar2 + (char)(uVar2 / 10) * -10 + '0';
  return puVar1 + 4;
}


