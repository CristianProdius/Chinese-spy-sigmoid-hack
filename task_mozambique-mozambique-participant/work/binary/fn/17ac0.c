// ===== FUNC 17ac0 size=54

void _FINI_0(void)

{
  if (DAT_00123181 == '\0') {
    if (PTR___cxa_finalize_00122c18 != (undefined *)0x0) {
      __cxa_finalize(PTR_LOOP_00123008);
    }
    FUN_00017a50();
    DAT_00123181 = 1;
    return;
  }
  return;
}


