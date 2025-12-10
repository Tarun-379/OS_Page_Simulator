def format_input(s):
    s = s.replace(';', ',').strip()
    parts = [p.strip() for p in s.split(',') if p.strip()!='']
    out = []
    for p in parts:
        try:
            out.append(int(p))
        except:
            out.append(p)
    return out

def fifo(refs, frames):
    fr = [None]*frames
    q = []
    steps = []
    for page in refs:
        hit = page in fr
        evicted = None
        if not hit:
            if None in fr:
                i = fr.index(None)
                fr[i] = page
                q.append(i)
            else:
                ev = q.pop(0)
                evicted = fr[ev]
                fr[ev] = page
                q.append(ev)
        steps.append((page, fr.copy(), hit, evicted))
    return steps

def lru(refs, frames):
    fr = [None]*frames
    last = {}
    steps = []
    for t, page in enumerate(refs):
        hit = page in fr
        evicted = None
        if hit:
            last[page] = t
        else:
            if None in fr:
                i = fr.index(None)
                fr[i] = page
                last[page] = t
            else:
                lru_p = min(((last.get(p, -1), p) for p in fr))[1]
                i = fr.index(lru_p)
                evicted = lru_p
                last.pop(lru_p, None)
                fr[i] = page
                last[page] = t
        steps.append((page, fr.copy(), hit, evicted))
    return steps

def optimal(refs, frames):
    fr = [None]*frames
    steps = []
    n = len(refs)
    for i, page in enumerate(refs):
        hit = page in fr
        evicted = None
        if not hit:
            if None in fr:
                j = fr.index(None)
                fr[j] = page
            else:
                ev_idx = 0
                farthest = -1
                for j, p in enumerate(fr):
                    next_use = None
                    for k in range(i+1, n):
                        if refs[k] == p:
                            next_use = k
                            break
                    if next_use is None:
                        ev_idx = j
                        farthest = float('inf')
                        break
                    if next_use > farthest:
                        farthest = next_use
                        ev_idx = j
                evicted = fr[ev_idx]
                fr[ev_idx] = page
        steps.append((page, fr.copy(), hit, evicted))
    return steps

ALGS = {'FIFO': fifo, 'LRU': lru, 'Optimal': optimal}

def format_frames(fr):
    return ' '.join('[{:^3}]'.format('-' if x is None else x) for x in fr)

s = input("Reference string (e.g. 1,2,3,4,5): ").strip()
if not s:
    print("Empty reference string provided.")
    raise SystemExit(1)
refs = format_input(s)

try:
    frames = int(input("Frames : ").strip())
    if frames <= 0:
        print("Frames must be positive. Using default value: 3.")
        frames = 3
except:
    print("Invalid frames — using default value: 3.")
    frames = 3

alg = input("Algorithm (FIFO / LRU / Optimal) [LRU]: ").strip() or 'LRU'
if alg not in ALGS:
    alg = 'LRU'

steps = ALGS[alg](refs, frames)
hits = sum(1 for s in steps if s[2])

print("\nAlgorithm:", alg, "| Frames:", frames)
print("="*65)
print(f"{'Step':<6}{'Page':<8}{'Frames':<35}{'Result':<8}{'Evicted'}")
print("-"*65)

for i, (page, fr, hit, evicted) in enumerate(steps, start=1):
    status = "Hit" if hit else "Miss"
    fr_text = format_frames(fr)
    evicted_text = evicted if evicted is not None else "-"
    print(f"{i:<6}{str(page):<8}{fr_text:<35}{status:<8}{evicted_text}")

print("-"*65)

total = len(steps)
misses = total - hits
ratio = (hits/total*100) if total else 0.0

print(f"Total Accesses : {total}")
print(f"Hits           : {hits}")
print(f"Misses         : {misses}")
print(f"Hit Ratio      : {ratio:.2f}%")
print("="*65)