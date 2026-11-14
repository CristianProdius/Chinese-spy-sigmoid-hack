// ===== FUNC 1ae00 size=106

void FUN_0001ae00(long param_1,undefined param_2)

{
  long *plVar1;
  long lVar2;
  long *plVar3;
  ulong uVar4;
  
  plVar1 = *(long **)(param_1 + 8);
  lVar2 = plVar1[1];
  plVar3 = (long *)*plVar1;
  if (plVar3 == plVar1 + 2) {
    uVar4 = 0xf;
  }
  else {
    uVar4 = plVar1[2];
  }
  if (uVar4 < lVar2 + 1U) {
    FUN_000b0b90(plVar1,lVar2,0,0,1);
    plVar3 = (long *)*plVar1;
  }
  *(undefined *)((long)plVar3 + lVar2) = param_2;
  plVar1[1] = lVar2 + 1U;
  *(undefined *)(*plVar1 + 1 + lVar2) = 0;
  return;
}


