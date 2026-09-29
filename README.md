## Part 4 Analysis
### Option A: stop mixing silence

`ToneMatrix.next_sample()` is called 44,100 times per second. During each call, the original implementation calls `next_sample()` on all `n` strings even when most of those strings are silent.

This problem is remedied by calling `next_sample()` only on the strings that are audible and retiring them when they are no longer audible. A string is added to the set `ringing_strings` when it is plucked in `pluck_column()` and removed when its energy falls below the 0.001 threshold. String energy is checked when the playhead changes columns.

The threshold was derived empirically by comparing the audio output at different threshold values. For example, a threshold of 0.01 caused the audio to cut off abruptly.

If a retired string is plucked again, it is added back in to `ringing_strings`.

---

Running times will be calculated based on the RAM model of computation. Let:

* `n` = grid size
* `k` = lit cells
* `a` = ringing strings, where `0 <= a <= n`
* `s` = size of the string buffer of the lowest frequency string

The original `next_sample()` contains:

```python
def next_sample(self):

	if self.times_sample_called == 0:
		self.pluck_column(self.column)
		self.column += 1
		if self.column == self.grid_size:
			self.column = 0

	sum = 0
	for instrument in self.instruments:
		sum += instrument.next_sample()

	self.times_sample_called += 1
	if self.times_sample_called == self.samples_per_column:
		self.times_sample_called = 0
        
	return sum
```

The original loop is:

```python
	for instrument in self.instruments:
		sum += instrument.next_sample()
```

ToneMatrix has one instrument for each row, meaning there are exactly `n` instruments.

Each call to `instrument.next_sample()` performs RingBuffer operations `dequeue()`, `peek()`, and `enqueue()`, which are all O(1).

Therefore, mixing runs in **O(n)** time per audio sample.

---

The optimized `next_sample()` contains:

```python
def next_sample(self):

	if self.times_sample_called == 0:
		self.pluck_column(self.column)
		self.column += 1
		self.counter += 1
		if self.column == self.grid_size:
			self.column = 0

		strings_to_retire = [row for row in self.ringing_strings if self.instruments[row].energy() < 0.001]
		for string in strings_to_retire:
			self.ringing_strings.discard(string)

	sum = 0
	for row in self.ringing_strings:
		sum += self.instruments[row].next_sample()

	self.times_sample_called += 1
	if self.times_sample_called == self.samples_per_column:
		self.times_sample_called = 0
        
	return sum
```

The optimized loop is:

```python
	for row in self.ringing_strings:
		sum += self.instruments[row].next_sample()
```

The loop runs through `a` ringing strings, therefore mixing takes **O(a)** per audio sample.

Since `a` &le; `n`, O(a) can be significantly smaller than O(n) when only a small number of strings are ringing. However, a check is done on all ringing strings every time the playhead moves by calling `energy()`.
```python
    def energy(self):
        total = 0.0
        n = self.buffer.size()
        for _ in range(n):
            value = self.buffer.dequeue()
            total += abs(value)
            self.buffer.enqueue(value)
        return total / n
```
`energy()` goes through all values in a string buffer, giving it an **O(s)** runtime. The size of the string buffer is inversely proportional to string frequency. Since `energy()` is called on every ringing string, `ToneMatrix.next_sample()` gains an additional **O(as)** run time each time the playhead moves, which by default is about once every 0.185 seconds (1/5.4 seconds).

---

**Why do these bounds hold?**

The original implementation mixes the sound by looping through every instrument. Since there are `n` strings, the loop executes `n` times for every audio sample, giving **O(n)** time per sample.

The optimized implementation only loops through `ringing_strings`. Since there are `a` currently ringing strings, the mixing loop executes `a` times, giving **O(a)** time per sample. However, the energies of each active string is checked (which is O(as)) roughly every 5.4 seconds. Thus, the running time of the entire operation is **O(a + as/5.4)**.

---

`python benchmark.py`

**original:**

| **size** | **density** | **samples** | **seconds** | **μs/sample** | **x real time** |
| --- | --- | --- | --- | --- | --- |
| 8 | 0.05 | 65536 | 0.236 | 3.608 | 6.28 |
| 8 | 0.25 | 65536 | 0.236 | 3.602 | 6.30 |
| 16 | 0.05 | 131072 | 0.921 | 7.028 | 3.23 |
| 16 | 0.25 | 131072 | 0.922 | 7.033 | 3.22 |
| 32 | 0.05 | 262144 | 3.644 | 13.901 | 1.63 |
| 32 | 0.25 | 262144 | 3.659 | 13.960 | 1.62 |
| 64 | 0.05 | 524288 | 14.533 | 27.719 | 0.82 |
| 64 | 0.25 | 524288 | 14.644 | 27.931 | 0.81 |

---

`python benchmark.py --impl optimized`

**optimized:**

| **size** | **density** | **samples** | **seconds** | **μs/sample** | **x real time** |
| --- | --- | --- | --- | --- | --- |
| 8 | 0.05 | 65536 | 0.023 | 0.349 | 64.90 |
| 8 | 0.25 | 65536 | 0.191 | 2.914 | 7.78 |
| 16 | 0.05 | 131072 | 0.322 | 2.454 | 9.24 |
| 16 | 0.25 | 131072 | 0.812 | 6.196 | 3.66 |
| 32 | 0.05 | 262144 | 1.609 | 6.140 | 3.69 |
| 32 | 0.25 | 262144 | 3.181 | 12.134 | 1.87 |
| 64 | 0.05 | 524288 | 5.982 | 11.410 | 1.99 |
| 64 | 0.25 | 524288 | 12.567 | 23.969 | 0.95 |

**Observations:**

- The optimized implementation has lower μs/sample at every tested grid size and density. 
- The improvement is more noticeable at lower densities, when fewer strings are likely to be ringing. 
- At size 64 and density 0.05, the original takes 27.719 μs/sample, while the optimized version takes 11.410 μs/sample. 
- At size 64 and density 0.25, the optimized version in still faster, but the difference is smaller: 23.969 μs/sample for the optimized version and 27.931 μs/sample for the original version.
- The results are consistent with the expected behavior of the optimized version; it should perform much better than the original when the active strings are less then the total amount of strings.

---

**When is the optimization worse?**

The optimization can be worse when almost all `n` strings are ringing, meaning `a` is close to `n`.

In this case, the optimized version still has to mix almost every string, so the O(a) mixing cost approaches O(n). However, unlike the original implementation, it still has to perform extra work to maintain `ringing_strings` and check string energy.

Therefore, the additional work can render the optimized version slower than the original when more strings are active.

All in all, the optimization is most effective when a significant number of strings are silent for significant periods of time.
