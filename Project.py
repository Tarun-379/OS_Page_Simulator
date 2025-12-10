import tkinter as tk
from tkinter import ttk, messagebox

def format_input(s):
    if s is None:
        return []
    t = s.strip().replace(";", ",")
    if "," in t:
        parts = [x.strip() for x in t.split(",") if x.strip()]
    else:
        parts = [x.strip() for x in t.split() if x.strip()]
    out = []
    for token in parts:
        try:
            out.append(int(token))
        except:
            messagebox.showerror("Error", f"Invalid number: {token}")
            return []
    return out

parse_refs = format_input

def fifo(refs, frames):
    fr = [None] * frames
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
                ev_idx = q.pop(0)
                evicted = fr[ev_idx]
                fr[ev_idx] = page
                q.append(ev_idx)
        steps.append({"page": page, "frames": fr.copy(), "hit": hit, "evicted": evicted})
    return steps

def lru(refs, frames):
    fr = [None] * frames
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
        steps.append({"page": page, "frames": fr.copy(), "hit": hit, "evicted": evicted})
    return steps

def optimal(refs, frames):
    fr = [None] * frames
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
                    for k in range(i + 1, n):
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
        steps.append({"page": page, "frames": fr.copy(), "hit": hit, "evicted": evicted})
    return steps

ALGS = {"FIFO": fifo, "LRU": lru, "Optimal": optimal}

class CenteredSim(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Page Replacement Simulator (Enhanced)")
        self.geometry("860x700")
        self.refs = []
        self.steps = []
        self.index = 0
        self.frames = 3
        self._build()
        self._build_table()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=12)
        ttk.Label(top, text="Reference string:").grid(row=0, column=0)
        self.e_refs = ttk.Entry(top, width=40)
        self.e_refs.grid(row=0, column=1, padx=6)

        self.e_refs.insert(0, "3,3,3,2,2,4,5,6,54,3,2,54,8,2,2,8")

        ttk.Label(top, text="Frames:").grid(row=0, column=2)
        self.spin = tk.Spinbox(top, from_=1, to=10, width=5)
        self.spin.grid(row=0, column=3, padx=6)
        self.spin.delete(0, "end")
        self.spin.insert(0, "3")

        ttk.Label(top, text="Algorithm:").grid(row=0, column=4)
        self.alg = ttk.Combobox(top, values=list(ALGS.keys()), state="readonly", width=10)
        self.alg.grid(row=0, column=5, padx=6)
        self.alg.set("LRU")

        btns = ttk.Frame(self)
        btns.pack(pady=8)
        ttk.Button(btns, text="Prepare", command=self.prepare).pack(side="left", padx=5)
        ttk.Button(btns, text="◀️ Back", command=self.back).pack(side="left", padx=5)
        ttk.Button(btns, text="Step ▶️", command=self.step).pack(side="left", padx=5)
        ttk.Button(btns, text="Run to End", command=self.run_end).pack(side="left", padx=5)
        ttk.Button(btns, text="Show Table ▼", command=self.show_table).pack(side="left", padx=5)

        main = ttk.Frame(self)
        main.pack(pady=10)
        ttk.Label(main, text="Frames:", font=("Segoe UI", 12, "bold")).pack()
        self.fr_box = ttk.Frame(main)
        self.fr_box.pack(pady=6)
        self.result_lbl = ttk.Label(main, text="Result: -", font=("Segoe UI", 14))
        self.result_lbl.pack()
        self.page_lbl = ttk.Label(main, text="Page: -", font=("Segoe UI", 12))
        self.page_lbl.pack()
        self.metrics_lbl = ttk.Label(main, text="Hits: 0 | Misses: 0", font=("Segoe UI", 12))
        self.metrics_lbl.pack()
        self._make_frame_labels(self.frames)

    def _build_table(self):
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=12, pady=6)
        self.tree = ttk.Treeview(table_frame, show="headings", height=12)
        self.tree.pack(side="left", fill="both", expand=True)
        vs = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vs.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.tag_configure("hit", background="#D1FADF", foreground="black")
        self.tree.tag_configure("miss", background="#FECACA", foreground="black")

    def show_table(self):
        if not self.steps:
            messagebox.showinfo("Info", "Run simulation first.")
            return
        self.update_table()

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        columns = ["Step", "Page"] + [f"F{i+1}" for i in range(self.frames)] + ["Result"]
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=70)
        for i, st in enumerate(self.steps, start=1):
            page = st["page"]
            frames = [str(f) if f is not None else "-" for f in st["frames"]]
            result = "HIT" if st["hit"] else "MISS"
            tag = "hit" if st["hit"] else "miss"
            self.tree.insert("", "end",
                             values=[i, page] + frames + [result],
                             tags=(tag,))

    def _make_frame_labels(self, frames):
        for w in self.fr_box.winfo_children():
            w.destroy()
        self.frame_labels = []
        for i in range(frames):
            lbl = tk.Label(self.fr_box, text="—", width=8, height=2,
                           relief="solid", font=("Segoe UI", 14))
            lbl.grid(row=0, column=i, padx=6)
            self.frame_labels.append(lbl)

    def prepare(self):
        s = self.e_refs.get().strip()
        if not s:
            return messagebox.showerror("Error", "Enter reference string")
        self.refs = parse_refs(s)
        if not self.refs:
            return
        try:
            self.frames = int(self.spin.get())
        except:
            return messagebox.showerror("Error", "Invalid frames")
        alg = self.alg.get()
        fn = ALGS.get(alg, lru)
        self.steps = fn(self.refs, self.frames)
        self.index = 0
        self._make_frame_labels(self.frames)
        self._update_display()

    def _update_display(self):
        if not self.steps:
            return
        st = self.steps[self.index]
        for i, lbl in enumerate(self.frame_labels):
            lbl.config(text=st["frames"][i] if st["frames"][i] is not None else "-")
        self.page_lbl.config(text=f"Page: {st['page']}")
        self.result_lbl.config(text="HIT" if st["hit"] else "MISS", foreground="black")
        hits = sum(1 for x in self.steps[:self.index+1] if x["hit"])
        misses = (self.index+1) - hits
        self.metrics_lbl.config(text=f"Hits: {hits} | Misses: {misses}")

    def step(self):
        if self.index < len(self.steps)-1:
            self.index += 1
            self._update_display()

    def back(self):
        if self.index > 0:
            self.index -= 1
            self._update_display()

    def run_end(self):
        if self.steps:
            self.index = len(self.steps)-1
            self._update_display()

if __name__ == "__main__":
    app = CenteredSim()
    app.mainloop()