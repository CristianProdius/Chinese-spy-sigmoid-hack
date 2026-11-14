// ===== FUNC 16561 size=39

void FUN_00016561(void)

{
  long in_RAX;
  long lVar1;
  long *unaff_R13;
  
  if (in_RAX != 1) {
    FUN_000410a0();
    FUN_0008cbd0(*(long *)(*unaff_R13 + -0x18) + (long)unaff_R13,1);
    FUN_00041110();
    lVar1 = *(long *)(*unaff_R13 + -0x18) + (long)unaff_R13;
    FUN_0008cb80(lVar1,*(uint *)(lVar1 + 0x20) | 4);
    return;
  }
  FUN_000410a0();
                    /* try { // try from 0001657e to 00016587 has its CatchHandler @ 000165e4 */
  FUN_0008cbd0(*(long *)(*unaff_R13 + -0x18) + (long)unaff_R13,1);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


