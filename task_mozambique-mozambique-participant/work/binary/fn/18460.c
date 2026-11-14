// ===== FUNC 18460 size=735

void FUN_00018460(long param_1)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  long local_48;
  
  local_48 = param_1;
  if (param_1 != 0) {
    do {
      lVar9 = *(long *)(local_48 + 0x18);
      while (lVar9 != 0) {
        lVar8 = *(long *)(lVar9 + 0x18);
        while (lVar8 != 0) {
          lVar7 = *(long *)(lVar8 + 0x18);
          while (lVar7 != 0) {
            lVar5 = *(long *)(lVar7 + 0x18);
            while (lVar5 != 0) {
              lVar3 = *(long *)(lVar5 + 0x18);
              while (lVar3 != 0) {
                lVar4 = *(long *)(lVar3 + 0x18);
                while (lVar4 != 0) {
                  lVar6 = *(long *)(lVar4 + 0x18);
                  while (lVar6 != 0) {
                    lVar2 = *(long *)(lVar6 + 0x18);
                    while (lVar2 != 0) {
                      FUN_00018460(*(undefined8 *)(lVar2 + 0x18));
                      lVar1 = *(long *)(lVar2 + 0x10);
                      if (*(long *)(lVar2 + 0x20) != lVar2 + 0x30) {
                        thunk_FUN_000d36e0(*(long *)(lVar2 + 0x20),*(long *)(lVar2 + 0x30) + 1);
                      }
                      thunk_FUN_000d36e0(lVar2,0x40);
                      lVar2 = lVar1;
                    }
                    lVar2 = *(long *)(lVar6 + 0x10);
                    if (*(long *)(lVar6 + 0x20) != lVar6 + 0x30) {
                      thunk_FUN_000d36e0(*(long *)(lVar6 + 0x20),*(long *)(lVar6 + 0x30) + 1);
                    }
                    thunk_FUN_000d36e0(lVar6,0x40);
                    lVar6 = lVar2;
                  }
                  lVar6 = *(long *)(lVar4 + 0x10);
                  if (*(long *)(lVar4 + 0x20) != lVar4 + 0x30) {
                    thunk_FUN_000d36e0(*(long *)(lVar4 + 0x20),*(long *)(lVar4 + 0x30) + 1);
                  }
                  thunk_FUN_000d36e0(lVar4,0x40);
                  lVar4 = lVar6;
                }
                lVar4 = *(long *)(lVar3 + 0x10);
                if (*(long *)(lVar3 + 0x20) != lVar3 + 0x30) {
                  thunk_FUN_000d36e0(*(long *)(lVar3 + 0x20),*(long *)(lVar3 + 0x30) + 1);
                }
                thunk_FUN_000d36e0(lVar3,0x40);
                lVar3 = lVar4;
              }
              lVar3 = *(long *)(lVar5 + 0x10);
              if (*(long *)(lVar5 + 0x20) != lVar5 + 0x30) {
                thunk_FUN_000d36e0(*(long *)(lVar5 + 0x20),*(long *)(lVar5 + 0x30) + 1);
              }
              thunk_FUN_000d36e0(lVar5,0x40);
              lVar5 = lVar3;
            }
            lVar5 = *(long *)(lVar7 + 0x10);
            if (*(long *)(lVar7 + 0x20) != lVar7 + 0x30) {
              thunk_FUN_000d36e0(*(long *)(lVar7 + 0x20),*(long *)(lVar7 + 0x30) + 1);
            }
            thunk_FUN_000d36e0(lVar7,0x40);
            lVar7 = lVar5;
          }
          lVar7 = *(long *)(lVar8 + 0x10);
          if (*(long *)(lVar8 + 0x20) != lVar8 + 0x30) {
            thunk_FUN_000d36e0(*(long *)(lVar8 + 0x20),*(long *)(lVar8 + 0x30) + 1);
          }
          thunk_FUN_000d36e0(lVar8,0x40);
          lVar8 = lVar7;
        }
        lVar8 = *(long *)(lVar9 + 0x10);
        if (*(long *)(lVar9 + 0x20) != lVar9 + 0x30) {
          thunk_FUN_000d36e0(*(long *)(lVar9 + 0x20),*(long *)(lVar9 + 0x30) + 1);
        }
        thunk_FUN_000d36e0(lVar9,0x40);
        lVar9 = lVar8;
      }
      lVar9 = *(long *)(local_48 + 0x10);
      if (*(long *)(local_48 + 0x20) != local_48 + 0x30) {
        thunk_FUN_000d36e0(*(long *)(local_48 + 0x20),*(long *)(local_48 + 0x30) + 1);
      }
      thunk_FUN_000d36e0(local_48,0x40);
      local_48 = lVar9;
    } while (lVar9 != 0);
  }
  return;
}


