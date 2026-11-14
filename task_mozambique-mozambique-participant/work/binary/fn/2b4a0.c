// ===== FUNC 2b4a0 size=510

undefined8 FUN_0002b4a0(long param_1,ulong param_2)

{
  int iVar1;
  ulong *puVar2;
  undefined8 *puVar3;
  char cVar4;
  ulong uVar5;
  undefined8 uVar6;
  ulong uVar7;
  char *extraout_RDX;
  char *pcVar8;
  long in_FS_OFFSET;
  undefined local_89;
  undefined4 local_88 [2];
  char *local_80;
  undefined local_78 [32];
  undefined local_58 [40];
  long local_30;
  
  local_30 = *(long *)(in_FS_OFFSET + 0x28);
  local_89 = 2;
  local_88[0] = (undefined4)(*(long *)(param_1 + 0x10) - *(long *)(param_1 + 8) >> 3);
  if (*(long *)(param_1 + 0x90) == 0) {
    uVar6 = FUN_00016056();
                    /* catch() { ... } // from try @ 0002b639 with catch @ 0002b695 */
    FUN_00040fa0();
                    /* WARNING: Subroutine does not return */
    FUN_000ddde0(uVar6);
  }
  cVar4 = (**(code **)(param_1 + 0x98))(param_1 + 0x80,local_88,&local_89,param_1 + 0xa8);
  puVar2 = *(ulong **)(param_1 + 0x30);
  if (puVar2 == *(ulong **)(param_1 + 0x40)) {
    FUN_00018750(param_1 + 0x20,puVar2,*(undefined4 *)(param_1 + 0x38),cVar4);
  }
  else {
    iVar1 = *(int *)(param_1 + 0x38);
    if (iVar1 == 0x3f) {
      *(undefined4 *)(param_1 + 0x38) = 0;
      *(ulong **)(param_1 + 0x30) = puVar2 + 1;
    }
    else {
      *(int *)(param_1 + 0x38) = iVar1 + 1;
    }
    uVar7 = 1L << ((byte)iVar1 & 0x3f);
    uVar5 = ~uVar7 & *puVar2;
    if (cVar4 != '\0') {
      uVar5 = uVar7 | *puVar2;
    }
    *puVar2 = uVar5;
  }
  local_89 = 2;
  local_88[0] = FUN_0002b090(param_1,&local_89,1);
  puVar3 = *(undefined8 **)(param_1 + 0x10);
  local_80 = extraout_RDX;
  if (puVar3 == *(undefined8 **)(param_1 + 0x18)) {
    FUN_0002b330(param_1 + 8,puVar3,&local_80);
    pcVar8 = *(char **)(*(long *)(param_1 + 0x10) + -8);
  }
  else {
    *puVar3 = extraout_RDX;
    *(undefined8 **)(param_1 + 0x10) = puVar3 + 1;
    pcVar8 = extraout_RDX;
  }
  if ((param_2 != 0xffffffffffffffff) && (pcVar8 != (char *)0x0)) {
    uVar5 = 0x199999999999999;
    cVar4 = *pcVar8;
    if ((cVar4 != '\x01') && (uVar5 = 0x7ffffffffffffff, cVar4 != '\x02')) {
      uVar5 = (ulong)(cVar4 != '\0');
    }
    if (uVar5 < param_2) {
      uVar6 = FUN_00040f40(0x20);
                    /* try { // try from 0002b639 to 0002b63d has its CatchHandler @ 0002b695 */
      FUN_0001bd50(local_78,param_2);
                    /* try { // try from 0002b650 to 0002b654 has its CatchHandler @ 0002b69f */
      FUN_000260a0(local_58,"excessive array size: ",local_78);
                    /* try { // try from 0002b660 to 0002b664 has its CatchHandler @ 0002b69a */
      FUN_00013a77(uVar6,0x198,local_58);
      FUN_000b07c0(local_58);
      FUN_000b07c0(local_78);
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(uVar6,&PTR_PTR_FUN_0011cc88,FUN_0001aa50);
    }
  }
  if (local_30 == *(long *)(in_FS_OFFSET + 0x28)) {
    return 1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


