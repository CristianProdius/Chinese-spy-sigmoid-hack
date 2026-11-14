// ===== FUNC 3ad40 size=216

void FUN_0003ad40(long param_1,long param_2,undefined8 param_3,long param_4)

{
  long lVar1;
  long lVar2;
  long lVar3;
  
  lVar2 = ((param_2 - param_1 >> 5) * 0x2e8ba2e8ba2e8ba3 + 1) / 2;
  lVar3 = lVar2 * 0x160;
  lVar1 = param_1 + lVar3;
  if (param_4 < lVar2) {
    FUN_0003ad40(param_1,lVar1,param_3);
    FUN_0003ad40(lVar1,param_2,param_3,param_4);
  }
  else {
    FUN_00039d80(param_1,lVar1,param_3);
    FUN_00039d80(lVar1,param_2,param_3);
  }
  FUN_0003a010(param_1,lVar1,param_2,(lVar3 >> 5) * 0x2e8ba2e8ba2e8ba3,
               (param_2 - lVar1 >> 5) * 0x2e8ba2e8ba2e8ba3,param_3,param_4);
  return;
}


