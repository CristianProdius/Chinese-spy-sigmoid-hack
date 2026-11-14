// ===== FUNC 176d0 size=108

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void _INIT_2(void)

{
  _DAT_001231c0 = 0;
  _DAT_001231d8 = 0x11c00;
  _DAT_001231a0 = (undefined  [16])0x0;
  _DAT_001231b0 = (undefined  [16])0x0;
  DAT_001231c8 = (undefined8 *)malloc(0x11c00);
  DAT_001231d0 = DAT_001231c8;
  if (DAT_001231c8 == (undefined8 *)0x0) {
    _DAT_001231d8 = 0;
  }
  else {
    *DAT_001231c8 = 0x11c00;
    DAT_001231c8[1] = 0;
  }
  return;
}


