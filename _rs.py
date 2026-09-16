# -*- coding: utf-8 -*-
import io, re, sys

F, MECH, ANA, LAB, PRAC, LABFILE, LO, HI = sys.argv[1:9]
LO, HI = int(LO), int(HI)          # dai so muc co che can dich (vd 2 8)

L = io.open(F, encoding="utf-8").read().split("\n")
def find(p):
    for i, x in enumerate(L):
        if x.startswith(p): return i
    raise SystemExit("KHONG THAY: " + p)

iM, iA, iL, iP = find(MECH), find(ANA), find(LAB), find(PRAC)

# 1) tach LAB
io.open(LABFILE, "w", encoding="utf-8", newline="\n").write(
    io.open("_lh.md", encoding="utf-8").read() + "\n".join(L[iL:iP-2]))

# 2) dao thu tu + chen con tro LAB
ptr = io.open("_lp.md", encoding="utf-8").read().rstrip("\n").split("\n")
new = L[:iM] + L[iA:iL-2] + ["", "---", ""] + L[iM:iA-2] + ptr + ["", "---", ""] + L[iP:]
io.open(F, "w", encoding="utf-8", newline="\n").write("\n".join(new))

# 3) danh so lai
L = io.open(F, encoding="utf-8").read().split("\n")
iA, iM = find(ANA), find(MECH)
iE = find("## 🧪 PHẦN 3")
ana_n = re.match(r'^## .{0,6}?(\d+)\.', ANA).group(1)
for i in range(iA, iM):
    L[i] = re.sub(r'^### %s\.' % ana_n, '### 2.', L[i])
for n in range(HI, LO-1, -1):
    for i in range(iM, iE):
        L[i] = re.sub(r'^(## .{0,14}?)%d\. ' % n, r'\g<1>%d. ' % (n+1), L[i], count=1)
        L[i] = re.sub(r'^### %d\.' % n, '### %d.' % (n+1), L[i], count=1)
io.open(F, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("OK %s -> %d dong | %s -> %d dong" % (F, len(L), LABFILE,
      len(io.open(LABFILE, encoding="utf-8").read().split("\n"))))
