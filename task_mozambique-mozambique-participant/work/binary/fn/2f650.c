// ===== FUNC 2f650 size=427

undefined8 FUN_0002f650(long param_1,long *param_2)

{
  undefined uVar1;
  char *pcVar2;
  undefined *puVar3;
  undefined8 uVar4;
  long lVar5;
  ulong *puVar6;
  void *__s2;
  ulong uVar7;
  char cVar8;
  int iVar9;
  long lVar10;
  long *plVar11;
  ulong uVar12;
  long lVar13;
  long lVar14;
  ulong __n;
  char *pcVar15;
  long lVar16;
  long lVar17;
  long in_FS_OFFSET;
  bool bVar18;
  undefined uStack_d9;
  long *plStack_d8;
  ulong uStack_d0;
  long *plStack_c8;
  long **pplStack_c0;
  long *aplStack_b8 [2];
  long lStack_a8;
  long lStack_98;
  char *local_68;
  long lStack_60;
  char *local_58;
  undefined8 local_50;
  int local_48 [2];
  undefined8 local_40;
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  lVar10 = *(long *)(param_1 + 0x10);
  if (*(long *)(lVar10 + -8) != 0) {
    local_68 = (char *)CONCAT71(local_68._1_7_,1);
    local_48[0] = (int)(lVar10 - *(long *)(param_1 + 8) >> 3) + -1;
    if (*(long *)(param_1 + 0x90) == 0) {
      lVar17 = param_1;
      FUN_00016056();
      lStack_a8 = *(long *)(in_FS_OFFSET + 0x28);
      uStack_d0 = 0;
      plStack_c8 = (long *)0x0;
      lStack_98 = param_1;
      FUN_00024620(&plStack_c8,0);
      uStack_d0 = CONCAT71(uStack_d0._1_7_,3);
      plVar11 = (long *)FUN_00041fe0(0x20);
      lVar10 = *param_2;
      lVar5 = param_2[1];
      *plVar11 = (long)(plVar11 + 2);
      pplStack_c0 = &plStack_d8;
      aplStack_b8[0] = plVar11;
      FUN_00017e00(plVar11,lVar10,lVar5 + lVar10);
      uStack_d9 = 4;
      pplStack_c0 = (long **)CONCAT44(pplStack_c0._4_4_,
                                      (int)(*(long *)(lVar17 + 0x10) - *(long *)(lVar17 + 8) >> 3));
      plStack_c8 = plVar11;
      if (*(long *)(lVar17 + 0x90) == 0) {
        FUN_00016056();
        goto LAB_0002fb06;
      }
      cVar8 = (**(code **)(lVar17 + 0x98))(lVar17 + 0x80,&pplStack_c0,&uStack_d9,&uStack_d0);
      puVar6 = *(ulong **)(lVar17 + 0x58);
      iVar9 = *(int *)(lVar17 + 0x60);
      if (puVar6 == *(ulong **)(lVar17 + 0x68)) {
        FUN_00018750(lVar17 + 0x48,puVar6,iVar9,cVar8);
        if (cVar8 != '\0') goto LAB_0002f92a;
      }
      else {
        if (iVar9 == 0x3f) {
          *(undefined4 *)(lVar17 + 0x60) = 0;
          *(ulong **)(lVar17 + 0x58) = puVar6 + 1;
        }
        else {
          *(int *)(lVar17 + 0x60) = iVar9 + 1;
        }
        uVar12 = 1L << ((byte)iVar9 & 0x3f);
        if (cVar8 == '\0') {
          *puVar6 = ~uVar12 & *puVar6;
        }
        else {
          *puVar6 = uVar12 | *puVar6;
LAB_0002f92a:
          if (*(long *)(*(long *)(lVar17 + 0x10) + -8) != 0) {
            FUN_0002f160(&pplStack_c0,lVar17 + 0xa8);
            lVar5 = *(long *)(*(long *)(*(long *)(lVar17 + 0x10) + -8) + 8);
            lVar10 = lVar5 + 8;
            if (*(long *)(lVar5 + 0x10) == 0) {
LAB_0002fae3:
              plStack_d8 = param_2;
              lVar13 = FUN_0001a480(lVar5,lVar10,&plStack_d8);
            }
            else {
              __s2 = (void *)*param_2;
              uVar12 = param_2[1];
              lVar14 = *(long *)(lVar5 + 0x10);
              lVar13 = lVar10;
              do {
                while( true ) {
                  lVar16 = lVar14;
                  uVar7 = *(ulong *)(lVar16 + 0x28);
                  __n = uVar12;
                  if (uVar7 <= uVar12) {
                    __n = uVar7;
                  }
                  if ((__n != 0) && (iVar9 = memcmp(*(void **)(lVar16 + 0x20),__s2,__n), iVar9 != 0)
                     ) break;
                  lVar14 = uVar7 - uVar12;
                  if (lVar14 < 0x80000000) {
                    if (-0x80000001 < lVar14) {
                      iVar9 = (int)lVar14;
                      break;
                    }
                    goto LAB_0002f9a0;
                  }
LAB_0002f9f1:
                  lVar14 = *(long *)(lVar16 + 0x10);
                  lVar13 = lVar16;
                  if (*(long *)(lVar16 + 0x10) == 0) goto LAB_0002f9fd;
                }
                if (-1 < iVar9) goto LAB_0002f9f1;
LAB_0002f9a0:
                lVar14 = *(long *)(lVar16 + 0x18);
              } while (*(long *)(lVar16 + 0x18) != 0);
LAB_0002f9fd:
              bVar18 = lVar10 == lVar13;
              lVar10 = lVar13;
              if ((bVar18) ||
                 (iVar9 = FUN_00017b10(__s2,uVar12,*(undefined8 *)(lVar13 + 0x20),
                                       *(undefined8 *)(lVar13 + 0x28)), iVar9 < 0))
              goto LAB_0002fae3;
            }
            uVar1 = *(undefined *)(lVar13 + 0x40);
            *(undefined *)(lVar13 + 0x40) = pplStack_c0._0_1_;
            plVar11 = *(long **)(lVar13 + 0x48);
            pplStack_c0 = (long **)CONCAT71(pplStack_c0._1_7_,uVar1);
            *(long **)(lVar13 + 0x48) = aplStack_b8[0];
            *(long *)(lVar17 + 0x70) = lVar13 + 0x40;
            aplStack_b8[0] = plVar11;
            FUN_00024620(aplStack_b8);
          }
        }
      }
      FUN_00024620(&plStack_c8,uStack_d0 & 0xff);
      if (lStack_a8 == *(long *)(in_FS_OFFSET + 0x28)) {
        return 1;
      }
LAB_0002fb06:
                    /* WARNING: Subroutine does not return */
      __stack_chk_fail();
    }
    cVar8 = (**(code **)(param_1 + 0x98))(param_1 + 0x80,local_48,&local_68);
    if (cVar8 == '\0') {
      FUN_0002f160(local_48,param_1 + 0xa8);
      puVar3 = *(undefined **)(*(long *)(param_1 + 0x10) + -8);
      uVar1 = *puVar3;
      *puVar3 = (undefined)local_48[0];
      uVar4 = *(undefined8 *)(puVar3 + 8);
      local_48[0] = CONCAT31(local_48[0]._1_3_,uVar1);
      *(undefined8 *)(puVar3 + 8) = local_40;
      local_40 = uVar4;
      FUN_00024620();
    }
    lVar10 = *(long *)(param_1 + 0x10);
  }
  *(long *)(param_1 + 0x10) = lVar10 + -8;
  if (*(int *)(param_1 + 0x38) == 0) {
    *(long *)(param_1 + 0x30) = *(long *)(param_1 + 0x30) + -8;
    *(undefined4 *)(param_1 + 0x38) = 0x3f;
  }
  else {
    *(int *)(param_1 + 0x38) = *(int *)(param_1 + 0x38) + -1;
  }
  if ((*(long *)(param_1 + 8) != lVar10 + -8) &&
     (pcVar2 = *(char **)(lVar10 + -0x10), pcVar2 != (char *)0x0)) {
    if (*pcVar2 == '\x02') {
      lVar10 = 0;
      for (pcVar15 = (char *)**(undefined8 **)(pcVar2 + 8);
          (char *)(*(undefined8 **)(pcVar2 + 8))[1] != pcVar15; pcVar15 = pcVar15 + 0x10) {
        if (*pcVar15 == '\t') goto LAB_0002f7a3;
      }
    }
    else if (*pcVar2 == '\x01') {
      lVar5 = *(long *)(pcVar2 + 8);
      pcVar15 = (char *)0x0;
      lVar10 = *(long *)(lVar5 + 0x18);
      while (lVar10 != lVar5 + 8) {
        if (*(char *)(lVar10 + 0x40) == '\t') goto LAB_0002f7a3;
        lVar10 = FUN_00049c90();
      }
    }
  }
LAB_0002f6f2:
  if (local_20 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 1;
LAB_0002f7a3:
  local_50 = 0x8000000000000000;
  local_68 = pcVar2;
  lStack_60 = lVar10;
  local_58 = pcVar15;
  FUN_00025c50(local_48,pcVar2,&local_68);
  goto LAB_0002f6f2;
}


