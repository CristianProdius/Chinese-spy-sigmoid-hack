// ===== FUNC 21660 size=2061

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined (*) [16]
FUN_00021660(undefined (*param_1) [16],long param_2,int *param_3,long param_4,long param_5,
            int param_6)

{
  int *piVar1;
  int iVar2;
  undefined auVar3 [16];
  undefined auVar4 [16];
  undefined auVar5 [16];
  ulong uVar6;
  undefined8 uVar7;
  undefined (*pauVar8) [16];
  long lVar9;
  ulong uVar10;
  int iVar11;
  long lVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int *piVar16;
  undefined4 uVar17;
  int *piVar18;
  long in_FS_OFFSET;
  int *local_c8;
  long local_b8;
  undefined local_78 [16];
  undefined local_68 [16];
  undefined local_58 [16];
  undefined8 local_48;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  *(undefined8 *)param_1[1] = 0;
  *param_1 = (undefined  [16])0x0;
  pauVar8 = (undefined (*) [16])FUN_00041fe0(0x38);
  *(undefined **)param_1[1] = pauVar8[3] + 8;
  *(undefined (**) [16])*param_1 = pauVar8;
  *(undefined (**) [16])(*param_1 + 8) = pauVar8;
  *pauVar8 = (undefined  [16])0x0;
  pauVar8[1] = (undefined  [16])0x0;
  pauVar8[2] = (undefined  [16])0x0;
  *(undefined8 *)pauVar8[3] = 0;
  *(undefined (**) [16])*pauVar8 = pauVar8 + 1;
                    /* try { // try from 00021704 to 00021708 has its CatchHandler @ 00021e83 */
  FUN_00017bf0(pauVar8,&DAT_000e0454);
  lVar12 = *(long *)(param_3 + 6);
  lVar9 = *(long *)(param_3 + 4);
  *(undefined **)(*param_1 + 8) = pauVar8[3] + 8;
  uVar7 = _UNK_000e2e88;
  uVar6 = DAT_000e2e80;
  *(undefined4 *)pauVar8[3] = 0xffffffff;
  local_b8 = 0;
  uVar10 = lVar12 - lVar9;
  *(ulong *)pauVar8[2] = uVar6;
  *(undefined8 *)(pauVar8[2] + 8) = uVar7;
  if (0 < (int)((long)uVar10 >> 3) * -0x55555555) {
    do {
      piVar1 = (int *)(lVar9 + local_b8 * 0x18);
      if (piVar1[2] == 0) {
        iVar2 = *piVar1;
        lVar12 = 0;
        iVar11 = 3 - (piVar1[4] + piVar1[3] + piVar1[5]);
        lVar9 = (long)iVar2;
        do {
          while (uVar17 = (undefined4)local_b8,
                *(int *)(param_2 + 0x34 + lVar9 * 0x28 + lVar12 * 4) == 0) {
LAB_000217d0:
            lVar12 = lVar12 + 1;
            if (lVar12 == 10) goto LAB_00021880;
          }
          local_58._0_12_ = ZEXT412(0xffffffff) << 0x40;
          local_58._12_4_ = 0;
          local_48 = 0xffffffff;
          local_78._0_8_ = local_68;
                    /* try { // try from 0002182c to 00021830 has its CatchHandler @ 00021eb2 */
          FUN_00017bf0(local_78,&DAT_000e0459);
          local_58._4_4_ = (int)lVar12;
          local_58._0_4_ = uVar17;
                    /* try { // try from 00021847 to 0002184b has its CatchHandler @ 00021ebb */
          FUN_000215a0(param_1,local_78);
          if ((undefined *)local_78._0_8_ == local_68) goto LAB_000217d0;
          lVar12 = lVar12 + 1;
          thunk_FUN_000d36e0(local_78._0_8_,local_68._0_8_ + 1);
        } while (lVar12 != 10);
LAB_00021880:
        if (*(uint *)(param_2 + 4 + lVar9 * 4) < 2) {
          iVar13 = *(int *)(param_4 + lVar9 * 4);
          if (iVar11 <= iVar13) {
            iVar13 = iVar11;
          }
          if (0 < iVar13) {
            iVar13 = 1;
            do {
              local_48 = 0xffffffff;
              local_58 = ZEXT816(0xffffffff00000000);
              local_78._0_8_ = local_68;
                    /* try { // try from 00021905 to 00021909 has its CatchHandler @ 00021eb2 */
              FUN_00017bf0(local_78,"gather","");
              local_58._0_4_ = uVar17;
              auVar4 = local_58;
              local_58._12_4_ = iVar13;
              local_58._8_4_ = *(undefined4 *)(param_2 + 4 + lVar9 * 4);
              local_58._0_8_ = auVar4._0_8_;
                    /* try { // try from 0002193b to 0002193f has its CatchHandler @ 00021ecc */
              FUN_000215a0(param_1,local_78);
              if ((undefined *)local_78._0_8_ != local_68) {
                thunk_FUN_000d36e0(local_78._0_8_,local_68._0_8_ + 1);
              }
              iVar13 = iVar13 + 1;
              iVar15 = *(int *)(param_4 + lVar9 * 4);
              if (iVar11 <= iVar15) {
                iVar15 = iVar11;
              }
            } while (iVar13 <= iVar15);
          }
        }
        piVar16 = param_3 + lVar9 * 3 + 10;
        local_c8 = piVar1 + 3;
        iVar13 = 0;
        piVar18 = piVar16;
        do {
          iVar14 = 1;
          iVar15 = *piVar18;
          if (iVar11 <= *piVar18) {
            iVar15 = iVar11;
          }
          if (0 < iVar15) {
            do {
              local_78._0_8_ = local_68;
              local_48 = 0xffffffff;
              local_58 = ZEXT816(0xffffffff00000000);
                    /* try { // try from 00021a11 to 00021a15 has its CatchHandler @ 00021eb2 */
              FUN_00017bf0(local_78,"load");
              local_58._0_4_ = uVar17;
              local_58._8_4_ = iVar13;
              local_58._12_4_ = iVar14;
                    /* try { // try from 00021a35 to 00021a39 has its CatchHandler @ 00021eae */
              FUN_000215a0(param_1,local_78);
              if ((undefined *)local_78._0_8_ != local_68) {
                thunk_FUN_000d36e0(local_78._0_8_,local_68._0_8_ + 1);
              }
              iVar14 = iVar14 + 1;
              iVar15 = *piVar18;
              if (iVar11 <= *piVar18) {
                iVar15 = iVar11;
              }
            } while (iVar14 <= iVar15);
          }
          iVar15 = 1;
          if (0 < *local_c8) {
            do {
              local_78._0_8_ = local_68;
              local_48 = 0xffffffff;
              local_58 = ZEXT816(0xffffffff00000000);
                    /* try { // try from 00021ad1 to 00021ad5 has its CatchHandler @ 00021eb2 */
              FUN_00017bf0(local_78,"unload");
              local_58._0_4_ = uVar17;
              local_58._8_4_ = iVar13;
              local_58._12_4_ = iVar15;
                    /* try { // try from 00021af5 to 00021af9 has its CatchHandler @ 00021eb9 */
              FUN_000215a0(param_1,local_78);
              if ((undefined *)local_78._0_8_ != local_68) {
                thunk_FUN_000d36e0(local_78._0_8_,local_68._0_8_ + 1);
              }
              iVar15 = iVar15 + 1;
            } while (iVar15 <= *local_c8);
          }
          iVar13 = iVar13 + 1;
          local_c8 = local_c8 + 1;
          piVar18 = piVar18 + 1;
        } while (iVar13 != 3);
        if (*(int *)(param_2 + 4 + lVar9 * 4) == 2) {
          if (*(char *)((long)param_3 + lVar9 + 0xa0) == '\0') {
            if ((1 < *piVar16) && (0 < piVar16[1])) {
              auVar4._8_8_ = 0;
              auVar4._0_8_ = DAT_000e2e80;
              local_58 = auVar4 << 0x20;
              local_48 = 0xffffffff;
              local_78 = (undefined  [16])0x0;
              local_68 = (undefined  [16])0x0;
                    /* try { // try from 00021ccd to 00021cd1 has its CatchHandler @ 00021eb2 */
              FUN_00018b10(local_78,"build_workshop");
              local_58._0_4_ = uVar17;
                    /* try { // try from 00021ce1 to 00021ce5 has its CatchHandler @ 00021eb0 */
              FUN_000215a0(param_1,local_78);
              FUN_000b07c0(local_78);
              if (*(char *)((long)param_3 + lVar9 + 0xa0) != '\0') goto LAB_00021d06;
            }
          }
          else {
LAB_00021d06:
            if (((param_3[lVar9 + 0x2b] == 0) && (1 < *piVar16)) && (0 < piVar16[1])) {
              auVar5._8_8_ = 0;
              auVar5._0_8_ = DAT_000e2e80;
              local_58 = auVar5 << 0x20;
              local_48 = 0xffffffff;
              local_78 = (undefined  [16])0x0;
              local_68 = (undefined  [16])0x0;
                    /* try { // try from 00021d83 to 00021d87 has its CatchHandler @ 00021eb2 */
              FUN_00018b10(local_78,"craft");
              local_58._0_4_ = uVar17;
                    /* try { // try from 00021d97 to 00021d9b has its CatchHandler @ 00021ec0 */
              FUN_000215a0(param_1,local_78);
              FUN_000b07c0(local_78);
            }
          }
        }
        lVar9 = 0;
        piVar16 = (int *)(param_2 + 0x4e4);
        do {
          while (((*(int *)(param_5 + lVar9 * 4) != -1 || (piVar16[4] <= param_6)) ||
                 ((piVar16[2] != iVar2 || (piVar1[(long)*piVar16 + 3] < piVar16[1]))))) {
LAB_00021b90:
            lVar9 = lVar9 + 1;
            piVar16 = piVar16 + 5;
            if (lVar9 == 8) goto LAB_00021c70;
          }
          local_48 = 0;
          auVar3._8_8_ = 0;
          auVar3._0_8_ = DAT_000e2e80;
          local_58 = auVar3 << 0x20;
          local_78 = (undefined  [16])0x0;
          local_68 = (undefined  [16])0x0;
                    /* try { // try from 00021c15 to 00021c19 has its CatchHandler @ 00021eb2 */
          FUN_00018b10(local_78,"deliver");
          local_58._0_4_ = uVar17;
          local_48 = CONCAT44(local_48._4_4_,(int)lVar9);
                    /* try { // try from 00021c31 to 00021c35 has its CatchHandler @ 00021eb7 */
          FUN_000215a0(param_1,local_78);
          if ((undefined *)local_78._0_8_ == local_68) goto LAB_00021b90;
          lVar9 = lVar9 + 1;
          piVar16 = piVar16 + 5;
          thunk_FUN_000d36e0(local_78._0_8_,local_68._0_8_ + 1);
        } while (lVar9 != 8);
LAB_00021c70:
        lVar9 = *(long *)(param_3 + 4);
        lVar12 = *(long *)(param_3 + 6);
      }
      local_b8 = local_b8 + 1;
      uVar10 = lVar12 - lVar9;
    } while ((int)local_b8 < (int)((long)uVar10 >> 3) * -0x55555555);
  }
  if (((uVar10 < 0x31) && (3 < param_3[(long)*param_3 * 3 + 10])) &&
     (1 < (param_3 + (long)*param_3 * 3 + 10)[1])) {
    local_58._8_4_ = 0xffffffff;
    local_58._0_8_ = DAT_000e2e80;
    local_58._12_4_ = 0;
    local_48 = 0xffffffff;
    local_78 = (undefined  [16])0x0;
    local_68 = (undefined  [16])0x0;
                    /* try { // try from 00021e5b to 00021e5f has its CatchHandler @ 00021eb2 */
    FUN_00018b10(local_78,"build_boat");
                    /* try { // try from 00021e67 to 00021e6b has its CatchHandler @ 00021e7e */
    FUN_000215a0(param_1,local_78);
    FUN_000b07c0(local_78);
  }
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return param_1;
}


