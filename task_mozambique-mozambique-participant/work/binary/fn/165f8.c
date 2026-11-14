// ===== FUNC 165f8 size=95

void FUN_000165f8(void)

{
  long in_RAX;
  long *unaff_RBX;
  long lVar1;
  long unaff_R12;
  undefined4 *unaff_R13;
  
  if (in_RAX != 1) {
    FUN_000410a0();
                    /* try { // try from 00016633 to 00016637 has its CatchHandler @ 0001666b */
    FUN_0008d5d0(*(long *)(*unaff_RBX + -0x18) + (long)unaff_RBX,1);
    FUN_00041110();
    if (0 < unaff_R12) {
      *unaff_R13 = 0;
    }
    if (unaff_RBX[1] == 0) {
      lVar1 = *(long *)(*unaff_RBX + -0x18) + (long)unaff_RBX;
      FUN_0008d580(lVar1,*(uint *)(lVar1 + 0x20) | 4);
    }
    return;
  }
  FUN_000410a0();
                    /* try { // try from 00016615 to 0001661e has its CatchHandler @ 00016657 */
  FUN_0008d5d0((long)unaff_RBX + *(long *)(*unaff_RBX + -0x18),1);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


