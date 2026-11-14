// ===== FUNC 2d610 size=4110

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0002d610(long *param_1,undefined *param_2,char param_3,undefined param_4,int param_5,
                 int param_6)

{
  undefined auVar1 [16];
  undefined2 uVar2;
  undefined4 in_EAX;
  uint uVar3;
  code *UNRECOVERED_JUMPTABLE;
  undefined *puVar4;
  undefined8 uVar5;
  long lVar6;
  undefined *puVar7;
  ulong uVar8;
  long *plVar9;
  char *pcVar10;
  undefined8 uVar11;
  undefined8 *puVar12;
  ulong uVar13;
  long in_FS_OFFSET;
  double dVar14;
  undefined4 local_48;
  undefined4 local_44;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  switch(*param_2) {
  case 0:
    plVar9 = (long *)*param_1;
    UNRECOVERED_JUMPTABLE = *(code **)(*plVar9 + 8);
    if (UNRECOVERED_JUMPTABLE == FUN_0001ac60) {
      lVar6 = plVar9[1];
      if (0x3fffffffffffffffU - *(long *)(lVar6 + 8) < 4) {
LAB_0002e6d9:
                    /* WARNING: Subroutine does not return */
        FUN_00015e26("basic_string::append");
      }
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        uVar5 = 4;
        pcVar10 = "null";
LAB_0002d7d6:
        FUN_000b2500(lVar6,pcVar10,uVar5);
        return;
      }
      break;
    }
    if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) break;
    goto LAB_0002de62;
  case 1:
    plVar9 = (long *)*param_1;
    puVar12 = (undefined8 *)*plVar9;
    if (*(long *)(*(long *)(param_2 + 8) + 0x28) == 0) {
      if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) break;
      UNRECOVERED_JUMPTABLE = (code *)puVar12[1];
      lVar6 = 2;
      pcVar10 = &DAT_000e0847;
      goto LAB_0002de6e;
    }
    if (param_3 != '\0') {
      (*(code *)puVar12[1])(plVar9,&DAT_000e084a,2);
      uVar3 = param_6 + param_5;
      uVar8 = (ulong)uVar3;
      if ((ulong)param_1[0x4d] < uVar8) {
        FUN_000b1a80(param_1 + 0x4c,param_1[0x4d] * 2,0x20);
      }
      lVar6 = *(long *)(*(long *)(param_2 + 8) + 0x18);
      if (*(long *)(*(long *)(param_2 + 8) + 0x28) != 1) {
        uVar13 = 0;
        do {
          plVar9 = (long *)*param_1;
          if (*(code **)(*plVar9 + 8) == FUN_0001ac60) {
            if (0x3fffffffffffffffU - *(long *)(plVar9[1] + 8) < uVar8) goto LAB_0002e6d9;
            FUN_000b2500(plVar9[1],param_1[0x4c],uVar8);
          }
          else {
            (**(code **)(*plVar9 + 8))(plVar9,param_1[0x4c],uVar8);
          }
          puVar12 = (undefined8 *)*param_1;
          if (*(code **)*puVar12 == FUN_0001ae00) {
            FUN_000b1530(puVar12[1],0x22);
          }
          else {
            (**(code **)*puVar12)(puVar12,0x22);
          }
          FUN_00025220(param_1,lVar6 + 0x20,param_4);
          plVar9 = (long *)*param_1;
          if (*(code **)(*plVar9 + 8) == FUN_0001ac60) {
            if (0x3fffffffffffffffU - *(long *)(plVar9[1] + 8) < 3) goto LAB_0002e6d9;
            FUN_000b2500(plVar9[1],&DAT_000e086a,3);
          }
          else {
            (**(code **)(*plVar9 + 8))(plVar9,&DAT_000e086a,3);
          }
          FUN_0002d610(param_1,lVar6 + 0x40,1,param_4,param_5,uVar3);
          plVar9 = (long *)*param_1;
          if (*(code **)(*plVar9 + 8) == FUN_0001ac60) {
            if (0x3fffffffffffffffU - *(long *)(plVar9[1] + 8) < 2) goto LAB_0002e6d9;
            FUN_000b2500(plVar9[1],&DAT_000e085f,2);
          }
          else {
            (**(code **)(*plVar9 + 8))(plVar9,&DAT_000e085f,2);
          }
          uVar13 = uVar13 + 1;
          lVar6 = FUN_00049ce0(lVar6);
        } while (uVar13 < *(long *)(*(long *)(param_2 + 8) + 0x28) - 1U);
      }
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,param_1[0x4c],uVar8);
      puVar12 = (undefined8 *)*param_1;
      if (*(code **)*puVar12 == FUN_0001ae00) {
        FUN_000b1530(puVar12[1],0x22);
      }
      else {
        (**(code **)*puVar12)(puVar12,0x22);
      }
      FUN_00025220(param_1,lVar6 + 0x20,param_4);
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,&DAT_000e086a,3);
      FUN_0002d610(param_1,lVar6 + 0x40,1,param_4,param_5,uVar3);
      puVar12 = (undefined8 *)*param_1;
      UNRECOVERED_JUMPTABLE = *(code **)*puVar12;
      if (UNRECOVERED_JUMPTABLE != FUN_0001ae00) goto LAB_0002e34c;
LAB_0002dada:
      FUN_000b1530(puVar12[1],10);
      goto LAB_0002dae8;
    }
    if ((code *)*puVar12 == FUN_0001ae00) {
      FUN_000b1530(plVar9[1],0x7b);
    }
    else {
      (*(code *)*puVar12)(plVar9,0x7b);
    }
    lVar6 = *(long *)(*(long *)(param_2 + 8) + 0x18);
    if (*(long *)(*(long *)(param_2 + 8) + 0x28) != 1) {
      uVar8 = 0;
      do {
        puVar12 = (undefined8 *)*param_1;
        if (*(code **)*puVar12 == FUN_0001ae00) {
          FUN_000b1530(puVar12[1],0x22);
        }
        else {
          (**(code **)*puVar12)(puVar12,0x22);
        }
        FUN_00025220(param_1,lVar6 + 0x20,param_4);
        plVar9 = (long *)*param_1;
        if (*(code **)(*plVar9 + 8) == FUN_0001ac60) {
          if (0x3fffffffffffffffU - *(long *)(plVar9[1] + 8) < 2) goto LAB_0002e6d9;
          FUN_000b2500(plVar9[1],&DAT_000e0883,2);
        }
        else {
          (**(code **)(*plVar9 + 8))(plVar9,&DAT_000e0883,2);
        }
        FUN_0002d610(param_1,lVar6 + 0x40,0,param_4,param_5,param_6);
        puVar12 = (undefined8 *)*param_1;
        if (*(code **)*puVar12 == FUN_0001ae00) {
          FUN_000b1530(puVar12[1],0x2c);
        }
        else {
          (**(code **)*puVar12)(puVar12,0x2c);
        }
        uVar8 = uVar8 + 1;
        lVar6 = FUN_00049ce0(lVar6);
      } while (uVar8 < *(long *)(*(long *)(param_2 + 8) + 0x28) - 1U);
    }
    puVar12 = (undefined8 *)*param_1;
    if (*(code **)*puVar12 == FUN_0001ae00) {
      FUN_000b1530(puVar12[1],0x22);
    }
    else {
      (**(code **)*puVar12)(puVar12,0x22);
    }
    FUN_00025220(param_1,lVar6 + 0x20,param_4);
    (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,&DAT_000e0883,2);
    FUN_0002d610(param_1,lVar6 + 0x40,0,param_4,param_5,param_6);
LAB_0002e228:
    puVar12 = (undefined8 *)*param_1;
    UNRECOVERED_JUMPTABLE = *(code **)*puVar12;
    if (UNRECOVERED_JUMPTABLE == FUN_0001ae00) {
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        uVar5 = puVar12[1];
        uVar11 = 0x7d;
LAB_0002dd5d:
        FUN_000b1530(uVar5,uVar11);
        return;
      }
      break;
    }
    if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) break;
    goto LAB_0002e4b8;
  case 2:
    plVar9 = (long *)*param_1;
    puVar12 = (undefined8 *)*plVar9;
    if (**(long **)(param_2 + 8) == (*(long **)(param_2 + 8))[1]) {
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        UNRECOVERED_JUMPTABLE = (code *)puVar12[1];
        lVar6 = 2;
        pcVar10 = &DAT_000e7051;
        goto LAB_0002de6e;
      }
    }
    else {
      if (param_3 == '\0') {
        if ((code *)*puVar12 == FUN_0001ae00) {
          FUN_000b1530(plVar9[1],0x5b);
        }
        else {
          (*(code *)*puVar12)(plVar9,0x5b);
        }
        lVar6 = **(long **)(param_2 + 8);
        if (lVar6 != (*(long **)(param_2 + 8))[1] + -0x10) {
          do {
            FUN_0002d610(param_1,lVar6,0,param_4,param_5,param_6);
            puVar12 = (undefined8 *)*param_1;
            if (*(code **)*puVar12 == FUN_0001ae00) {
              FUN_000b1530(puVar12[1],0x2c);
            }
            else {
              (**(code **)*puVar12)(puVar12,0x2c);
            }
            lVar6 = lVar6 + 0x10;
          } while (lVar6 != *(long *)(*(long *)(param_2 + 8) + 8) + -0x10);
        }
        FUN_0002d610(param_1,lVar6,0,param_4,param_5,param_6);
      }
      else {
        (*(code *)puVar12[1])(plVar9,&DAT_000e084d,2);
        uVar3 = param_6 + param_5;
        uVar8 = (ulong)uVar3;
        if ((ulong)param_1[0x4d] < uVar8) {
          FUN_000b1a80(param_1 + 0x4c,param_1[0x4d] * 2,0x20);
        }
        lVar6 = **(long **)(param_2 + 8);
        if (lVar6 != (*(long **)(param_2 + 8))[1] + -0x10) {
          do {
            plVar9 = (long *)*param_1;
            if (*(code **)(*plVar9 + 8) == FUN_0001ac60) {
              if (0x3fffffffffffffffU - *(long *)(plVar9[1] + 8) < uVar8) goto LAB_0002e6d9;
              FUN_000b2500(plVar9[1],param_1[0x4c],uVar8);
            }
            else {
              (**(code **)(*plVar9 + 8))(plVar9,param_1[0x4c],uVar8);
            }
            FUN_0002d610(param_1,lVar6,1,param_4,param_5,uVar3);
            plVar9 = (long *)*param_1;
            if (*(code **)(*plVar9 + 8) == FUN_0001ac60) {
              if (0x3fffffffffffffffU - *(long *)(plVar9[1] + 8) < 2) goto LAB_0002e6d9;
              FUN_000b2500(plVar9[1],&DAT_000e085f,2);
            }
            else {
              (**(code **)(*plVar9 + 8))(plVar9,&DAT_000e085f,2);
            }
            lVar6 = lVar6 + 0x10;
          } while (*(long *)(*(long *)(param_2 + 8) + 8) + -0x10 != lVar6);
        }
        (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,param_1[0x4c],uVar8);
        FUN_0002d610(param_1,*(long *)(*(long *)(param_2 + 8) + 8) + -0x10,1,param_4,param_5,uVar3);
        puVar12 = (undefined8 *)*param_1;
        if (*(code **)*puVar12 == FUN_0001ae00) {
          FUN_000b1530(puVar12[1],10);
        }
        else {
          (**(code **)*puVar12)(puVar12,10);
        }
        (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,param_1[0x4c],param_6);
      }
      puVar12 = (undefined8 *)*param_1;
      UNRECOVERED_JUMPTABLE = *(code **)*puVar12;
      if (UNRECOVERED_JUMPTABLE == FUN_0001ae00) {
        if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
          uVar5 = puVar12[1];
          uVar11 = 0x5d;
          goto LAB_0002dd5d;
        }
      }
      else if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        uVar5 = 0x5d;
        goto LAB_0002e4bd;
      }
    }
    break;
  case 3:
    puVar12 = (undefined8 *)*param_1;
    if (*(code **)*puVar12 == FUN_0001ae00) {
      FUN_000b1530(puVar12[1],0x22);
    }
    else {
      (**(code **)*puVar12)(puVar12,0x22);
    }
    FUN_00025220(param_1,*(undefined8 *)(param_2 + 8),param_4);
    puVar12 = (undefined8 *)*param_1;
    UNRECOVERED_JUMPTABLE = *(code **)*puVar12;
    if (UNRECOVERED_JUMPTABLE == FUN_0001ae00) {
      if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) break;
      uVar5 = puVar12[1];
      uVar11 = 0x22;
      goto LAB_0002dd5d;
    }
    if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) break;
    uVar5 = 0x22;
    goto LAB_0002e4bd;
  case 4:
    UNRECOVERED_JUMPTABLE = *(code **)(*(long *)*param_1 + 8);
    if (param_2[8] == '\0') {
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        uVar5 = 5;
        pcVar10 = "false";
LAB_0002dda5:
                    /* WARNING: Could not recover jumptable at 0x0002ddb3. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*UNRECOVERED_JUMPTABLE)((long *)*param_1,pcVar10,uVar5,UNRECOVERED_JUMPTABLE);
        return;
      }
    }
    else if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
      uVar5 = 4;
      pcVar10 = "true";
      goto LAB_0002dda5;
    }
    break;
  case 5:
    if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
      FUN_00023fa0(param_1,*(undefined8 *)(param_2 + 8));
      return;
    }
    break;
  case 6:
    if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
      FUN_00023c90(param_1,*(undefined8 *)(param_2 + 8));
      return;
    }
    break;
  case 7:
    dVar14 = *(double *)(param_2 + 8);
    if ((double)((ulong)dVar14 & _DAT_000e2ea0) <= DAT_000e2e40) {
      pcVar10 = (char *)(param_1 + 2);
      auVar1._8_8_ = 0;
      auVar1._0_8_ = dVar14;
      uVar3 = movmskpd(in_EAX,auVar1);
      plVar9 = (long *)pcVar10;
      if ((uVar3 & 1) != 0) {
        *(undefined *)(param_1 + 2) = 0x2d;
        dVar14 = (double)((ulong)dVar14 ^ _DAT_000e2eb0);
        plVar9 = (long *)((long)param_1 + 0x11);
      }
      uVar2 = DAT_000e2da2;
      if (dVar14 == 0.0) {
        *(undefined *)((long)plVar9 + 2) = 0x30;
        puVar4 = (undefined *)((long)plVar9 + 3);
        *(undefined2 *)plVar9 = uVar2;
      }
      else {
        local_48 = 0;
        local_44 = 0;
        FUN_0002cf40(plVar9,&local_48,&local_44);
        puVar4 = (undefined *)FUN_0001c360(plVar9,local_48,local_44,0xfffffffc,0xf);
      }
      plVar9 = (long *)*param_1;
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        lVar6 = (long)puVar4 - (long)pcVar10;
        UNRECOVERED_JUMPTABLE = *(code **)(*plVar9 + 8);
        goto LAB_0002de6e;
      }
      break;
    }
    plVar9 = (long *)*param_1;
    if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) break;
    UNRECOVERED_JUMPTABLE = *(code **)(*plVar9 + 8);
LAB_0002de62:
    lVar6 = 4;
    pcVar10 = &DAT_000e0004;
LAB_0002de6e:
                    /* WARNING: Could not recover jumptable at 0x0002de7c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*UNRECOVERED_JUMPTABLE)(plVar9,pcVar10,lVar6);
    return;
  case 8:
    plVar9 = (long *)*param_1;
    if (param_3 != '\0') {
      (**(code **)(*plVar9 + 8))(plVar9,&DAT_000e084a,2);
      uVar8 = (ulong)(uint)(param_6 + param_5);
      if ((ulong)param_1[0x4d] < uVar8) {
        FUN_000b1a80(param_1 + 0x4c,param_1[0x4d] * 2,0x20);
      }
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,param_1[0x4c],uVar8);
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,"\"bytes\": [",10);
      puVar4 = (undefined *)(*(undefined8 **)(param_2 + 8))[1];
      puVar7 = (undefined *)**(undefined8 **)(param_2 + 8);
      if (puVar4 != puVar7) {
        if (puVar7 != puVar4 + -1) {
          do {
            FUN_00023ae0(param_1,*puVar7);
            plVar9 = (long *)*param_1;
            if (*(code **)(*plVar9 + 8) == FUN_0001ac60) {
              if (0x3fffffffffffffffU - *(long *)(plVar9[1] + 8) < 2) goto LAB_0002e6d9;
              FUN_000b2500(plVar9[1],&DAT_000e085b,2);
            }
            else {
              (**(code **)(*plVar9 + 8))(plVar9,&DAT_000e085b,2);
            }
            puVar7 = puVar7 + 1;
            puVar4 = *(undefined **)(*(long *)(param_2 + 8) + 8);
          } while (puVar4 + -1 != puVar7);
        }
        FUN_00023ae0(param_1,puVar4[-1]);
      }
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,&DAT_000e085e,3);
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,param_1[0x4c],uVar8);
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,&DAT_000e0862,0xb);
      if (*(char *)(*(long *)(param_2 + 8) + 0x20) == '\0') {
        (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,&DAT_000e0004,4);
      }
      else {
        FUN_00023c90(param_1,*(undefined8 *)(*(long *)(param_2 + 8) + 0x18));
      }
      puVar12 = (undefined8 *)*param_1;
      UNRECOVERED_JUMPTABLE = *(code **)*puVar12;
      if (UNRECOVERED_JUMPTABLE == FUN_0001ae00) goto LAB_0002dada;
LAB_0002e34c:
      (*UNRECOVERED_JUMPTABLE)(puVar12,10);
LAB_0002dae8:
      (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,param_1[0x4c],param_6);
      goto LAB_0002e228;
    }
    (**(code **)(*plVar9 + 8))(plVar9,"{\"bytes\":[",10);
    puVar4 = (undefined *)(*(undefined8 **)(param_2 + 8))[1];
    puVar7 = (undefined *)**(undefined8 **)(param_2 + 8);
    if (puVar4 != puVar7) {
      if (puVar7 != puVar4 + -1) {
        do {
          FUN_00023ae0(param_1,*puVar7);
          puVar12 = (undefined8 *)*param_1;
          if (*(code **)*puVar12 == FUN_0001ae00) {
            FUN_000b1530(puVar12[1],0x2c);
          }
          else {
            (**(code **)*puVar12)(puVar12,0x2c);
          }
          puVar7 = puVar7 + 1;
          puVar4 = *(undefined **)(*(long *)(param_2 + 8) + 8);
        } while (puVar4 + -1 != puVar7);
      }
      FUN_00023ae0(param_1,puVar4[-1]);
    }
    (**(code **)(*(long *)*param_1 + 8))((long *)*param_1,&DAT_000e0879,0xc);
    if (*(char *)(*(long *)(param_2 + 8) + 0x20) == '\0') {
      plVar9 = (long *)*param_1;
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        lVar6 = 5;
        pcVar10 = "null}";
        UNRECOVERED_JUMPTABLE = *(code **)(*plVar9 + 8);
        goto LAB_0002de6e;
      }
      break;
    }
    FUN_00023c90(param_1,*(undefined8 *)(*(long *)(param_2 + 8) + 0x18));
    puVar12 = (undefined8 *)*param_1;
    if (local_40 != *(long *)(in_FS_OFFSET + 0x28)) break;
    UNRECOVERED_JUMPTABLE = *(code **)*puVar12;
LAB_0002e4b8:
    uVar5 = 0x7d;
LAB_0002e4bd:
                    /* WARNING: Could not recover jumptable at 0x0002e4cb. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*UNRECOVERED_JUMPTABLE)(puVar12,uVar5);
    return;
  case 9:
    plVar9 = (long *)*param_1;
    UNRECOVERED_JUMPTABLE = *(code **)(*plVar9 + 8);
    if (UNRECOVERED_JUMPTABLE == FUN_0001ac60) {
      lVar6 = plVar9[1];
      if (0x3fffffffffffffffU - *(long *)(lVar6 + 8) < 0xb) goto LAB_0002e6d9;
      if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
        uVar5 = 0xb;
        pcVar10 = "<discarded>";
        goto LAB_0002d7d6;
      }
    }
    else if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
      lVar6 = 0xb;
      pcVar10 = "<discarded>";
      goto LAB_0002de6e;
    }
    break;
  default:
    if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
      return;
    }
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


