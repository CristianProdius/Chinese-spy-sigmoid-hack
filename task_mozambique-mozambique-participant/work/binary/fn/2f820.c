// ===== FUNC 2f820 size=728

undefined8 FUN_0002f820(long param_1,long *param_2)

{
  undefined uVar1;
  long lVar2;
  ulong *puVar3;
  void *__s2;
  ulong uVar4;
  char cVar5;
  int iVar6;
  long *plVar7;
  ulong uVar8;
  long lVar9;
  long lVar10;
  ulong __n;
  long lVar11;
  long lVar12;
  long in_FS_OFFSET;
  bool bVar13;
  undefined local_71;
  long *local_70;
  ulong local_68;
  long *local_60;
  long **local_58;
  long *local_50 [2];
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  local_68 = 0;
  local_60 = (long *)0x0;
                    /* try { // try from 0002f860 to 0002f873 has its CatchHandler @ 0002fb58 */
  FUN_00024620(&local_60,0);
  local_68 = CONCAT71(local_68._1_7_,3);
  plVar7 = (long *)FUN_00041fe0(0x20);
  lVar12 = *param_2;
  lVar2 = param_2[1];
  *plVar7 = (long)(plVar7 + 2);
  local_58 = &local_70;
  local_50[0] = plVar7;
                    /* try { // try from 0002f89f to 0002f8a3 has its CatchHandler @ 0002fb10 */
  FUN_00017e00(plVar7,lVar12,lVar2 + lVar12);
  local_71 = 4;
  local_58 = (long **)CONCAT44(local_58._4_4_,
                               (int)(*(long *)(param_1 + 0x10) - *(long *)(param_1 + 8) >> 3));
  local_60 = plVar7;
  if (*(long *)(param_1 + 0x90) == 0) {
                    /* try { // try from 0002fb01 to 0002fb05 has its CatchHandler @ 0002fb5d */
    FUN_00016056();
    goto LAB_0002fb06;
  }
                    /* try { // try from 0002f8e5 to 0002f947 has its CatchHandler @ 0002fb5d */
  cVar5 = (**(code **)(param_1 + 0x98))(param_1 + 0x80,&local_58,&local_71,&local_68);
  puVar3 = *(ulong **)(param_1 + 0x58);
  iVar6 = *(int *)(param_1 + 0x60);
  if (puVar3 == *(ulong **)(param_1 + 0x68)) {
                    /* try { // try from 0002facf to 0002fad3 has its CatchHandler @ 0002fb5d */
    FUN_00018750(param_1 + 0x48,puVar3,iVar6,cVar5);
    if (cVar5 != '\0') goto LAB_0002f92a;
  }
  else {
    if (iVar6 == 0x3f) {
      *(undefined4 *)(param_1 + 0x60) = 0;
      *(ulong **)(param_1 + 0x58) = puVar3 + 1;
    }
    else {
      *(int *)(param_1 + 0x60) = iVar6 + 1;
    }
    uVar8 = 1L << ((byte)iVar6 & 0x3f);
    if (cVar5 == '\0') {
      *puVar3 = ~uVar8 & *puVar3;
    }
    else {
      *puVar3 = uVar8 | *puVar3;
LAB_0002f92a:
      if (*(long *)(*(long *)(param_1 + 0x10) + -8) != 0) {
        FUN_0002f160(&local_58,param_1 + 0xa8);
        lVar2 = *(long *)(*(long *)(*(long *)(param_1 + 0x10) + -8) + 8);
        lVar12 = lVar2 + 8;
        if (*(long *)(lVar2 + 0x10) == 0) {
LAB_0002fae3:
          local_70 = param_2;
                    /* try { // try from 0002faf4 to 0002faf8 has its CatchHandler @ 0002fb0b */
          lVar9 = FUN_0001a480(lVar2,lVar12,&local_70);
        }
        else {
          __s2 = (void *)*param_2;
          uVar8 = param_2[1];
          lVar10 = *(long *)(lVar2 + 0x10);
          lVar9 = lVar12;
          do {
            while( true ) {
              lVar11 = lVar10;
              uVar4 = *(ulong *)(lVar11 + 0x28);
              __n = uVar8;
              if (uVar4 <= uVar8) {
                __n = uVar4;
              }
              if ((__n != 0) && (iVar6 = memcmp(*(void **)(lVar11 + 0x20),__s2,__n), iVar6 != 0))
              break;
              lVar10 = uVar4 - uVar8;
              if (lVar10 < 0x80000000) {
                if (-0x80000001 < lVar10) {
                  iVar6 = (int)lVar10;
                  break;
                }
                goto LAB_0002f9a0;
              }
LAB_0002f9f1:
              lVar10 = *(long *)(lVar11 + 0x10);
              lVar9 = lVar11;
              if (*(long *)(lVar11 + 0x10) == 0) goto LAB_0002f9fd;
            }
            if (-1 < iVar6) goto LAB_0002f9f1;
LAB_0002f9a0:
            lVar10 = *(long *)(lVar11 + 0x18);
          } while (*(long *)(lVar11 + 0x18) != 0);
LAB_0002f9fd:
          bVar13 = lVar12 == lVar9;
          lVar12 = lVar9;
          if ((bVar13) ||
             (iVar6 = FUN_00017b10(__s2,uVar8,*(undefined8 *)(lVar9 + 0x20),
                                   *(undefined8 *)(lVar9 + 0x28)), iVar6 < 0)) goto LAB_0002fae3;
        }
        uVar1 = *(undefined *)(lVar9 + 0x40);
        *(undefined *)(lVar9 + 0x40) = local_58._0_1_;
        plVar7 = *(long **)(lVar9 + 0x48);
        local_58 = (long **)CONCAT71(local_58._1_7_,uVar1);
        *(long **)(lVar9 + 0x48) = local_50[0];
        *(long *)(param_1 + 0x70) = lVar9 + 0x40;
        local_50[0] = plVar7;
        FUN_00024620(local_50);
      }
    }
  }
  FUN_00024620(&local_60,local_68 & 0xff);
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return 1;
  }
LAB_0002fb06:
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


