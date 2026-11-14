// ===== FUNC 14d56 size=105

/* WARNING: Removing unreachable block (ram,0x00014d9e) */
/* WARNING: Removing unreachable block (ram,0x00014d8c) */
/* WARNING: Removing unreachable block (ram,0x00014db0) */

void FUN_00014d56(void)

{
  long unaff_RBX;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
                    /* try { // try from 00014d7b to 00014dbe has its CatchHandler @ 00014dde */
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
    *(undefined8 *)(unaff_RBX + 0x10) = 0;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


