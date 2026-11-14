// ===== FUNC 2bdd0 size=303

void FUN_0002bdd0(long param_1,long param_2,undefined8 param_3,long param_4,undefined8 param_5,
                 undefined8 param_6,undefined8 param_7,undefined8 param_8_00,undefined8 param_8)

{
  long lVar1;
  long lVar2;
  long lVar3;
  
  lVar3 = ((param_2 - param_1 >> 3) + 1) / 2;
  lVar2 = lVar3 * 8;
  lVar1 = param_1 + lVar2;
  if (param_4 < lVar3) {
    FUN_0002bdd0(param_1,lVar1,param_3);
    FUN_0002bdd0(lVar1,param_2,param_3,param_4);
  }
  else {
    FUN_0002bb00(param_1,lVar1,param_3);
    FUN_0002bb00(lVar1,param_2,param_3);
  }
  FUN_0002aca0(param_1,lVar1,param_2,lVar2 >> 3,param_2 - lVar1 >> 3,param_3,param_4,param_7,
               param_8_00,param_8);
  return;
}


