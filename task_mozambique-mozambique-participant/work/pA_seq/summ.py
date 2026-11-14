import sys, re
for f in sys.argv[1:]:
    rows = [l for l in open(f) if l.startswith('map')]
    def stat(rows):
        hp = 0; g = 0; w = 0; d = 0
        for l in rows:
            worst = int(re.search(r'worst (\d)', l).group(1)); hp += worst
            for a, b in re.findall(r's\d:(\d+)-(\d+)', l):
                g += 1; w += int(a) > int(b); d += int(a) == int(b)
        n = len(rows)
        return 'maps %d match %.3f win %.1f%% draw %.1f%%' % (n, hp / (2.0 * n) if n else 0, 100.0 * w / max(1, g), 100.0 * d / max(1, g))
    head = open(f).readline()
    m = re.search(r'"cpu_max": ([\d.]+), "cpu_mean": ([\d.]+)', head)
    print('%-22s all: %s | first24: %s | cpu max/mean %s' % (f.split('/')[-1], stat(rows), stat(rows[:24]), m.groups() if m else '?'))
