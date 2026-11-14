#!/bin/bash
# usage: dis.sh START END (hex) - print disassembly lines in [START,END)
awk -v lo=$((16#$1)) -v hi=$((16#$2)) '/^ +[0-9a-f]+:/{a=$1; sub(":","",a); n=strtonum("0x"a); if(n>=lo && n<hi) print; if(n>=hi) exit}' "$(dirname "$0")/engine.asm" | sed 's/<__cxa_finalize@plt+0x[0-9a-f]*>//; s/QWORD PTR /q/g; s/DWORD PTR /d/g; s/BYTE PTR /b/g; s/XMMWORD PTR /x/g; s/WORD PTR /w/g'
