// ===== FUNC 1646c size=94

void FUN_0001646c(void)

{
  long in_RAX;
  long *unaff_RBX;
  long lVar1;
  long unaff_R12;
  undefined *unaff_R13;
  
  if (in_RAX != 1) {
    FUN_000410a0();
                    /* try { // try from 000164a7 to 000164ab has its CatchHandler @ 000164de */
    FUN_0008cbd0(*(long *)(*unaff_RBX + -0x18) + (long)unaff_RBX,1);
    FUN_00041110();
    if (0 < unaff_R12) {
      *unaff_R13 = 0;
    }
    if (unaff_RBX[1] == 0) {
      lVar1 = *(long *)(*unaff_RBX + -0x18) + (long)unaff_RBX;
      FUN_0008cb80(lVar1,*(uint *)(lVar1 + 0x20) | 4);
    }
    return;
  }
  FUN_000410a0();
                    /* try { // try from 00016489 to 00016492 has its CatchHandler @ 000164ca */
  FUN_0008cbd0((long)unaff_RBX + *(long *)(*unaff_RBX + -0x18),1);
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


