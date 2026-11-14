// ===== FUNC 2bf10 size=1761

void FUN_0002bf10(long *param_1,long param_2,long param_3,undefined8 param_4,undefined8 param_5,
                 undefined8 param_6)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  long *plVar5;
  char cVar6;
  long lVar7;
  long lVar8;
  int iVar9;
  ulong uVar10;
  long *plVar11;
  char *pcVar12;
  long *plVar13;
  long lVar14;
  long *plVar15;
  long lVar16;
  long in_FS_OFFSET;
  long *local_228;
  undefined4 local_20c;
  undefined local_208 [16];
  long *local_1f8;
  undefined local_1e8 [8];
  undefined4 *puStack_1e0;
  long local_1d8;
  undefined local_1c8 [16];
  undefined local_1b8 [16];
  undefined local_1a8 [16];
  undefined8 local_198;
  undefined local_188 [16];
  long local_178 [2];
  long local_168;
  int local_68;
  char local_64;
  long *local_60;
  long *local_58;
  long local_50;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  if ((*(char *)(param_2 + 0x124) != '\0') &&
     ((*(char *)(*param_1 + 0x140) == '\0' ||
      (*(int *)(param_2 + 0x120) < *(int *)(*param_1 + 0x120))))) {
    lVar14 = *(long *)param_1[1];
    if (param_3 == ((long *)param_1[1])[1] - lVar14 >> 2) {
      FUN_00026a00(local_188,param_2);
                    /* try { // try from 0002c43e to 0002c552 has its CatchHandler @ 0002c60b */
      FUN_0001a1c0(param_1[4],local_188,*(undefined4 *)param_1[2],*(undefined4 *)param_1[3]);
      lVar14 = 0;
      if (*(char *)param_1[5] != '\0') {
        do {
          if (*(int *)(param_1[6] + lVar14 * 4) != 0) {
            lVar16 = param_1[4];
            local_1a8 = ZEXT816(0xffffffff00000000);
            local_198 = 0xffffffff;
            local_1c8 = (undefined  [16])0x0;
            local_1b8 = (undefined  [16])0x0;
            FUN_00018b10(local_1c8,"unload");
            local_1a8._8_4_ = (int)lVar14;
            local_1a8._0_4_ = *(undefined4 *)param_1[2];
            local_1a8._12_4_ = *(undefined4 *)(param_1[6] + lVar14 * 4);
                    /* try { // try from 0002c582 to 0002c586 has its CatchHandler @ 0002c5fc */
            FUN_00019ec0(lVar16,local_188,local_1c8,0);
            FUN_000b07c0(local_1c8);
          }
          lVar14 = lVar14 + 1;
        } while (lVar14 != 3);
      }
      if (local_64 != '\0') {
        lVar14 = *param_1;
        if (*(char *)(lVar14 + 0x140) == '\0') {
          FUN_0001c620(lVar14,local_188);
          *(undefined *)(lVar14 + 0x140) = 1;
        }
        else if (local_68 < *(int *)(lVar14 + 0x120)) {
          FUN_00018bf0(lVar14,local_188);
        }
      }
      FUN_0001cf40(&local_60);
      FUN_0001cb50(local_178);
    }
    else {
      pcVar12 = (char *)param_1[5];
      plVar11 = (long *)0x0;
      local_1f8 = (long *)0x0;
      iVar9 = 0;
      iVar2 = *(int *)(lVar14 + param_3 * 4);
      lVar16 = (long)iVar2;
      local_208 = (undefined  [16])0x0;
      local_228 = (long *)0x0;
      cVar6 = *pcVar12;
      lVar14 = param_2 + lVar16 * 4;
      do {
        while (((cVar6 != '\0' && (*(int *)param_1[3] == iVar9)) ||
               (*(int *)(lVar14 + 0x28) < *(int *)(param_1[7] + lVar16 * 4)))) {
          iVar9 = iVar9 + 1;
          lVar14 = lVar14 + 0xc;
          if (iVar9 == 10) goto LAB_0002c02c;
        }
        local_1e8[4] = 1;
        local_1e8._0_4_ = iVar9;
        if (local_228 == plVar11) {
                    /* try { // try from 0002c3f4 to 0002c3f8 has its CatchHandler @ 0002c601 */
          FUN_00022530(local_208,local_228,local_1e8);
          local_228 = local_1f8;
          pcVar12 = (char *)param_1[5];
          plVar11 = (long *)local_208._8_8_;
        }
        else {
          *plVar11 = (long)local_1e8;
          local_208._8_8_ = plVar11 + 1;
          plVar11 = plVar11 + 1;
        }
        iVar9 = iVar9 + 1;
        cVar6 = *pcVar12;
        lVar14 = lVar14 + 0xc;
      } while (iVar9 != 10);
LAB_0002c02c:
      lVar14 = param_1[4];
      lVar8 = 0;
      while( true ) {
        if (((cVar6 == '\0') || (*(uint *)param_1[3] != (uint)lVar8)) &&
           ((*(int *)(lVar14 + 0x18 + lVar8 * 4) == iVar2 &&
            (*(int *)(param_1[7] + lVar16 * 4) <= *(int *)(param_2 + 0xd8 + lVar8 * 4))))) {
          local_1e8[4] = 0;
          local_1e8._0_4_ = (uint)lVar8;
          if (local_228 == plVar11) {
                    /* try { // try from 0002c5a3 to 0002c5a7 has its CatchHandler @ 0002c601 */
            FUN_00022530(local_208,local_228,local_1e8);
            lVar14 = param_1[4];
            plVar11 = (long *)local_208._8_8_;
            local_228 = local_1f8;
          }
          else {
            *plVar11 = (long)local_1e8;
            local_208._8_8_ = plVar11 + 1;
            plVar11 = plVar11 + 1;
          }
        }
        if (lVar8 == 9) break;
        lVar8 = lVar8 + 1;
        cVar6 = *(char *)param_1[5];
      }
      puVar1 = (undefined4 *)(*(long *)(param_2 + 0x10) + (long)*(int *)param_1[2] * 0x18);
      local_20c = puVar1[1];
      if (puVar1[2] == 0) {
        local_20c = *puVar1;
      }
      uVar4 = local_208._0_8_;
      puStack_1e0 = &local_20c;
      local_1d8 = param_1[3];
      local_1e8 = (undefined  [8])lVar14;
      if (plVar11 != (long *)local_208._0_8_) {
        uVar10 = (long)plVar11 - local_208._0_8_;
        lVar14 = (((long)uVar10 >> 3) + 1) / 2;
        if ((long)uVar10 < 1) {
LAB_0002c4c1:
          lVar8 = 0;
          FUN_0002aaf0(uVar4,plVar11);
          lVar7 = 0;
        }
        else {
          while( true ) {
            lVar8 = lVar14 * 8;
            lVar7 = FUN_00042020(lVar8,&DAT_000e30f8);
            if (lVar7 != 0) break;
            if (lVar14 == 1) goto LAB_0002c4c1;
            lVar14 = lVar14 + 1 >> 1;
          }
          FUN_0002bdd0(uVar4,plVar11,lVar7,lVar14,param_5,param_6,local_1e8,puStack_1e0,local_1d8);
        }
        thunk_FUN_000d36e0(lVar7,lVar8);
        plVar13 = plVar11;
        if ((0x28 < uVar10) && (plVar13 = (long *)(uVar4 + 0x28), plVar11 != plVar13)) {
          local_208._8_8_ = plVar13;
        }
        plVar11 = (long *)uVar4;
        do {
          uVar3 = *(undefined4 *)plVar11;
          cVar6 = *(char *)((long)plVar11 + 4);
                    /* try { // try from 0002c1fb to 0002c1ff has its CatchHandler @ 0002c601 */
          FUN_00026a00(local_188,param_2);
                    /* try { // try from 0002c212 to 0002c295 has its CatchHandler @ 0002c606 */
          FUN_0001a1c0(param_1[4],local_188,*(undefined4 *)param_1[2],uVar3);
          lVar14 = param_1[4];
          lVar8 = 6;
          pcVar12 = "gather";
          local_198 = 0xffffffff;
          local_1a8 = ZEXT816(0xffffffff00000000);
          local_1c8._8_8_ = 0;
          local_1c8._0_8_ = local_1b8;
          local_1b8 = (undefined  [16])0x0;
          if (cVar6 != '\0') {
            lVar8 = 4;
            pcVar12 = "load";
          }
          FUN_00017bf0(local_1c8,pcVar12,pcVar12 + lVar8);
          local_1a8._0_4_ = *(undefined4 *)param_1[2];
          local_1a8._8_4_ = iVar2;
          local_1a8._12_4_ = *(undefined4 *)(param_1[7] + lVar16 * 4);
                    /* try { // try from 0002c2ca to 0002c2ce has its CatchHandler @ 0002c610 */
          FUN_00019ec0(lVar14,local_188,local_1c8,0);
          if ((undefined *)local_1c8._0_8_ != local_1b8) {
            thunk_FUN_000d36e0(local_1c8._0_8_,local_1b8._0_8_ + 1);
          }
          lVar14 = param_1[8];
          local_1e8 = (undefined  [8])(param_3 + 1);
          if (*(long *)(lVar14 + 0x10) == 0) {
                    /* try { // try from 0002c5d9 to 0002c5dd has its CatchHandler @ 0002c606 */
            FUN_00016056();
            goto LAB_0002c5de;
          }
                    /* try { // try from 0002c31c to 0002c31e has its CatchHandler @ 0002c606 */
          (**(code **)(lVar14 + 0x18))(lVar14,local_188,local_1e8);
          plVar5 = local_58;
          for (plVar15 = local_60; plVar5 != plVar15; plVar15 = plVar15 + 7) {
            if ((long *)*plVar15 != plVar15 + 2) {
              thunk_FUN_000d36e0((long *)*plVar15,plVar15[2] + 1);
            }
          }
          if (local_60 != (long *)0x0) {
            thunk_FUN_000d36e0(local_60,local_50 - (long)local_60);
          }
          if (local_178[0] != 0) {
            thunk_FUN_000d36e0(local_178[0],local_168 - local_178[0]);
          }
          plVar11 = plVar11 + 1;
        } while (plVar13 != plVar11);
      }
      if ((long *)uVar4 != (long *)0x0) {
        thunk_FUN_000d36e0(uVar4,(long)local_228 - uVar4);
      }
    }
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
LAB_0002c5de:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


