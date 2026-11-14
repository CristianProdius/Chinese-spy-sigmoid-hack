// ===== FUNC 13df2 size=107

void FUN_00013df2(void)

{
  undefined8 uVar1;
  undefined *in_RCX;
  undefined *param_7;
  
  param_7 = in_RCX;
  uVar1 = FUN_00040f40(0x20);
  FUN_000137b8(*param_7,"type must be string, but is ");
                    /* try { // try from 00013e2a to 00013e2e has its CatchHandler @ 00013eca */
  FUN_0001df60(&stack0x00000040);
                    /* try { // try from 00013e3a to 00013e3e has its CatchHandler @ 00013ea7 */
  FUN_00013cc9(uVar1,0x12e,&stack0x00000040);
  FUN_000b07c0(&stack0x00000040);
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00013e58 to 00013e5c has its CatchHandler @ 00013e8f */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
}


