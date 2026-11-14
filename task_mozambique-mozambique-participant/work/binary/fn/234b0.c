// ===== FUNC 234b0 size=1380

long FUN_000234b0(long param_1,long param_2,int param_3,undefined8 *param_4)

{
  size_t sVar1;
  char *pcVar2;
  long in_FS_OFFSET;
  long *local_88;
  ulong local_80;
  long local_78 [2];
  undefined *local_68;
  ulong local_60;
  undefined local_58;
  undefined7 uStack_57;
  long local_40;
  
  local_40 = *(long *)(in_FS_OFFSET + 0x28);
  FUN_00018b10(param_1,"syntax error ");
  if (param_4[1] != 0) {
    local_60 = 0;
    local_58 = 0;
    local_68 = &local_58;
                    /* try { // try from 00023517 to 0002355e has its CatchHandler @ 00023ac3 */
    FUN_000b1110(&local_68,param_4[1] + 0xf);
    FUN_00017ba0(&local_68,"while parsing ");
    if (0x3fffffffffffffff - local_60 < (ulong)param_4[1]) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00023a33 to 00023a37 has its CatchHandler @ 00023ac3 */
      FUN_00015e26("basic_string::append",*param_4);
    }
    FUN_000b2500(&local_68);
    FUN_000b1530(&local_68,0x20);
    if (0x3fffffffffffffffU - *(long *)(param_1 + 8) < local_60) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00023a70 to 00023a74 has its CatchHandler @ 00023aa3 */
      FUN_00015e26("basic_string::append",local_68);
    }
                    /* try { // try from 00023583 to 00023587 has its CatchHandler @ 00023aa3 */
    FUN_000b2500(param_1);
    if (local_68 != &local_58) {
      thunk_FUN_000d36e0(local_68,CONCAT71(uStack_57,local_58) + 1);
    }
  }
  if (0x3fffffffffffffffU - *(long *)(param_1 + 8) < 2) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00023a53 to 00023a57 has its CatchHandler @ 00023a99 */
    FUN_00015e26("basic_string::append");
  }
                    /* try { // try from 000235c7 to 000235fe has its CatchHandler @ 00023a99 */
  FUN_000b2500(param_1,&DAT_000e05c4,2);
  if (*(int *)(param_2 + 0x20) == 0xe) {
    FUN_00023340(&local_88,param_2 + 0x28);
    local_58 = 0;
    pcVar2 = *(char **)(param_2 + 0x98);
    local_60 = 0;
    local_68 = &local_58;
    sVar1 = strlen(pcVar2);
                    /* try { // try from 00023638 to 0002368c has its CatchHandler @ 00023ac5 */
    FUN_000b1110(&local_68,local_80 + 0xf + sVar1);
    FUN_00017ba0(&local_68,pcVar2);
    FUN_00017ba0(&local_68,"; last read: \'");
    if (0x3fffffffffffffff - local_60 < local_80) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00023a94 to 00023a98 has its CatchHandler @ 00023ac5 */
      FUN_00015e26("basic_string::append",local_88);
    }
    FUN_000b2500(&local_68);
    FUN_000b1530(&local_68,0x27);
    if (0x3fffffffffffffffU - *(long *)(param_1 + 8) < local_60) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00023a88 to 00023a8c has its CatchHandler @ 00023aca */
      FUN_00015e26("basic_string::append",local_68);
    }
                    /* try { // try from 000236b1 to 000236b5 has its CatchHandler @ 00023aca */
    FUN_000b2500(param_1);
    if (local_68 != &local_58) {
      thunk_FUN_000d36e0(local_68,CONCAT71(uStack_57,local_58) + 1);
    }
    if (local_88 != local_78) {
      thunk_FUN_000d36e0(local_88,local_78[0] + 1);
    }
  }
  else {
    switch(*(int *)(param_2 + 0x20)) {
    case 0:
      pcVar2 = "<uninitialized>";
      break;
    case 1:
      pcVar2 = "true literal";
      break;
    case 2:
      pcVar2 = "false literal";
      break;
    case 3:
      pcVar2 = "null literal";
      break;
    case 4:
      pcVar2 = "string literal";
      break;
    case 5:
    case 6:
    case 7:
      pcVar2 = "number literal";
      break;
    case 8:
      pcVar2 = "\'[\'";
      break;
    case 9:
      pcVar2 = "\'{\'";
      break;
    case 10:
      pcVar2 = "\']\'";
      break;
    case 0xb:
      pcVar2 = "\'}\'";
      break;
    case 0xc:
      pcVar2 = "\':\'";
      break;
    case 0xd:
      pcVar2 = "\',\'";
      break;
    default:
      pcVar2 = "unknown token";
      break;
    case 0xf:
      pcVar2 = "end of input";
      break;
    case 0x10:
      pcVar2 = "\'[\', \'{\', or a literal";
    }
    local_58 = 0;
    local_60 = 0;
    local_68 = &local_58;
    sVar1 = strlen(pcVar2);
                    /* try { // try from 0002377c to 0002379a has its CatchHandler @ 00023aa7 */
    FUN_000b1110(&local_68,sVar1 + 0xb);
    FUN_00017ba0(&local_68,"unexpected ");
    FUN_00017ba0(&local_68,pcVar2);
    if (0x3fffffffffffffffU - *(long *)(param_1 + 8) < local_60) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00023a64 to 00023a68 has its CatchHandler @ 00023aa9 */
      FUN_00015e26("basic_string::append",local_68);
    }
                    /* try { // try from 000237bf to 000237c3 has its CatchHandler @ 00023aa9 */
    FUN_000b2500(param_1);
    if (local_68 != &local_58) {
      thunk_FUN_000d36e0(local_68,CONCAT71(uStack_57,local_58) + 1);
    }
  }
  if (param_3 != 0) {
    switch(param_3) {
    case 1:
      pcVar2 = "true literal";
      break;
    case 2:
      pcVar2 = "false literal";
      break;
    case 3:
      pcVar2 = "null literal";
      break;
    case 4:
      pcVar2 = "string literal";
      break;
    case 5:
    case 6:
    case 7:
      pcVar2 = "number literal";
      break;
    case 8:
      pcVar2 = "\'[\'";
      break;
    case 9:
      pcVar2 = "\'{\'";
      break;
    case 10:
      pcVar2 = "\']\'";
      break;
    case 0xb:
      pcVar2 = "\'}\'";
      break;
    case 0xc:
      pcVar2 = "\':\'";
      break;
    case 0xd:
      pcVar2 = "\',\'";
      break;
    case 0xe:
      pcVar2 = "<parse error>";
      break;
    case 0xf:
      pcVar2 = "end of input";
      break;
    case 0x10:
      pcVar2 = "\'[\', \'{\', or a literal";
      break;
    default:
      pcVar2 = "unknown token";
    }
    local_60 = 0;
    local_58 = 0;
    local_68 = &local_58;
    sVar1 = strlen(pcVar2);
                    /* try { // try from 00023812 to 00023830 has its CatchHandler @ 00023aa5 */
    FUN_000b1110(&local_68,sVar1 + 0xb);
    FUN_00017ba0(&local_68,"; expected ");
    FUN_00017ba0(&local_68,pcVar2);
    if (0x3fffffffffffffffU - *(long *)(param_1 + 8) < local_60) {
                    /* WARNING: Subroutine does not return */
                    /* try { // try from 00023a7c to 00023a80 has its CatchHandler @ 00023a9e */
      FUN_00015e26("basic_string::append",local_68);
    }
                    /* try { // try from 00023855 to 00023859 has its CatchHandler @ 00023a9e */
    FUN_000b2500(param_1);
    if (local_68 != &local_58) {
      thunk_FUN_000d36e0(local_68,CONCAT71(uStack_57,local_58) + 1);
    }
  }
  if (local_40 == *(long *)(in_FS_OFFSET + 0x28)) {
    return param_1;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}


