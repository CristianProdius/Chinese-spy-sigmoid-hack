// ===== FUNC 25220 size=2099

void FUN_00025220(long *param_1,long *param_2,char param_3)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  long lVar4;
  undefined2 uVar5;
  code *UNRECOVERED_JUMPTABLE;
  undefined8 uVar6;
  ulong uVar7;
  ulong uVar8;
  ulong uVar9;
  long lVar10;
  char *pcVar11;
  long *plVar12;
  ulong uVar13;
  uint uVar14;
  long in_FS_OFFSET;
  undefined8 local_a8;
  ulong local_a0;
  undefined8 local_88;
  ulong local_80;
  undefined *local_68;
  long local_60;
  undefined local_58 [24];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_2[1] != 0) {
    uVar8 = 0;
    uVar14 = 0;
    uVar9 = 0;
    lVar10 = 0;
    uVar7 = 0;
    uVar13 = 0;
LAB_000252c3:
    uVar5 = DAT_000e2db4;
    bVar2 = *(byte *)(*param_2 + uVar9);
    if ((char)uVar8 == '\0') {
      uVar14 = 0xffU >> ((&DAT_000e2220)[(uint)bVar2] & 0x1f) & (uint)bVar2;
    }
    else {
      uVar14 = uVar14 << 6 | bVar2 & 0x3f;
    }
    bVar1 = (&DAT_000e2220)[(ulong)(byte)(&DAT_000e2220)[(uint)bVar2] + (uVar8 + 0x10) * 0x10];
    uVar8 = (ulong)bVar1;
    if (bVar1 == 0) {
      if (0x22 < uVar14) {
        if (uVar14 == 0x5c) {
          *(undefined2 *)((long)param_1 + uVar13 + 0x5a) = DAT_000e2db0;
          uVar7 = uVar13 + 2;
        }
        else if ((uVar14 < 0x7f) || (param_3 == '\0')) {
LAB_000255a0:
          *(byte *)((long)param_1 + uVar13 + 0x5a) = bVar2;
          uVar7 = uVar13 + 1;
        }
        else {
          if (uVar14 < 0x10000) goto LAB_000255c0;
          __snprintf_chk((long)param_1 + uVar13 + 0x5a,0xd,2,0xffffffffffffffff,&DAT_000e069c,
                         (short)(uVar14 >> 10) + -0x2840,((ushort)uVar14 & 0x3ff) + 0xdc00);
          uVar7 = uVar13 + 0xc;
        }
        goto joined_r0x000254bd;
      }
      if (uVar14 < 8) {
LAB_000255c0:
        __snprintf_chk((long)param_1 + uVar13 + 0x5a,7,2,0xffffffffffffffff,"\\u%04x",uVar14);
        uVar7 = uVar13 + 6;
      }
      else {
        switch(uVar14) {
        case 8:
          *(undefined2 *)((long)param_1 + uVar13 + 0x5a) = DAT_000e2da4;
          uVar7 = uVar13 + 2;
          break;
        case 9:
          *(undefined2 *)((long)param_1 + uVar13 + 0x5a) = DAT_000e2da6;
          uVar7 = uVar13 + 2;
          break;
        case 10:
          *(undefined2 *)((long)param_1 + uVar13 + 0x5a) = DAT_000e2da8;
          uVar7 = uVar13 + 2;
          break;
        default:
          if (0x1f < uVar14) goto LAB_000255a0;
          goto LAB_000255c0;
        case 0xc:
          *(undefined2 *)((long)param_1 + uVar13 + 0x5a) = DAT_000e2daa;
          uVar7 = uVar13 + 2;
          break;
        case 0xd:
          *(undefined2 *)((long)param_1 + uVar13 + 0x5a) = DAT_000e2dac;
          uVar7 = uVar13 + 2;
          break;
        case 0x22:
          *(undefined2 *)((long)param_1 + uVar13 + 0x5a) = DAT_000e2dae;
          uVar7 = uVar13 + 2;
        }
      }
joined_r0x000254bd:
      if (0x200 - uVar7 < 0xd) {
        plVar12 = (long *)*param_1;
        if (*(code **)(*plVar12 + 8) == FUN_0001ac60) {
          if (0x3fffffffffffffffU - *(long *)(plVar12[1] + 8) < uVar7) goto LAB_000258af;
          FUN_000b2500(plVar12[1],(long)param_1 + 0x5a,uVar7);
          lVar10 = 0;
          uVar7 = 0;
          uVar13 = 0;
        }
        else {
          (**(code **)(*plVar12 + 8))(plVar12,(long)param_1 + 0x5a,uVar7);
          lVar10 = 0;
          uVar7 = 0;
          uVar13 = 0;
        }
      }
      else {
        lVar10 = 0;
        uVar13 = uVar7;
      }
    }
    else {
      if (bVar1 != 1) {
        if (param_3 == '\0') {
          *(byte *)((long)param_1 + uVar13 + 0x5a) = bVar2;
          uVar13 = uVar13 + 1;
        }
        lVar10 = lVar10 + 1;
        goto LAB_000252b9;
      }
      iVar3 = *(int *)(param_1 + 0x50);
      if (iVar3 == 0) {
        uVar6 = FUN_00040f40(0x20);
                    /* try { // try from 0002599e to 000259a2 has its CatchHandler @ 00025af0 */
        FUN_000251c0(&local_88,bVar2);
                    /* try { // try from 000259ae to 000259b2 has its CatchHandler @ 00025ae9 */
        FUN_0001bd50(&local_a8,uVar9);
        local_68 = local_58;
        local_60 = 0;
        local_58[0] = 0;
                    /* try { // try from 000259df to 00025a55 has its CatchHandler @ 00025aee */
        FUN_000b1110(&local_68,local_80 + local_a0 + 0x20);
        FUN_00017ba0(&local_68,"invalid UTF-8 byte at index ");
        if (0x3fffffffffffffffU - local_60 < local_a0) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00025aa0 to 00025aa4 has its CatchHandler @ 00025aee */
          FUN_00015e26("basic_string::append",local_a8);
        }
        FUN_000b2500(&local_68);
        FUN_00017ba0(&local_68,&DAT_000e06c6);
        if (0x3fffffffffffffffU - local_60 < local_80) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00025adf to 00025ae3 has its CatchHandler @ 00025aee */
          FUN_00015e26("basic_string::append",local_88);
        }
        FUN_000b2500(&local_68);
                    /* try { // try from 00025a61 to 00025a65 has its CatchHandler @ 00025ae4 */
        FUN_00013f05(uVar6,0x13c,&local_68);
        FUN_000b07c0(&local_68);
        FUN_000b07c0(&local_a8);
        FUN_000b07c0(&local_88);
                    /* WARNING: Subroutine does not return */
        FUN_00041f00(uVar6,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
      }
      if (1 < iVar3 - 1U) goto LAB_000252b9;
      uVar9 = (uVar9 - 1) + (ulong)(lVar10 == 0);
      if (iVar3 != 1) {
        uVar8 = 0;
        lVar10 = 0;
        uVar9 = uVar9 + 1;
        uVar13 = uVar7;
        if ((ulong)param_2[1] <= uVar9) goto LAB_00025328;
        goto LAB_000252c3;
      }
      if (param_3 == '\0') {
        *(undefined *)((long)param_1 + uVar7 + 0x5c) = 0xbd;
        *(undefined2 *)((long)param_1 + uVar7 + 0x5a) = uVar5;
        uVar7 = uVar7 + 3;
      }
      else {
        *(undefined4 *)((long)param_1 + uVar7 + 0x5a) = DAT_000e2f30;
        *(undefined2 *)((long)param_1 + uVar7 + 0x5e) = DAT_000e2db2;
        uVar7 = uVar7 + 6;
      }
      if (0xc < 0x200 - uVar7) {
        uVar8 = 0;
        lVar10 = 0;
        uVar13 = uVar7;
        goto LAB_000252b9;
      }
      plVar12 = (long *)*param_1;
      if (*(code **)(*plVar12 + 8) == FUN_0001ac60) {
        if (0x3fffffffffffffffU - *(long *)(plVar12[1] + 8) < uVar7) goto LAB_000258af;
        FUN_000b2500(plVar12[1],(long)param_1 + 0x5a,uVar7);
      }
      else {
        (**(code **)(*plVar12 + 8))(plVar12,(long)param_1 + 0x5a,uVar7);
      }
      uVar8 = 0;
      lVar10 = 0;
      uVar7 = 0;
      uVar13 = 0;
    }
LAB_000252b9:
    uVar9 = uVar9 + 1;
    if ((ulong)param_2[1] <= uVar9) goto LAB_00025328;
    goto LAB_000252c3;
  }
LAB_00025470:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_000258bb:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
LAB_00025328:
  if ((char)uVar8 == '\0') {
    if (uVar13 != 0) {
      plVar12 = (long *)*param_1;
      if (*(code **)(*plVar12 + 8) != FUN_0001ac60) {
        if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Could not recover jumptable at 0x0002576e. Too many branches */
                    /* WARNING: Treating indirect jump as call */
          (**(code **)(*plVar12 + 8))(plVar12,(long)param_1 + 0x5a,uVar13);
          return;
        }
        goto LAB_000258bb;
      }
      lVar10 = plVar12[1];
      if (0x3fffffffffffffffU - *(long *)(lVar10 + 8) < uVar13) {
LAB_000258af:
                    /* WARNING: Subroutine does not return */
        FUN_00015e26("basic_string::append");
      }
      lVar4 = *(long *)(in_FS_OFFSET + 0x28);
joined_r0x0002586c:
      if (local_40 == lVar4) {
        FUN_000b2500(lVar10,(long)param_1 + 0x5a,uVar13);
        return;
      }
      goto LAB_000258bb;
    }
  }
  else {
    iVar3 = *(int *)(param_1 + 0x50);
    if (iVar3 == 2) {
      plVar12 = (long *)*param_1;
      pcVar11 = (char *)((long)param_1 + 0x5a);
      UNRECOVERED_JUMPTABLE = *(code **)(*plVar12 + 8);
      if (UNRECOVERED_JUMPTABLE != FUN_0001ac60) {
        if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) goto LAB_00025733;
        goto LAB_000258bb;
      }
      lVar10 = plVar12[1];
      if (0x3fffffffffffffffU - *(long *)(lVar10 + 8) < uVar7) goto LAB_000258af;
      lVar4 = *(long *)(in_FS_OFFSET + 0x28);
      uVar13 = uVar7;
      goto joined_r0x0002586c;
    }
    if (iVar3 < 3) {
      if (iVar3 == 0) {
        uVar6 = FUN_00040f40(0x20);
                    /* try { // try from 000258e2 to 000258e6 has its CatchHandler @ 00025ab1 */
        FUN_000251c0(&local_88,*(undefined *)(*param_2 + -1 + param_2[1]));
        local_68 = local_58;
        local_58[0] = 0;
        local_60 = 0;
                    /* try { // try from 0002590e to 0002594b has its CatchHandler @ 00025a94 */
        FUN_000b1110(&local_68,local_80 + 0x26);
        FUN_00017ba0(&local_68,"incomplete UTF-8 string; last byte: 0x");
        if (0x3fffffffffffffffU - local_60 < local_80) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00025aac to 00025ab0 has its CatchHandler @ 00025a94 */
          FUN_00015e26("basic_string::append",local_88);
        }
        FUN_000b2500(&local_68);
                    /* try { // try from 00025957 to 0002595b has its CatchHandler @ 00025ab6 */
        FUN_00013f05(uVar6,0x13c,&local_68);
        FUN_000b07c0(&local_68);
        FUN_000b07c0(&local_88);
                    /* WARNING: Subroutine does not return */
        FUN_00041f00(uVar6,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
      }
      if (iVar3 == 1) {
        plVar12 = (long *)*param_1;
        if (*(code **)(*plVar12 + 8) == FUN_0001ac60) {
          if (0x3fffffffffffffffU - *(long *)(plVar12[1] + 8) < uVar7) goto LAB_000258af;
          FUN_000b2500(plVar12[1],(long)param_1 + 0x5a,uVar7);
        }
        else {
          (**(code **)(*plVar12 + 8))(plVar12,(long)param_1 + 0x5a,uVar7);
        }
        plVar12 = (long *)*param_1;
        UNRECOVERED_JUMPTABLE = *(code **)(*plVar12 + 8);
        if (param_3 == '\0') {
          if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
            uVar7 = 3;
            pcVar11 = &DAT_000e06d2;
            goto LAB_00025733;
          }
        }
        else if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
          uVar7 = 6;
          pcVar11 = "\\ufffd";
LAB_00025733:
                    /* WARNING: Could not recover jumptable at 0x00025744. Too many branches */
                    /* WARNING: Treating indirect jump as call */
          (*UNRECOVERED_JUMPTABLE)(plVar12,pcVar11,uVar7);
          return;
        }
        goto LAB_000258bb;
      }
    }
  }
  goto LAB_00025470;
}


