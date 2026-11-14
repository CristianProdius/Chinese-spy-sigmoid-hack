// ===== FUNC 21220 size=49

bool FUN_00021220(char *param_1)

{
  char *pcVar1;
  char *pcVar2;
  bool bVar3;
  
  pcVar2 = *(char **)(param_1 + 0x10);
  if (*(char **)(param_1 + 0x10) == (char *)0x0) {
    pcVar2 = param_1;
  }
  bVar3 = false;
  if ((*pcVar2 == '\x02') &&
     (pcVar1 = (char *)**(undefined8 **)(pcVar2 + 8),
     (*(undefined8 **)(pcVar2 + 8))[1] - (long)pcVar1 == 0x20)) {
    bVar3 = *pcVar1 == '\x03';
  }
  return bVar3;
}


