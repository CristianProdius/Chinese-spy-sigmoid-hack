// ===== FUNC 16680 size=71

void FUN_00016680(void)

{
  long in_RAX;
  long *unaff_RBX;
  
  if (in_RAX == 1) {
    FUN_000410a0();
                    /* try { // try from 0001669a to 000166a3 has its CatchHandler @ 000166c7 */
    FUN_0008d5d0((long)unaff_RBX + *(long *)(*unaff_RBX + -0x18),1);
                    /* WARNING: Subroutine does not return */
    FUN_00041f50();
  }
  FUN_000410a0();
                    /* try { // try from 000166b8 to 000166bc has its CatchHandler @ 000166db */
  FUN_0008d5d0(*(long *)(*unaff_RBX + -0x18) + (long)unaff_RBX,1);
  FUN_00041110();
  return;
}


