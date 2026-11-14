// ===== FUNC 243f0 size=261

long * FUN_000243f0(long *param_1,char *param_2,undefined8 *param_3,undefined *param_4)

{
  undefined uVar1;
  long lVar2;
  size_t sVar3;
  long *plVar4;
  ulong uVar5;
  
  *param_1 = (long)(param_1 + 2);
  param_1[1] = 0;
  *(undefined *)(param_1 + 2) = 0;
  sVar3 = strlen(param_2);
                    /* try { // try from 0002442c to 000244fe has its CatchHandler @ 000244ff */
  FUN_000b1110(param_1,param_3[1] + 1 + sVar3);
  sVar3 = strlen(param_2);
  if (0x3fffffffffffffffU - param_1[1] < sVar3) {
                    /* WARNING: Subroutine does not return */
    FUN_00015e26("basic_string::append");
  }
  FUN_000b2500(param_1,param_2);
  if ((ulong)param_3[1] <= 0x3fffffffffffffffU - param_1[1]) {
    FUN_000b2500(param_1);
    lVar2 = param_1[1];
    plVar4 = (long *)*param_1;
    uVar1 = *param_4;
    if (param_1 + 2 == plVar4) {
      uVar5 = 0xf;
    }
    else {
      uVar5 = param_1[2];
    }
    if (uVar5 < lVar2 + 1U) {
      FUN_000b0b90(param_1,lVar2,0,0,1);
      plVar4 = (long *)*param_1;
    }
    *(undefined *)((long)plVar4 + lVar2) = uVar1;
    param_1[1] = lVar2 + 1U;
    *(undefined *)(*param_1 + 1 + lVar2) = 0;
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00015e26("basic_string::append",*param_3);
}


