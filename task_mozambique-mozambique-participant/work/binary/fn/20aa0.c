// ===== FUNC 20aa0 size=756

void FUN_00020aa0(long *param_1,long param_2)

{
  undefined8 uVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  undefined8 uVar5;
  ulong uVar6;
  ulong uVar7;
  ulong uVar8;
  long lVar9;
  long lVar10;
  long lVar11;
  long local_50;
  long local_40;
  
  lVar2 = param_1[1];
  lVar3 = *param_1;
  uVar6 = (lVar2 - lVar3 >> 4) * -0x5555555555555555;
  if (uVar6 == 0x2aaaaaaaaaaaaaa) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("vector::_M_realloc_insert");
  }
  uVar8 = 1;
  if (lVar3 != lVar2) {
    uVar8 = uVar6;
  }
  uVar7 = uVar6 + uVar8;
  if (CARRY8(uVar6,uVar8) == false) {
    if (uVar7 == 0) {
      local_40 = 0;
      lVar9 = 0x30;
      local_50 = 0;
      goto LAB_00020b34;
    }
    if (0x2aaaaaaaaaaaaaa < uVar7) {
      uVar7 = 0x2aaaaaaaaaaaaaa;
    }
    local_40 = uVar7 * 0x30;
  }
  else {
    local_40 = 0x7fffffffffffffe0;
  }
  local_50 = FUN_00041fe0(local_40);
  local_40 = local_50 + local_40;
  lVar9 = local_50 + 0x30;
LAB_00020b34:
  lVar10 = local_50 + (param_2 - lVar3);
  *(undefined4 *)(lVar10 + 8) = 0;
  *(undefined8 *)(lVar10 + 0x10) = 0;
  *(long *)(lVar10 + 0x18) = lVar10 + 8;
  *(long *)(lVar10 + 0x20) = lVar10 + 8;
  *(undefined8 *)(lVar10 + 0x28) = 0;
  lVar10 = local_50;
  lVar11 = lVar3;
  if (param_2 == lVar3) goto LAB_00020d13;
  while( true ) {
    lVar4 = *(long *)(lVar11 + 0x10);
    lVar9 = lVar10 + 8;
    if (lVar4 == 0) {
      *(undefined8 *)(lVar10 + 0x10) = 0;
      *(long *)(lVar10 + 0x18) = lVar9;
      *(long *)(lVar10 + 0x20) = lVar9;
      lVar9 = *(long *)(lVar11 + 0x10);
      *(undefined4 *)(lVar10 + 8) = 0;
      *(undefined8 *)(lVar10 + 0x28) = 0;
      while (lVar9 != 0) {
        FUN_00018460(*(undefined8 *)(lVar9 + 0x18));
        lVar4 = *(long *)(lVar9 + 0x10);
        if (*(long *)(lVar9 + 0x20) != lVar9 + 0x30) {
          thunk_FUN_000d36e0(*(long *)(lVar9 + 0x20),*(long *)(lVar9 + 0x30) + 1);
        }
        thunk_FUN_000d36e0(lVar9,0x40);
        lVar9 = lVar4;
      }
    }
    else {
      uVar1 = *(undefined8 *)(lVar11 + 0x18);
      *(undefined4 *)(lVar10 + 8) = *(undefined4 *)(lVar11 + 8);
      uVar5 = *(undefined8 *)(lVar11 + 0x20);
      *(long *)(lVar10 + 0x10) = lVar4;
      *(undefined8 *)(lVar10 + 0x18) = uVar1;
      *(undefined8 *)(lVar10 + 0x20) = uVar5;
      *(long *)(lVar4 + 8) = lVar9;
      *(undefined8 *)(lVar11 + 0x10) = 0;
      *(undefined8 *)(lVar10 + 0x28) = *(undefined8 *)(lVar11 + 0x28);
      *(long *)(lVar11 + 0x18) = lVar11 + 8;
      *(long *)(lVar11 + 0x20) = lVar11 + 8;
      *(undefined8 *)(lVar11 + 0x28) = 0;
    }
    if (lVar11 + 0x30 == param_2) break;
    lVar10 = lVar10 + 0x30;
    lVar11 = lVar11 + 0x30;
  }
  lVar9 = lVar10 + 0x60;
  if (param_2 != lVar2) {
    do {
      lVar11 = *(long *)(param_2 + 0x10);
      lVar10 = lVar9 + 8;
      if (lVar11 == 0) {
        *(undefined4 *)(lVar9 + 8) = 0;
        *(undefined8 *)(lVar9 + 0x10) = 0;
        *(long *)(lVar9 + 0x18) = lVar10;
        *(long *)(lVar9 + 0x20) = lVar10;
        *(undefined8 *)(lVar9 + 0x28) = 0;
      }
      else {
        uVar1 = *(undefined8 *)(param_2 + 0x18);
        *(undefined4 *)(lVar9 + 8) = *(undefined4 *)(param_2 + 8);
        uVar5 = *(undefined8 *)(param_2 + 0x20);
        *(long *)(lVar9 + 0x10) = lVar11;
        *(undefined8 *)(lVar9 + 0x18) = uVar1;
        *(undefined8 *)(lVar9 + 0x20) = uVar5;
        *(long *)(lVar11 + 8) = lVar10;
        *(undefined8 *)(param_2 + 0x10) = 0;
        *(undefined8 *)(lVar9 + 0x28) = *(undefined8 *)(param_2 + 0x28);
        *(long *)(param_2 + 0x18) = param_2 + 8;
        *(long *)(param_2 + 0x20) = param_2 + 8;
        *(undefined8 *)(param_2 + 0x28) = 0;
      }
      param_2 = param_2 + 0x30;
      lVar9 = lVar9 + 0x30;
LAB_00020d13:
    } while (param_2 != lVar2);
  }
  if (lVar3 != 0) {
    thunk_FUN_000d36e0(lVar3,param_1[2] - lVar3);
  }
  *param_1 = local_50;
  param_1[1] = lVar9;
  param_1[2] = local_40;
  return;
}


