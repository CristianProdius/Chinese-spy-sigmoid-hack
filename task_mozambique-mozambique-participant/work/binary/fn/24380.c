// ===== FUNC 24380 size=89

void FUN_00024380(long param_1,char param_2)

{
  int iVar1;
  ulong *puVar2;
  ulong uVar3;
  ulong uVar4;
  
  puVar2 = *(ulong **)(param_1 + 0x10);
  iVar1 = *(int *)(param_1 + 0x18);
  if (puVar2 != *(ulong **)(param_1 + 0x20)) {
    if (iVar1 == 0x3f) {
      *(undefined4 *)(param_1 + 0x18) = 0;
      *(ulong **)(param_1 + 0x10) = puVar2 + 1;
    }
    else {
      *(int *)(param_1 + 0x18) = iVar1 + 1;
    }
    uVar3 = 1L << ((byte)iVar1 & 0x3f);
    uVar4 = ~uVar3 & *puVar2;
    if (param_2 != '\0') {
      uVar4 = uVar3 | *puVar2;
    }
    *puVar2 = uVar4;
    return;
  }
  FUN_00018750(param_1,puVar2,iVar1,param_2);
  return;
}


