// ===== FUNC 16a22 size=73

void FUN_00016a22(void)

{
  long in_RAX;
  long *unaff_RBP;
  
  if (in_RAX == 1) {
    FUN_000410a0();
                    /* try { // try from 00016a3d to 00016a46 has its CatchHandler @ 00016a6b */
    FUN_0008d5d0(*(long *)(*unaff_RBP + -0x18) + (long)unaff_RBP,1);
                    /* WARNING: Subroutine does not return */
    FUN_00041f50();
  }
  FUN_000410a0();
                    /* try { // try from 00016a5c to 00016a60 has its CatchHandler @ 00016a7f */
  FUN_0008d5d0(*(long *)(*unaff_RBP + -0x18) + (long)unaff_RBP,1);
  FUN_00041110();
  return;
}


