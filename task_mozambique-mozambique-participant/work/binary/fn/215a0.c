// ===== FUNC 215a0 size=169

void FUN_000215a0(long param_1,undefined8 *param_2)

{
  undefined8 *__src;
  undefined8 *puVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  
  puVar1 = *(undefined8 **)(param_1 + 8);
  if (puVar1 != *(undefined8 **)(param_1 + 0x10)) {
    __src = param_2 + 2;
    *puVar1 = puVar1 + 2;
    if ((undefined8 *)*param_2 == __src) {
      uVar3 = 0xffffffffffffffff;
      if (param_2[1] + 1 != 0) {
        memcpy(puVar1 + 2,__src,param_2[1] + 1);
        uVar3 = param_2[1];
      }
    }
    else {
      *puVar1 = (void *)*param_2;
      puVar1[2] = param_2[2];
      uVar3 = param_2[1];
    }
    puVar1[1] = uVar3;
    uVar3 = param_2[4];
    uVar2 = param_2[5];
    *param_2 = __src;
    param_2[1] = 0;
    *(undefined *)(param_2 + 2) = 0;
    *(undefined4 *)(puVar1 + 6) = *(undefined4 *)(param_2 + 6);
    puVar1[4] = uVar3;
    puVar1[5] = uVar2;
    *(long *)(param_1 + 8) = *(long *)(param_1 + 8) + 0x38;
    return;
  }
  FUN_00021260(param_1,puVar1,param_2);
  return;
}


