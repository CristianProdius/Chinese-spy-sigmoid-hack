// ===== FUNC 2f4e0 size=357

undefined8 FUN_0002f4e0(long param_1,long *param_2)

{
  undefined uVar1;
  undefined *puVar2;
  undefined8 uVar3;
  char *pcVar4;
  ulong *puVar5;
  void *__s2;
  ulong uVar6;
  char cVar7;
  int iVar8;
  long lVar9;
  long *plVar10;
  ulong uVar11;
  long lVar12;
  long lVar13;
  ulong __n;
  char *pcVar14;
  long lVar15;
  long lVar16;
  long lVar17;
  long in_FS_OFFSET;
  bool bVar18;
  undefined uStack_121;
  long *plStack_120;
  ulong uStack_118;
  long *plStack_110;
  long **pplStack_108;
  long *aplStack_100 [2];
  long lStack_f0;
  long lStack_e0;
  char *pcStack_b0;
  long lStack_a8;
  char *pcStack_a0;
  undefined8 uStack_98;
  int aiStack_90 [2];
  undefined8 uStack_88;
  long lStack_68;
  long lStack_60;
  undefined local_39;
  int local_38 [2];
  undefined8 local_30 [2];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  lVar9 = *(long *)(param_1 + 0x10);
  if (*(long *)(lVar9 + -8) != 0) {
    local_39 = 3;
    local_38[0] = (int)(lVar9 - *(long *)(param_1 + 8) >> 3) + -1;
    if (*(long *)(param_1 + 0x90) == 0) {
      lVar16 = param_1;
      FUN_00016056();
      lStack_68 = *(long *)(in_FS_OFFSET + 0x28);
      lVar9 = *(long *)(lVar16 + 0x10);
      lStack_60 = param_1;
      if (*(long *)(lVar9 + -8) != 0) {
        pcStack_b0 = (char *)CONCAT71(pcStack_b0._1_7_,1);
        aiStack_90[0] = (int)(lVar9 - *(long *)(lVar16 + 8) >> 3) + -1;
        if (*(long *)(lVar16 + 0x90) == 0) {
          lVar17 = lVar16;
          FUN_00016056();
          lStack_f0 = *(long *)(in_FS_OFFSET + 0x28);
          uStack_118 = 0;
          plStack_110 = (long *)0x0;
          lStack_e0 = lVar16;
          FUN_00024620(&plStack_110,0);
          uStack_118 = CONCAT71(uStack_118._1_7_,3);
          plVar10 = (long *)FUN_00041fe0(0x20);
          lVar9 = *param_2;
          lVar16 = param_2[1];
          *plVar10 = (long)(plVar10 + 2);
          pplStack_108 = &plStack_120;
          aplStack_100[0] = plVar10;
          FUN_00017e00(plVar10,lVar9,lVar16 + lVar9);
          uStack_121 = 4;
          pplStack_108 = (long **)CONCAT44(pplStack_108._4_4_,
                                           (int)(*(long *)(lVar17 + 0x10) - *(long *)(lVar17 + 8) >>
                                                3));
          plStack_110 = plVar10;
          if (*(long *)(lVar17 + 0x90) == 0) {
            FUN_00016056();
            goto LAB_0002fb06;
          }
          cVar7 = (**(code **)(lVar17 + 0x98))(lVar17 + 0x80,&pplStack_108,&uStack_121,&uStack_118);
          puVar5 = *(ulong **)(lVar17 + 0x58);
          iVar8 = *(int *)(lVar17 + 0x60);
          if (puVar5 == *(ulong **)(lVar17 + 0x68)) {
            FUN_00018750(lVar17 + 0x48,puVar5,iVar8,cVar7);
            if (cVar7 != '\0') goto LAB_0002f92a;
          }
          else {
            if (iVar8 == 0x3f) {
              *(undefined4 *)(lVar17 + 0x60) = 0;
              *(ulong **)(lVar17 + 0x58) = puVar5 + 1;
            }
            else {
              *(int *)(lVar17 + 0x60) = iVar8 + 1;
            }
            uVar11 = 1L << ((byte)iVar8 & 0x3f);
            if (cVar7 == '\0') {
              *puVar5 = ~uVar11 & *puVar5;
            }
            else {
              *puVar5 = uVar11 | *puVar5;
LAB_0002f92a:
              if (*(long *)(*(long *)(lVar17 + 0x10) + -8) != 0) {
                FUN_0002f160(&pplStack_108,lVar17 + 0xa8);
                lVar16 = *(long *)(*(long *)(*(long *)(lVar17 + 0x10) + -8) + 8);
                lVar9 = lVar16 + 8;
                if (*(long *)(lVar16 + 0x10) == 0) {
LAB_0002fae3:
                  plStack_120 = param_2;
                  lVar12 = FUN_0001a480(lVar16,lVar9,&plStack_120);
                }
                else {
                  __s2 = (void *)*param_2;
                  uVar11 = param_2[1];
                  lVar13 = *(long *)(lVar16 + 0x10);
                  lVar12 = lVar9;
                  do {
                    while( true ) {
                      lVar15 = lVar13;
                      uVar6 = *(ulong *)(lVar15 + 0x28);
                      __n = uVar11;
                      if (uVar6 <= uVar11) {
                        __n = uVar6;
                      }
                      if ((__n != 0) &&
                         (iVar8 = memcmp(*(void **)(lVar15 + 0x20),__s2,__n), iVar8 != 0)) break;
                      lVar13 = uVar6 - uVar11;
                      if (lVar13 < 0x80000000) {
                        if (-0x80000001 < lVar13) {
                          iVar8 = (int)lVar13;
                          break;
                        }
                        goto LAB_0002f9a0;
                      }
LAB_0002f9f1:
                      lVar13 = *(long *)(lVar15 + 0x10);
                      lVar12 = lVar15;
                      if (*(long *)(lVar15 + 0x10) == 0) goto LAB_0002f9fd;
                    }
                    if (-1 < iVar8) goto LAB_0002f9f1;
LAB_0002f9a0:
                    lVar13 = *(long *)(lVar15 + 0x18);
                  } while (*(long *)(lVar15 + 0x18) != 0);
LAB_0002f9fd:
                  bVar18 = lVar9 == lVar12;
                  lVar9 = lVar12;
                  if ((bVar18) ||
                     (iVar8 = FUN_00017b10(__s2,uVar11,*(undefined8 *)(lVar12 + 0x20),
                                           *(undefined8 *)(lVar12 + 0x28)), iVar8 < 0))
                  goto LAB_0002fae3;
                }
                uVar1 = *(undefined *)(lVar12 + 0x40);
                *(undefined *)(lVar12 + 0x40) = pplStack_108._0_1_;
                plVar10 = *(long **)(lVar12 + 0x48);
                pplStack_108 = (long **)CONCAT71(pplStack_108._1_7_,uVar1);
                *(long **)(lVar12 + 0x48) = aplStack_100[0];
                *(long *)(lVar17 + 0x70) = lVar12 + 0x40;
                aplStack_100[0] = plVar10;
                FUN_00024620(aplStack_100);
              }
            }
          }
          FUN_00024620(&plStack_110,uStack_118 & 0xff);
          if (lStack_f0 == *(long *)(in_FS_OFFSET + 0x28)) {
            return 1;
          }
LAB_0002fb06:
                    /* WARNING: Subroutine does not return */
          __stack_chk_fail();
        }
        cVar7 = (**(code **)(lVar16 + 0x98))(lVar16 + 0x80,aiStack_90,&pcStack_b0);
        if (cVar7 == '\0') {
          FUN_0002f160(aiStack_90,lVar16 + 0xa8);
          puVar2 = *(undefined **)(*(long *)(lVar16 + 0x10) + -8);
          uVar1 = *puVar2;
          *puVar2 = (undefined)aiStack_90[0];
          uVar3 = *(undefined8 *)(puVar2 + 8);
          aiStack_90[0] = CONCAT31(aiStack_90[0]._1_3_,uVar1);
          *(undefined8 *)(puVar2 + 8) = uStack_88;
          uStack_88 = uVar3;
          FUN_00024620();
        }
        lVar9 = *(long *)(lVar16 + 0x10);
      }
      *(long *)(lVar16 + 0x10) = lVar9 + -8;
      if (*(int *)(lVar16 + 0x38) == 0) {
        *(long *)(lVar16 + 0x30) = *(long *)(lVar16 + 0x30) + -8;
        *(undefined4 *)(lVar16 + 0x38) = 0x3f;
      }
      else {
        *(int *)(lVar16 + 0x38) = *(int *)(lVar16 + 0x38) + -1;
      }
      if ((*(long *)(lVar16 + 8) != lVar9 + -8) &&
         (pcVar4 = *(char **)(lVar9 + -0x10), pcVar4 != (char *)0x0)) {
        if (*pcVar4 == '\x02') {
          lVar9 = 0;
          for (pcVar14 = (char *)**(undefined8 **)(pcVar4 + 8);
              (char *)(*(undefined8 **)(pcVar4 + 8))[1] != pcVar14; pcVar14 = pcVar14 + 0x10) {
            if (*pcVar14 == '\t') goto LAB_0002f7a3;
          }
        }
        else if (*pcVar4 == '\x01') {
          lVar16 = *(long *)(pcVar4 + 8);
          pcVar14 = (char *)0x0;
          lVar9 = *(long *)(lVar16 + 0x18);
          while (lVar9 != lVar16 + 8) {
            if (*(char *)(lVar9 + 0x40) == '\t') goto LAB_0002f7a3;
            lVar9 = FUN_00049c90();
          }
        }
      }
LAB_0002f6f2:
      if (lStack_68 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
      return 1;
    }
    cVar7 = (**(code **)(param_1 + 0x98))(param_1 + 0x80,local_38,&local_39);
    if (cVar7 == '\0') {
      FUN_0002f160(local_38,param_1 + 0xa8);
      puVar2 = *(undefined **)(*(long *)(param_1 + 0x10) + -8);
      uVar1 = *puVar2;
      *puVar2 = (undefined)local_38[0];
      uVar3 = *(undefined8 *)(puVar2 + 8);
      local_38[0] = CONCAT31(local_38[0]._1_3_,uVar1);
      *(undefined8 *)(puVar2 + 8) = local_30[0];
      local_30[0] = uVar3;
      FUN_00024620(local_30);
      lVar16 = *(long *)(param_1 + 0x10);
      lVar9 = lVar16 + -8;
      *(long *)(param_1 + 0x10) = lVar9;
      if (*(int *)(param_1 + 0x38) == 0) {
        *(long *)(param_1 + 0x30) = *(long *)(param_1 + 0x30) + -8;
        *(undefined4 *)(param_1 + 0x38) = 0x3f;
      }
      else {
        *(int *)(param_1 + 0x38) = *(int *)(param_1 + 0x38) + -1;
      }
      if ((lVar9 != *(long *)(param_1 + 8)) &&
         (pcVar4 = *(char **)(lVar16 + -0x10), *pcVar4 == '\x02')) {
        lVar9 = *(long *)(pcVar4 + 8);
        lVar16 = *(long *)(lVar9 + 8);
        uVar1 = *(undefined *)(lVar16 + -0x10);
        *(long *)(lVar9 + 8) = lVar16 + -0x10;
        FUN_00024620(lVar16 + -8,uVar1);
      }
      goto LAB_0002f55d;
    }
    lVar9 = *(long *)(param_1 + 0x10);
  }
  *(long *)(param_1 + 0x10) = lVar9 + -8;
  if (*(int *)(param_1 + 0x38) == 0) {
    *(long *)(param_1 + 0x30) = *(long *)(param_1 + 0x30) + -8;
    *(undefined4 *)(param_1 + 0x38) = 0x3f;
  }
  else {
    *(int *)(param_1 + 0x38) = *(int *)(param_1 + 0x38) + -1;
  }
LAB_0002f55d:
  if (local_20 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 1;
LAB_0002f7a3:
  uStack_98 = 0x8000000000000000;
  pcStack_b0 = pcVar4;
  lStack_a8 = lVar9;
  pcStack_a0 = pcVar14;
  FUN_00025c50(aiStack_90,pcVar4,&pcStack_b0);
  goto LAB_0002f6f2;
}


