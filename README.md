# OS_Page_Simulator


🟦 1. FIFO (First-In First-Out)
    Idea: Evict the page that has been in memory the longest.

    How it works:
    Pages enter a queue.
    When the queue is full → remove the front page.

    Pros: Simple, easy to implement.
    Cons: May evict frequently used pages → Belady’s anomaly (more frames → more faults sometimes).



🟩 2. LRU (Least Recently Used)
    Idea: Replace the page that hasn’t been used for the longest time.

    How it works:
    Track last access time of each page.
    Evict the page with the oldest timestamp.

    Pros: Very good approximation of optimal.
    Cons: Needs extra hardware or expensive tracking.



🟪 3. Optimal (MIN) Algorithm
    Idea: Replace the page that will not be used for the longest time in the future.

    How it works:
    Look ahead in the reference string.
    Evict the page whose next use is farthest.

    Pros: Best possible performance.
    Cons: Impossible to implement in real OS (requires future knowledge).



🟧 4. Clock (Second-Chance Algorithm)
    Idea: Give recently used pages a second chance before eviction.

    How it works:
    Each page has a reference bit (R).
    A clock hand scans frames:
    If R = 0 → evict
    If R = 1 → set R = 0 and skip it (second chance)

    Pros: Simple & close to LRU.
    Cons: Less accurate than true LRU.



🟫 5. Enhanced Clock (NRU – Not Recently Used)
    Idea: Consider both recent use (R bit) and dirty state (D bit).

    How it works: Pages fall into 4 classes:
    Class	R	D	Meaning
    0	0	0	Best choice to replace
    1	0	1	Dirty but not recently used
    2	1	0	Recently used, clean
    3	1	1	Recently used & dirty
    Evict from the lowest-numbered class.

    Pros: Smarter decisions than simple clock.
    Cons: Slightly more overhead.



🟫 6. Random Replacement
    Idea: Remove a random page.

    How it works:
    Pick any frame arbitrarily.
    Replace its page.

    Pros: Very simple; surprisingly effective sometimes.
    Cons: Can be very bad; unpredictable.



🟦 7. LFU (Least Frequently Used)
    Idea: Evict the page with the fewest total accesses.

    How it works:
    Maintain a counter for each page.
    Evict the page with the lowest count.

    Pros: Good for workloads where heavily used pages stay important.
    Cons: A page used heavily in the past may stay forever → needs aging.



🟩 8. MFU (Most Frequently Used)
    Idea: Opposite of LFU — evict the most frequently used page.

    Logic:
    Pages with high access count have probably “served their purpose.”

    Pros: Rarely useful, mostly theoretical.
    Cons: Bad performance in most real workloads.



🟪 9. Aging Algorithm (Approximate LRU)
    Idea: Approximate LRU using cheap counters instead of full history.

    How it works:
    Each page has an 8-bit or 16-bit counter.
    Each time unit:
    Shift counter right
    Insert current R bit into MSB

    Pros: Almost as good as LRU, cheap to implement.
    Cons: Requires periodic timer interrupts.



🟩 10. ARC (Adaptive Replacement Cache)
    Idea: Balance between recency and frequency automatically.

    How it works:
    Two main lists:
    T1: recently used
    T2: frequently used
    Two “ghost lists” (history of evicted pages).
    Algorithm constantly adjusts itself based on workload.

    Pros: One of the best practical algorithms; adapts itself.
    Cons: Complex to implement.



🟦 11. CAR (Clock with Adaptive Replacement)
    Idea: ARC logic + Clock structure.

    How it works:
    Similar to ARC but uses Clock to reduce overhead.
    
    Pros: Fast & adaptive.
    Cons: Still more complicated than LRU or FIFO.
