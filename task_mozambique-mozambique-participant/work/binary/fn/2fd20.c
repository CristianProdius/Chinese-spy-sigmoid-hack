// ===== FUNC 2fd20 size=1526

void FUN_0002fd20(undefined *param_1,ulong *param_2,long param_3,uint param_4,undefined8 param_5)

{
  long *plVar1;
  undefined8 *__src;
  ulong *puVar2;
  undefined8 *puVar3;
  void *pvVar4;
  ulong uVar5;
  undefined8 uVar6;
  char cVar7;
  int iVar8;
  uint uVar9;
  undefined (*pauVar10) [16];
  ulong *puVar11;
  long lVar12;
  undefined8 uVar13;
  ulong uVar14;
  long lVar15;
  ulong *puVar16;
  char cVar17;
  long lVar18;
  ulong *puVar19;
  char cVar20;
  ulong uVar21;
  long lVar22;
  long lVar23;
  long lVar24;
  long in_FS_OFFSET;
  undefined auVar25 [16];
  ulong local_78;
  long *plStack_70;
  undefined local_68 [40];
  long local_40;
  
  cVar17 = (char)param_5;
  uVar21 = (ulong)param_4;
  cVar20 = (char)param_4;
  lVar22 = param_3 * 0x18 >> 3;
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  puVar2 = param_2 + param_3 * 3;
  *param_1 = 0;
  lVar23 = lVar22 * -0x5555555555555555;
  *(undefined8 *)(param_1 + 8) = 0;
  lVar12 = lVar23;
  puVar11 = param_2;
  if (0 < lVar23 >> 2) {
    puVar19 = param_2 + (lVar23 >> 2) * 0xc;
    puVar16 = param_2;
    do {
      cVar7 = FUN_00021220(puVar16);
      cVar17 = (char)param_5;
      cVar20 = (char)uVar21;
      puVar11 = puVar16;
      if (cVar7 == '\0') goto joined_r0x0003018e;
      puVar11 = puVar16 + 3;
      cVar7 = FUN_00021220();
      cVar20 = (char)uVar21;
      cVar17 = (char)param_5;
      if (cVar7 == '\0') goto joined_r0x0003018e;
      puVar11 = puVar16 + 6;
      cVar7 = FUN_00021220();
      cVar20 = (char)uVar21;
      cVar17 = (char)param_5;
      if (cVar7 == '\0') goto joined_r0x0003018e;
      puVar11 = puVar16 + 9;
      cVar7 = FUN_00021220();
      cVar20 = (char)uVar21;
      cVar17 = (char)param_5;
      if (cVar7 == '\0') goto joined_r0x0003018e;
      puVar16 = puVar16 + 0xc;
    } while (puVar16 != puVar19);
    lVar12 = ((long)puVar2 - (long)puVar16 >> 3) * -0x5555555555555555;
    puVar11 = puVar16;
  }
  if (lVar12 == 2) {
LAB_000302ab:
    cVar7 = FUN_00021220(puVar11);
    if (cVar7 != '\0') {
      puVar11 = puVar11 + 3;
LAB_000302bf:
      cVar7 = FUN_00021220(puVar11);
      if (cVar7 != '\0') goto LAB_0003025e;
    }
joined_r0x0003018e:
    if (cVar20 == '\0') {
      if (cVar17 == '\x02') goto LAB_0002fe00;
      if (cVar17 == '\x01') {
        if (puVar2 != puVar11) {
          uVar13 = FUN_00040f40(0x20);
                    /* try { // try from 0003030d to 00030311 has its CatchHandler @ 000303ad */
          FUN_00018b10(local_68,"cannot create object from initializer list");
                    /* try { // try from 0003031d to 00030321 has its CatchHandler @ 000303a8 */
          FUN_00013f05(uVar13,0x12d,local_68);
          FUN_000b07c0(local_68);
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 0003033b to 0003033f has its CatchHandler @ 00030345 */
          FUN_00041f00(uVar13,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
        }
        goto LAB_0002feff;
      }
    }
    if (puVar2 != puVar11) {
LAB_0002fe00:
      *param_1 = 2;
                    /* try { // try from 0002fe0d to 0002fe11 has its CatchHandler @ 00030345 */
      pauVar10 = (undefined (*) [16])FUN_00041fe0(0x18);
      *(undefined8 *)pauVar10[1] = 0;
      *pauVar10 = (undefined  [16])0x0;
      if (param_3 * 0x18 < 0) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 000302e4 to 000302e8 has its CatchHandler @ 000302e9 */
        FUN_00015e26("cannot create std::vector larger than max_size()");
      }
      if (lVar23 == 0) {
        puVar11 = (ulong *)0x0;
      }
      else {
                    /* try { // try from 0002fe40 to 0002fe44 has its CatchHandler @ 000302e9 */
        puVar11 = (ulong *)FUN_00041fe0(lVar22 * -0x5555555555555550);
      }
      *(ulong **)*pauVar10 = puVar11;
      *(ulong **)pauVar10[1] = puVar11 + lVar22 * -0xaaaaaaaaaaaaaaa;
      if (param_2 != puVar2) {
        do {
          while (param_2[2] != 0) {
                    /* try { // try from 0002fe6b to 0002fe6f has its CatchHandler @ 00030372 */
            FUN_0002f160(puVar11);
            param_2 = param_2 + 3;
            puVar11 = puVar11 + 2;
            if (puVar2 == param_2) goto LAB_0002feaa;
          }
          uVar21 = *param_2;
          uVar5 = param_2[1];
          puVar19 = puVar11 + 2;
          *(undefined *)param_2 = 0;
          puVar16 = param_2 + 3;
          param_2[1] = 0;
          *puVar11 = uVar21;
          puVar11[1] = uVar5;
          param_2 = puVar16;
          puVar11 = puVar19;
        } while (puVar2 != puVar16);
      }
LAB_0002feaa:
      *(ulong **)(*pauVar10 + 8) = puVar11;
      *(undefined (**) [16])(param_1 + 8) = pauVar10;
      goto LAB_0002feb7;
    }
  }
  else {
    if (lVar12 == 3) {
      cVar7 = FUN_00021220(puVar11);
      if (cVar7 != '\0') {
        puVar11 = puVar11 + 3;
        goto LAB_000302ab;
      }
      goto joined_r0x0003018e;
    }
    if (lVar12 == 1) goto LAB_000302bf;
LAB_0003025e:
    if ((cVar20 == '\0') && (cVar17 == '\x02')) goto LAB_0002fe00;
  }
LAB_0002feff:
  *param_1 = 1;
                    /* try { // try from 0002ff0c to 0002ff69 has its CatchHandler @ 00030345 */
  lVar12 = FUN_00041fe0(0x30);
  *(undefined4 *)(lVar12 + 8) = 0;
  *(undefined8 *)(lVar12 + 0x10) = 0;
  *(long *)(lVar12 + 0x18) = lVar12 + 8;
  *(long *)(lVar12 + 0x20) = lVar12 + 8;
  *(undefined8 *)(lVar12 + 0x28) = 0;
  *(long *)(param_1 + 8) = lVar12;
  if (param_2 != puVar2) {
    if (param_2[2] == 0) goto LAB_00030167;
LAB_0002ff60:
    FUN_0002f160(&local_78);
    puVar11 = param_2;
    do {
      lVar22 = *(long *)(param_1 + 8);
      lVar23 = *plStack_70;
      lVar12 = lVar22 + 8;
      puVar3 = *(undefined8 **)(lVar23 + 8);
      lVar15 = lVar12;
      if (*(long *)(lVar22 + 0x10) == 0) {
LAB_0003007d:
                    /* try { // try from 00030082 to 00030086 has its CatchHandler @ 00030340 */
        lVar18 = FUN_00041fe0(0x50);
        pvVar4 = (void *)(lVar18 + 0x30);
        *(void **)(lVar18 + 0x20) = pvVar4;
        __src = puVar3 + 2;
        if ((undefined8 *)*puVar3 == __src) {
          uVar13 = 0xffffffffffffffff;
          if (puVar3[1] + 1 != 0) {
            memcpy(pvVar4,__src,puVar3[1] + 1);
            uVar13 = puVar3[1];
          }
        }
        else {
          *(void **)(lVar18 + 0x20) = (void *)*puVar3;
          *(undefined8 *)(lVar18 + 0x30) = puVar3[2];
          uVar13 = puVar3[1];
        }
        *(undefined8 *)(lVar18 + 0x28) = uVar13;
        puVar3[1] = 0;
        *(undefined *)(puVar3 + 2) = 0;
        uVar13 = *(undefined8 *)(lVar23 + 0x10);
        uVar6 = *(undefined8 *)(lVar23 + 0x18);
        *puVar3 = __src;
        *(undefined *)(lVar23 + 0x10) = 0;
        *(undefined8 *)(lVar23 + 0x18) = 0;
        *(undefined8 *)(lVar18 + 0x40) = uVar13;
        *(undefined8 *)(lVar18 + 0x48) = uVar6;
        auVar25 = FUN_00026160(lVar22,lVar15,lVar18 + 0x20);
        lVar23 = auVar25._8_8_;
        if (lVar23 == 0) {
          FUN_00024620(lVar18 + 0x48,*(undefined *)(lVar18 + 0x40));
          if (pvVar4 != *(void **)(lVar18 + 0x20)) {
            thunk_FUN_000d36e0(*(void **)(lVar18 + 0x20),*(long *)(lVar18 + 0x30) + 1);
          }
          thunk_FUN_000d36e0(lVar18,0x50);
        }
        else {
          if ((auVar25._0_8_ == 0) && (lVar23 != lVar12)) {
            uVar9 = FUN_00017b10(*(undefined8 *)(lVar18 + 0x20),*(undefined8 *)(lVar18 + 0x28),
                                 *(undefined8 *)(lVar23 + 0x20),*(undefined8 *)(lVar23 + 0x28));
            uVar9 = uVar9 >> 0x1f;
          }
          else {
            uVar9 = 1;
          }
          FUN_00049eb0(uVar9,lVar18,lVar23,lVar12);
          *(long *)(lVar22 + 0x28) = *(long *)(lVar22 + 0x28) + 1;
        }
      }
      else {
        uVar21 = puVar3[1];
        pvVar4 = (void *)*puVar3;
        lVar18 = *(long *)(lVar22 + 0x10);
        do {
          while( true ) {
            uVar5 = *(ulong *)(lVar18 + 0x28);
            uVar14 = uVar21;
            if (uVar5 <= uVar21) {
              uVar14 = uVar5;
            }
            if ((uVar14 != 0) &&
               (iVar8 = memcmp(*(void **)(lVar18 + 0x20),pvVar4,uVar14), iVar8 != 0)) break;
            lVar24 = uVar5 - uVar21;
            if (lVar24 < 0x80000000) {
              if (-0x80000001 < lVar24) {
                iVar8 = (int)lVar24;
                break;
              }
              goto LAB_0002ffb8;
            }
LAB_00030007:
            plVar1 = (long *)(lVar18 + 0x10);
            lVar15 = lVar18;
            lVar18 = *plVar1;
            if (*plVar1 == 0) goto LAB_00030013;
          }
          if (-1 < iVar8) goto LAB_00030007;
LAB_0002ffb8:
          lVar18 = *(long *)(lVar18 + 0x18);
        } while (lVar18 != 0);
LAB_00030013:
        if (lVar12 == lVar15) goto LAB_0003007d;
        uVar5 = *(ulong *)(lVar15 + 0x28);
        uVar14 = uVar21;
        if (uVar5 <= uVar21) {
          uVar14 = uVar5;
        }
        if ((uVar14 == 0) || (iVar8 = memcmp(pvVar4,*(void **)(lVar15 + 0x20),uVar14), iVar8 == 0))
        {
          lVar18 = uVar21 - uVar5;
          if (lVar18 < 0x80000000) {
            if (lVar18 < -0x80000000) goto LAB_0003007d;
            iVar8 = (int)lVar18;
            goto LAB_00030075;
          }
        }
        else {
LAB_00030075:
          if (iVar8 < 0) goto LAB_0003007d;
        }
      }
      param_2 = puVar11 + 3;
      FUN_00024620(&plStack_70,local_78 & 0xff);
      if (puVar2 == param_2) break;
      if (puVar11[5] != 0) goto LAB_0002ff60;
LAB_00030167:
      local_78 = *param_2;
      plStack_70 = (long *)param_2[1];
      *(undefined *)param_2 = 0;
      param_2[1] = 0;
      puVar11 = param_2;
    } while( true );
  }
LAB_0002feb7:
  if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}


