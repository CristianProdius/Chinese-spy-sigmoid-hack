// ===== FUNC 169b0 size=73

void FUN_000169b0(void)

{
  long in_RAX;
  long *unaff_RBP;
  
  if (in_RAX == 1) {
    FUN_000410a0();
                    /* try { // try from 000169cb to 000169d4 has its CatchHandler @ 000169f9 */
    FUN_0008cbd0(*(long *)(*unaff_RBP + -0x18) + (long)unaff_RBP,1);
                    /* WARNING: Subroutine does not return */
    FUN_00041f50();
  }
  FUN_000410a0();
                    /* try { // try from 000169ea to 000169ee has its CatchHandler @ 00016a0d */
  FUN_0008cbd0(*(long *)(*unaff_RBP + -0x18) + (long)unaff_RBP,1);
  FUN_00041110();
  return;
}


