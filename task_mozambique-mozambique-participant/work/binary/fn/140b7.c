// ===== FUNC 140b7 size=95

void FUN_000140b7(void)

{
  undefined8 uVar1;
  undefined *unaff_RBX;
  
  uVar1 = FUN_00040f40(0x20);
  FUN_000137b8(*unaff_RBX,"type must be number, but is ");
                    /* try { // try from 000140e3 to 000140e7 has its CatchHandler @ 00014144 */
  FUN_0001df60(&stack0x00000010);
                    /* try { // try from 000140f3 to 000140f7 has its CatchHandler @ 00014129 */
  FUN_00013cc9(uVar1,0x12e,&stack0x00000010);
  FUN_000b07c0(&stack0x00000010);
                    /* WARNING: Subroutine does not return */
  FUN_00041f00(uVar1,&PTR_PTR_FUN_0011cc70,FUN_0001ab10);
}


