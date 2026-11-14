#!/bin/bash
# strip local declarations and stack-protector noise from a decompiled function
grep -v -E "^\s*(undefined[0-9]*|long|int|char|ulong|uint|byte|double|bool|void|undefined|float|short|ushort)\s*\**\s*\(?\**[a-zA-Z_0-9]+\)?(\s*\[[0-9]+\])*;\s*$" "$1" | grep -v -E "__stack_chk_fail|in_FS_OFFSET|WARNING: Subroutine|try \{ // try from"
