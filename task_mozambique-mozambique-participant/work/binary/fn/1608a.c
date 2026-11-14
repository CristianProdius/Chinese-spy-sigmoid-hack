// ===== FUNC 1608a size=15

void FUN_0001608a(void)

{
  long *unaff_RBX;
  undefined4 unaff_R12D;
  
  FUN_000410a0();
                    /* try { // try from 0001608f to 00016093 has its CatchHandler @ 00016099 */
  FUN_00041110();
  while (unaff_RBX = (long *)*unaff_RBX, unaff_RBX != (long *)0x0) {
    (*(code *)unaff_RBX[1])(unaff_R12D);
  }
  return;
}


