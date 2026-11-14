// ===== FUNC 16588 size=72

void FUN_00016588(void)

{
  long lVar1;
  long unaff_R12;
  long *unaff_R13;
  
  FUN_000437a0();
  if (unaff_R12 != 1) {
    FUN_000410a0();
                    /* try { // try from 000165af to 000165b3 has its CatchHandler @ 000165d0 */
    FUN_0008cbd0(*(long *)(*unaff_R13 + -0x18) + (long)unaff_R13,1);
    FUN_00041110();
    lVar1 = *(long *)(*unaff_R13 + -0x18) + (long)unaff_R13;
    FUN_0008cb80(lVar1,*(uint *)(lVar1 + 0x20) | 4);
    return;
  }
  FUN_000410a0();
  FUN_0008cbd0(*(long *)(*unaff_R13 + -0x18) + (long)unaff_R13,1);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


