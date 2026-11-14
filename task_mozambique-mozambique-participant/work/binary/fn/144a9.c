// ===== FUNC 144a9 size=106

undefined8 FUN_000144a9(void)

{
  byte bVar1;
  long lVar2;
  bool bVar3;
  undefined uVar4;
  int iVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  undefined8 uVar9;
  long *plVar10;
  char *pcVar11;
  byte *pbVar12;
  undefined *puVar13;
  long unaff_RBP;
  undefined8 *puVar14;
  undefined *unaff_R13;
  long lVar16;
  long lVar17;
  long lVar18;
  long in_FS_OFFSET;
  undefined8 param_8;
  undefined8 param_9;
  long param_10;
  undefined *param_11;
  code *in_stack_00000030;
  undefined *in_stack_00000038;
  undefined8 in_stack_00000040;
  undefined8 param_12;
  undefined8 in_stack_00000050;
  ulong in_stack_00000058;
  char in_stack_00000060;
  long in_stack_00000068;
  ulong in_stack_00000070;
  undefined8 in_stack_00000078;
  undefined uStack0000000000000080;
  undefined8 uStack0000000000000088;
  long in_stack_00000090;
  undefined8 in_stack_000000a0;
  ulong in_stack_000000a8;
  undefined in_stack_000000b0;
  undefined *in_stack_000000c0;
  undefined8 in_stack_000000c8;
  undefined in_stack_000000d0;
  undefined in_stack_000000e0;
  long *in_stack_000000e8;
  undefined8 in_stack_000000f0;
  undefined in_stack_000000f8;
  undefined8 in_stack_00000100;
  undefined8 in_stack_00000108;
  undefined param_13;
  long *in_stack_00000118;
  undefined8 in_stack_00000120;
  undefined param_14;
  undefined8 param_15;
  undefined8 in_stack_00000138;
  undefined param_16;
  long *in_stack_00000148;
  undefined8 in_stack_00000150;
  undefined param_17;
  undefined8 param_18;
  undefined8 in_stack_00000168;
  char *in_stack_00000170;
  char *in_stack_00000178;
  code *in_stack_00000180;
  undefined *in_stack_00000188;
  undefined8 in_stack_00000198;
  undefined8 in_stack_000001b0;
  long in_stack_000001b8;
  undefined8 *puVar15;
  
  param_11 = (undefined *)0x0;
  FUN_00024620(&stack0x00000160,param_17);
  FUN_00024620();
  FUN_00024620(&stack0x00000130,param_14);
  FUN_00024620(param_12,param_13);
  FUN_00024620(&stack0x00000100,in_stack_000000f8);
  FUN_00024620(param_8,in_stack_000000e0);
  puVar13 = unaff_R13 + (2 - (long)param_11) * 0x18;
  while (puVar13 != unaff_R13) {
    FUN_00024620(puVar13 + -0x10,puVar13[-0x18]);
    puVar13 = puVar13 + -0x18;
  }
  FUN_00024620(&stack0x00000078,in_stack_00000070 & 0xff);
  FUN_000b07c0();
  FUN_00024620(&stack0x00000068,in_stack_00000060);
  if (unaff_RBP != 1) {
    FUN_000b07c0(param_9);
    if (param_10 != 0) {
      FUN_00018de0(param_10);
    }
                    /* WARNING: Subroutine does not return */
    FUN_000ddde0();
  }
  FUN_000410a0();
  uVar9 = FUN_000aaab0(&DAT_00124100,"{\"error\":\"invalid request or action\"}\n");
  FUN_000a9b20(uVar9);
  FUN_00041110();
  do {
    FUN_000b07c0(param_9);
    in_stack_000000b0 = 0;
    bVar3 = false;
    in_stack_000000a8 = 0;
    in_stack_000000a0 = in_stack_00000040;
    while ((plVar10 = (long *)FUN_00090640(),
           (*(byte *)((long)plVar10 + *(long *)(*plVar10 + -0x18) + 0x20) & 5) == 0 &&
           (in_stack_00000050._6_1_ != '\n'))) {
      if (in_stack_000000a8 < 0x8000) {
        FUN_000b1530(param_9,(int)in_stack_00000050._6_1_);
      }
      else {
        bVar3 = true;
      }
    }
    if (((DAT_00124250 & 5) != 0) && (in_stack_000000a8 == 0)) {
      if (!bVar3) {
LAB_00016f07:
        FUN_000b07c0(param_9);
        if (param_10 != 0) {
          FUN_00018de0(param_10);
        }
        if (in_stack_000001b8 == *(long *)(in_FS_OFFSET + 0x28)) {
          return 0;
        }
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
LAB_00014534:
      uVar9 = FUN_00040f40(0x10);
      FUN_00053220(uVar9,"request too large");
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(uVar9,&PTR_PTR_FUN_0011d470,FUN_00049930);
    }
    if (bVar3) goto LAB_00014534;
    param_11 = &stack0x00000080;
    in_stack_00000090 = 0;
    in_stack_00000178 = (char *)0x0;
    _uStack0000000000000080 = (undefined  [16])0x0;
    in_stack_00000180 = in_stack_00000030;
    in_stack_00000188 = in_stack_00000038;
    in_stack_00000170 = param_11;
    FUN_00038940(&stack0x00000060,param_9,&stack0x00000170,1,0);
    if (in_stack_00000180 != (code *)0x0) {
      (*in_stack_00000180)(&stack0x00000170,&stack0x00000170,3);
    }
    uVar9 = uStack0000000000000088;
    for (lVar16 = _uStack0000000000000080; uVar9 != lVar16; lVar16 = lVar16 + 0x30) {
      lVar2 = *(long *)(lVar16 + 0x10);
      while (lVar2 != 0) {
        FUN_00018460(*(undefined8 *)(lVar2 + 0x18));
        lVar17 = *(long *)(lVar2 + 0x10);
        if (*(long *)(lVar2 + 0x20) != lVar2 + 0x30) {
          thunk_FUN_000d36e0(*(long *)(lVar2 + 0x20),*(long *)(lVar2 + 0x30) + 1);
        }
        thunk_FUN_000d36e0(lVar2,0x40);
        lVar2 = lVar17;
      }
    }
    if (_uStack0000000000000080 != 0) {
      thunk_FUN_000d36e0(_uStack0000000000000080,in_stack_00000090 - _uStack0000000000000080);
    }
    if (in_stack_00000060 != '\x01') {
      uVar9 = FUN_000142f8();
      return uVar9;
    }
    lVar16 = in_stack_00000068 + 8;
    lVar2 = *(long *)(in_stack_00000068 + 0x10);
    lVar17 = lVar16;
    if (*(long *)(in_stack_00000068 + 0x10) == 0) {
code_r0x000142f8:
      uVar9 = FUN_00040f40(0x10);
      FUN_00053220(uVar9,"command required");
                    /* WARNING: Subroutine does not return */
      FUN_00041f00(uVar9,&PTR_PTR_FUN_0011d470,FUN_00049930);
    }
    do {
      while( true ) {
        lVar18 = lVar2;
        iVar5 = FUN_000b31e0(lVar18 + 0x20,"command");
        plVar10 = (long *)(lVar18 + 0x18);
        if (-1 < iVar5) break;
        lVar2 = *plVar10;
        lVar18 = lVar17;
        if (*plVar10 == 0) goto LAB_00016d9b;
      }
      lVar2 = *(long *)(lVar18 + 0x10);
      lVar17 = lVar18;
    } while (*(long *)(lVar18 + 0x10) != 0);
LAB_00016d9b:
    if ((lVar16 == lVar18) || (iVar5 = FUN_000b31e0(lVar18 + 0x20,"command"), 0 < iVar5))
    goto code_r0x000142f8;
    in_stack_00000170 = (char *)&stack0x00000180;
    FUN_00017bf0(&stack0x00000170,"command","");
    pcVar11 = (char *)FUN_00026330(&stack0x00000060,&stack0x00000170);
    if ((code **)in_stack_00000170 != &stack0x00000180) {
      thunk_FUN_000d36e0(in_stack_00000170,in_stack_00000180 + 1);
    }
    if (*pcVar11 != '\x03') {
      uVar9 = FUN_000142f8();
      return uVar9;
    }
    in_stack_00000170 = (char *)&stack0x00000180;
    FUN_00017bf0(&stack0x00000170,"command","");
    pcVar11 = (char *)FUN_00026330(&stack0x00000060,&stack0x00000170);
    if ((code **)in_stack_00000170 != &stack0x00000180) {
      thunk_FUN_000d36e0(in_stack_00000170,in_stack_00000180 + 1);
    }
    in_stack_000000d0 = 0;
    in_stack_000000c0 = &stack0x000000d0;
    in_stack_000000c8 = 0;
    if (*pcVar11 != '\x03') {
      uVar9 = FUN_00014254();
      return uVar9;
    }
    FUN_000b0ad0(&stack0x000000c0,*(undefined8 *)(pcVar11 + 8));
    in_stack_00000070 = 0;
    in_stack_00000078 = 0;
    iVar5 = FUN_000b31e0(&stack0x000000c0,&DAT_000e013c);
    if (iVar5 == 0) {
      in_stack_00000170 = "command";
      FUN_00017f10(&stack0x00000060,&stack0x00000170,1);
      FUN_00024620(&stack0x00000078,0);
      FUN_000b07c0(&stack0x000000c0);
      FUN_00024620(&stack0x00000068,in_stack_00000060);
      goto LAB_00016f07;
    }
    iVar5 = FUN_000b31e0(&stack0x000000c0,"hello");
    if (iVar5 == 0) {
      in_stack_00000170 = "command";
      FUN_00017f10(&stack0x00000060,&stack0x00000170,1);
      in_stack_000000e0 = 0;
      in_stack_000000e8 = (long *)0x0;
      FUN_00024620(&stack0x000000e8,0);
      in_stack_000000e0 = 3;
      plVar10 = (long *)FUN_00041fe0(0x20);
      *plVar10 = (long)(plVar10 + 2);
      FUN_00017bf0(plVar10,"protocol");
      in_stack_000000f0 = 0;
      in_stack_000000f8 = 5;
      in_stack_00000100 = 5;
      in_stack_00000108 = 0;
      in_stack_000000e8 = plVar10;
      FUN_0002fd20(&stack0x00000170,&stack0x000000e0,2,1,2);
      in_stack_00000180 = (code *)0x0;
      param_13 = 0;
      in_stack_00000118 = (long *)0x0;
      FUN_00024620(&stack0x00000118,0);
      param_13 = 3;
      plVar10 = (long *)FUN_00041fe0(0x20);
      *plVar10 = (long)(plVar10 + 2);
      FUN_00017bf0(plVar10,"rounds");
      in_stack_00000120 = 0;
      param_14 = 5;
      param_15 = 0x50;
      in_stack_00000138 = 0;
      in_stack_00000118 = plVar10;
      FUN_0002fd20(&stack0x00000188,&stack0x00000110,2);
      in_stack_00000198 = 0;
      param_16 = 0;
      in_stack_00000148 = (long *)0x0;
      FUN_00024620(&stack0x00000148,0);
      param_16 = 3;
      plVar10 = (long *)FUN_00041fe0(0x20);
      *plVar10 = (long)(plVar10 + 2);
      uStack0000000000000088 = plVar10;
      _uStack0000000000000080 = (long)&stack0x00000050 + 7;
      FUN_00017bf0(plVar10);
      in_stack_00000150 = 0;
      in_stack_00000168 = 0;
      param_17 = 6;
      param_18 = 5;
      in_stack_00000148 = plVar10;
      FUN_0002fd20(&stack0x000001a0,&stack0x00000140,2,1,2);
      in_stack_000001b0 = 0;
      FUN_0002fd20(param_11,&stack0x00000170,3,1);
      uVar9 = in_stack_00000078;
      uVar4 = uStack0000000000000080;
      _uStack0000000000000080 = SUB168(_uStack0000000000000080,1) << 8;
      in_stack_00000070 = CONCAT71(in_stack_00000070._1_7_,uVar4);
      in_stack_00000078 = uStack0000000000000088;
      uStack0000000000000088 = uVar9;
      FUN_00024620(&stack0x00000080 + 8,0);
      puVar14 = &stack0x000001b8;
      do {
        puVar15 = puVar14 + -3;
        FUN_00024620(puVar14 + -2,*(undefined *)puVar15);
        puVar14 = puVar15;
      } while ((char **)puVar15 != &stack0x00000170);
      FUN_00024620(&stack0x00000160,param_17);
      FUN_00024620(&stack0x00000148,param_16);
      FUN_00024620(&stack0x00000130,param_14);
      FUN_00024620(&stack0x00000118,param_13);
      FUN_00024620(&stack0x00000100,in_stack_000000f8);
      FUN_00024620(&stack0x000000e8,in_stack_000000e0);
    }
    else {
      iVar5 = FUN_000b31e0(&stack0x000000c0,"reset");
      if (iVar5 == 0) {
        in_stack_00000170 = "command";
        in_stack_00000178 = PTR_s_group_0011bb90;
        in_stack_00000180 = (code *)0xe5bd2;
        in_stack_00000188 = PTR_DAT_0011bb98;
        FUN_00017f10(&stack0x00000060,&stack0x00000170,4);
        uVar9 = FUN_000266c0(&stack0x00000060,"group");
        uVar6 = FUN_0001a590(uVar9);
        uVar9 = FUN_000266c0(&stack0x00000060,"seed");
        uVar7 = FUN_0001a590(uVar9);
        pbVar12 = (byte *)FUN_000266c0(&stack0x00000060,&DAT_000e016b);
        if (*pbVar12 != 6) {
LAB_00014179:
          uVar9 = FUN_00040f40(0x10);
          FUN_00053220(uVar9,"game must be 0-4");
                    /* WARNING: Subroutine does not return */
          FUN_00041f00(uVar9,&PTR_PTR_FUN_0011d470,FUN_00049930);
        }
        in_stack_00000058 = 0;
        FUN_0002ce30(pbVar12,&stack0x00000058);
        if (4 < in_stack_00000058) goto LAB_00014179;
        bVar1 = *pbVar12;
        if (bVar1 == 6) {
LAB_0001718c:
          uVar8 = *(uint *)(pbVar12 + 8);
        }
        else if (bVar1 < 7) {
          if (bVar1 != 4) {
            if (bVar1 != 5) {
              uVar9 = FUN_00014566();
              return uVar9;
            }
            goto LAB_0001718c;
          }
          uVar8 = (uint)pbVar12[8];
        }
        else {
          if (bVar1 != 7) {
            uVar9 = FUN_00014566();
            return uVar9;
          }
          uVar8 = (uint)*(double *)(pbVar12 + 8);
        }
        if (7 < uVar6) {
          uVar9 = FUN_000141ab();
          return uVar9;
        }
        lVar16 = FUN_00041fe0(0xf00);
        FUN_0001fed0(lVar16,uVar6,uVar7,uVar8);
        if (param_10 != 0) {
          FUN_00018de0(param_10);
        }
        FUN_0003fdf0(param_11,lVar16);
        uVar9 = in_stack_00000078;
        uVar4 = uStack0000000000000080;
        _uStack0000000000000080 = SUB168(_uStack0000000000000080,1) << 8;
        in_stack_00000070 = CONCAT71(in_stack_00000070._1_7_,uVar4);
        in_stack_00000078 = uStack0000000000000088;
        uStack0000000000000088 = uVar9;
        FUN_00024620(&stack0x00000080 + 8,0);
        param_10 = lVar16;
      }
      else {
        iVar5 = FUN_000b31e0(&stack0x000000c0,&DAT_000e018f);
        if (iVar5 != 0) {
          uVar9 = FUN_00040f40(0x10);
          FUN_00053220(uVar9,"unknown command");
                    /* WARNING: Subroutine does not return */
          FUN_00041f00(uVar9,&PTR_PTR_FUN_0011d470,FUN_00049930);
        }
        in_stack_00000170 = "command";
        in_stack_00000178 = "action";
        FUN_00017f10(&stack0x00000060,&stack0x00000170,2);
        if (param_10 == 0) {
          uVar9 = FUN_00040f40(0x10);
          FUN_00053220(uVar9,"reset first");
                    /* WARNING: Subroutine does not return */
          FUN_00041f00(uVar9,&PTR_PTR_FUN_0011d470,FUN_00049930);
        }
        uVar9 = FUN_000266c0(&stack0x00000060,"action");
        FUN_0003d0b0(param_10,uVar9);
        FUN_0003fdf0(param_11,param_10);
        uVar9 = in_stack_00000078;
        uVar4 = uStack0000000000000080;
        _uStack0000000000000080 = SUB168(_uStack0000000000000080,1) << 8;
        in_stack_00000070 = CONCAT71(in_stack_00000070._1_7_,uVar4);
        in_stack_00000078 = uStack0000000000000088;
        uStack0000000000000088 = uVar9;
        FUN_00024620(&stack0x00000080 + 8,0);
      }
    }
    FUN_0002e6f0(&stack0x00000170,&stack0x00000070,0xffffffff,0x20);
    uVar9 = FUN_000aa620(&DAT_00124100,in_stack_00000170,in_stack_00000178);
    uVar9 = FUN_000aaa60(uVar9,10);
    FUN_000a9b20(uVar9);
    FUN_000b07c0(&stack0x00000170);
    FUN_00024620(&stack0x00000078,in_stack_00000070 & 0xff);
    FUN_000b07c0(&stack0x000000c0);
    FUN_00024620(&stack0x00000068,in_stack_00000060);
  } while( true );
}


