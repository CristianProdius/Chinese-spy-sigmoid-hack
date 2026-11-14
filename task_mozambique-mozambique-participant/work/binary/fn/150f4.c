// ===== FUNC 150f4 size=105

/* WARNING: Removing unreachable block (ram,0x0001513c) */
/* WARNING: Removing unreachable block (ram,0x0001512a) */
/* WARNING: Removing unreachable block (ram,0x0001514e) */

void FUN_000150f4(void)

{
  long unaff_RBX;
  
  FUN_000410a0();
  if (*(long **)(unaff_RBX + 0x10) != (long *)0x0) {
                    /* try { // try from 00015119 to 0001515c has its CatchHandler @ 0001517c */
    (**(code **)(**(long **)(unaff_RBX + 0x10) + 8))();
    *(undefined8 *)(unaff_RBX + 0x10) = 0;
  }
                    /* WARNING: Subroutine does not return */
  FUN_00041f50();
}


