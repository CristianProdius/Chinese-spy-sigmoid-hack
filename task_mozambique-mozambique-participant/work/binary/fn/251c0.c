// ===== FUNC 251c0 size=81

long * FUN_000251c0(long *param_1,uint param_2)

{
  char cVar1;
  
  *param_1 = (long)(param_1 + 2);
  FUN_00017bf0(param_1,&DAT_000e0688);
  cVar1 = "0123456789ABCDEF"[param_2 & 0xf];
  *(char *)*param_1 = "0123456789ABCDEF"[(byte)((byte)param_2 >> 4)];
  *(char *)(*param_1 + 1) = cVar1;
  return param_1;
}


