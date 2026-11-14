// ===== FUNC 24620 size=1171

void FUN_00024620(long *param_1,byte param_2)

{
  undefined8 *puVar1;
  undefined uVar2;
  undefined8 *puVar3;
  undefined8 *puVar4;
  long lVar5;
  undefined *puVar6;
  undefined *puVar7;
  undefined *puVar8;
  undefined *puVar9;
  long *plVar10;
  undefined8 uVar11;
  long lVar12;
  long in_FS_OFFSET;
  char local_68;
  undefined8 *puStack_60;
  undefined local_58 [16];
  long local_48;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_2 == 1) {
    if (*param_1 == 0) goto LAB_00024820;
    local_48 = 0;
    local_58 = (undefined  [16])0x0;
                    /* try { // try from 0002486e to 0002489b has its CatchHandler @ 00024adb */
    FUN_00024550(local_58,*(undefined8 *)(*param_1 + 0x28));
    lVar5 = *param_1;
    for (lVar12 = *(long *)(lVar5 + 0x18); lVar5 + 8 != lVar12; lVar12 = FUN_00049c90(lVar12)) {
      FUN_000182f0(local_58,lVar12 + 0x40);
    }
    if (local_58._0_8_ != local_58._8_8_) goto LAB_000246e5;
    lVar5 = local_58._8_8_;
    if (local_58._8_8_ != 0) goto LAB_000248cd;
LAB_000248ea:
    if (param_2 < 3) {
      if (param_2 == 1) {
        FUN_0001a410(*(undefined8 *)(*param_1 + 0x10));
        if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
          uVar11 = 0x30;
          plVar10 = (long *)*param_1;
          goto LAB_0002492c;
        }
        goto LAB_00024ad6;
      }
    }
    else {
      if (param_2 == 3) {
        lVar5 = *param_1;
LAB_00024a01:
        FUN_000b07c0(lVar5);
        if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
          uVar11 = 0x20;
          plVar10 = (long *)*param_1;
LAB_0002492c:
          thunk_FUN_000d36e0(plVar10,uVar11);
          return;
        }
        goto LAB_00024ad6;
      }
      if (param_2 == 8) {
        plVar10 = (long *)*param_1;
        goto LAB_000247dd;
      }
    }
  }
  else {
    if (param_2 == 2) {
      plVar10 = (long *)*param_1;
      if (plVar10 == (long *)0x0) goto LAB_00024820;
      local_58 = (undefined  [16])0x0;
      local_48 = 0;
                    /* try { // try from 00024690 to 000246ca has its CatchHandler @ 00024adb */
      FUN_00024550(local_58,plVar10[1] - *plVar10 >> 4);
      plVar10 = (long *)*param_1;
      lVar5 = *plVar10;
      lVar12 = plVar10[1] - lVar5 >> 4;
      if (plVar10[1] - lVar5 < 1) {
        if (local_58._0_8_ != local_58._8_8_) goto LAB_000246e5;
        lVar5 = local_58._8_8_;
        if (local_58._8_8_ != 0) goto LAB_000248cd;
      }
      else {
        do {
          FUN_000182f0(local_58,lVar5);
          lVar5 = lVar5 + 0x10;
          lVar12 = lVar12 + -1;
        } while (lVar12 != 0);
        if (local_58._0_8_ == local_58._8_8_) {
          lVar5 = local_58._8_8_;
          if (local_58._8_8_ != 0) goto LAB_000248cd;
        }
        else {
LAB_000246e5:
          lVar12 = local_58._8_8_;
          do {
            uVar11 = *(undefined8 *)(lVar12 + -0x10);
            puStack_60 = *(undefined8 **)(lVar12 + -8);
            lVar5 = lVar12 + -0x10;
            *(undefined *)(lVar12 + -0x10) = 0;
            *(undefined8 *)(lVar12 + -8) = 0;
            local_58._8_8_ = lVar5;
            FUN_00024620(lVar12 + -8,0);
            puVar3 = puStack_60;
            local_68 = (char)uVar11;
            if (local_68 == '\x02') {
              puVar7 = (undefined *)puStack_60[1];
              puVar6 = (undefined *)*puStack_60;
              lVar12 = (long)puVar7 - (long)puVar6 >> 4;
              if (0 < (long)puVar7 - (long)puVar6) {
                do {
                    /* try { // try from 00024996 to 0002499a has its CatchHandler @ 00024ae0 */
                  FUN_000182f0(local_58,puVar6);
                  puVar6 = puVar6 + 0x10;
                  lVar12 = lVar12 + -1;
                } while (lVar12 != 0);
                puVar6 = (undefined *)*puVar3;
                puVar7 = (undefined *)puVar3[1];
                lVar5 = local_58._8_8_;
              }
              puVar8 = puVar6;
              if (puVar7 != puVar6) {
                do {
                  puVar9 = puVar8 + 0x10;
                  FUN_00024620(puVar8 + 8,*puVar8);
                  puVar8 = puVar9;
                } while (puVar7 != puVar9);
                puVar3[1] = puVar6;
              }
            }
            else if (local_68 == '\x01') {
              puVar4 = (undefined8 *)puStack_60[3];
              puVar1 = puStack_60 + 1;
              if (puVar1 != puVar4) {
                do {
                    /* try { // try from 0002477f to 00024783 has its CatchHandler @ 00024ae0 */
                  FUN_000182f0(local_58,puVar4 + 8);
                  puVar4 = (undefined8 *)FUN_00049c90(puVar4);
                } while (puVar1 != puVar4);
                lVar5 = local_58._8_8_;
              }
              FUN_0001a410(puVar3[2]);
              puVar3[2] = 0;
              puVar3[3] = puVar1;
              puVar3[4] = puVar1;
              puVar3[5] = 0;
            }
            FUN_00024620(&puStack_60,local_68);
            lVar12 = lVar5;
          } while (local_58._0_8_ != lVar5);
          if (lVar5 != 0) {
LAB_000248cd:
            thunk_FUN_000d36e0(lVar5,local_48 - lVar5);
          }
          if (param_2 != 2) goto LAB_000248ea;
        }
        plVar10 = (long *)*param_1;
      }
      puVar6 = (undefined *)plVar10[1];
      puVar7 = (undefined *)*plVar10;
      if (puVar6 != puVar7) {
        do {
          uVar2 = *puVar7;
          puVar8 = puVar7 + 8;
          puVar7 = puVar7 + 0x10;
          FUN_00024620(puVar8,uVar2);
        } while (puVar6 != puVar7);
        puVar7 = (undefined *)*plVar10;
      }
      if (puVar7 != (undefined *)0x0) {
        thunk_FUN_000d36e0(puVar7,plVar10[2] - (long)puVar7);
      }
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        uVar11 = 0x18;
        plVar10 = (long *)*param_1;
        goto LAB_0002492c;
      }
      goto LAB_00024ad6;
    }
    if (param_2 == 3) {
      lVar5 = *param_1;
      if (lVar5 != 0) goto LAB_00024a01;
    }
    else if ((param_2 == 8) && (plVar10 = (long *)*param_1, plVar10 != (long *)0x0)) {
LAB_000247dd:
      lVar5 = *plVar10;
      if (lVar5 != 0) {
        thunk_FUN_000d36e0(lVar5,plVar10[2] - lVar5);
        plVar10 = (long *)*param_1;
      }
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        uVar11 = 0x28;
        goto LAB_0002492c;
      }
      goto LAB_00024ad6;
    }
  }
LAB_00024820:
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_00024ad6:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


