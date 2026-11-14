// ===== FUNC 164f2 size=71

void FUN_000164f2(void)

{
  long in_RAX;
  long *unaff_RBX;
  
  if (in_RAX == 1) {
    FUN_000410a0();
                    /* try { // try from 0001650c to 00016515 has its CatchHandler @ 00016539 */
    FUN_0008cbd0((long)unaff_RBX + *(long *)(*unaff_RBX + -0x18),1);
                    /* WARNING: Subroutine does not return */
    FUN_00041f50();
  }
  FUN_000410a0();
                    /* try { // try from 0001652a to 0001652e has its CatchHandler @ 0001654d */
  FUN_0008cbd0(*(long *)(*unaff_RBX + -0x18) + (long)unaff_RBX,1);
  FUN_00041110();
  return;
}


