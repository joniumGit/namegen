# Namegen

#### Three drivers are available:

- SQLite - persists as sqlite database
    - Safe storage
    - Slow
    - Crash Resistant
        - Safe if crash happens outside a call
        - Relies on rollback if crash happens in call
- Memory - persists as compressed file on disk
    - Saves as compressed file on disk
        - Perhaps not as portable
    - Much Faster
    - Constant memory use
    - Not crash safe
- Hybrid
    - Pretty much as fast as the memory one
    - Offloads saving to another thread (SQLite)
    - Uses more and more memory
    - Lags behind generation
    - Not crash safe
        - Saving lags behind
    - Should be interoperable with SQLite driver

#### Environment Variables

```text
The workdir in Dockerfile is /opt/namegen

NAMEGEN_FILE ( default: wordlist.csv )
- This file specifies names for generation

NAMEGEN_DB_FILE ( default: namegen.db )
- Database file for namegen
- Hybrid and SQLite drivers only

NAMEGEN_MEMORY_STATE ( default: namegen_memory_state )
- Memory driver state file
- Memory driver only

NAMEGEN_DRIVER ( default: hybrid )
- Options: memory, sqlite
- Defines which driver is user
- Server only
```


#### Test

- Coverage is 100%
- Full gen tests are marked _skip_ because of comparatively long runtime
    - These generate all values available

#### TODO and Improvements

- Add tests that test regaining state
- Add driver for Redis or MariaDB for distributed use
    - Going to be slower
- Make hybrid model compress events
    - Remove individual counts
    - Save on interval and take the last event maybe

#### Generation Speed

This is not really relevant in actual use most probably, but shows the differences between the drivers. If the pool of
words is a lot larger, then the memory usage will go up. The Hybrid driver will lag behind in saving the events and
needs to catch up.

```json
{
  "sqlite": {
    "time": "31.05 ms",
    "memory_increase": "0.27%",
    "memory_maximum": "36.68 mb",
    "memory_minimum": "36.59 mb"
  },
  "memory": {
    "time": "0.48 ms",
    "memory_increase": "0.00%",
    "memory_maximum": "36.80 mb",
    "memory_minimum": "36.80 mb"
  },
  "hybrid": {
    "time": "0.64 ms",
    "memory_increase": "0.09%",
    "memory_maximum": "37.03 mb",
    "memory_minimum": "37.00 mb"
  },
  "count": 1000
}
```

```json
{
  "sqlite": {
    "time": "2218.99 ms",
    "memory_increase": "0.80%",
    "memory_maximum": "37.34 mb",
    "memory_minimum": "37.04 mb"
  },
  "memory": {
    "time": "40.61 ms",
    "memory_increase": "0.00%",
    "memory_maximum": "37.49 mb",
    "memory_minimum": "37.49 mb"
  },
  "hybrid": {
    "time": "49.99 ms",
    "memory_increase": "27.42%",
    "memory_maximum": "48.04 mb",
    "memory_minimum": "37.70 mb"
  },
  "count": 100000
}
```

```json
{
  "sqlite": {
    "time": "21669.93 ms",
    "memory_increase": "0.70%",
    "memory_maximum": "37.50 mb",
    "memory_minimum": "37.24 mb"
  },
  "memory": {
    "time": "406.25 ms",
    "memory_increase": "0.00%",
    "memory_maximum": "37.65 mb",
    "memory_minimum": "37.65 mb"
  },
  "hybrid": {
    "time": "488.76 ms",
    "memory_increase": "269.45%",
    "memory_maximum": "139.71 mb",
    "memory_minimum": "37.81 mb"
  },
  "count": 1000000
}
```

#### Notes

```
Period of sum of two periodic functions (a,b) is lcm(a,b)

I.E: (wordgen.py)

START.rotate(1) => Period of len(START) = a
END.rotate(1) => Period of len(END) = b

Proof:

When START rotates fully END has rotated a / b laps.
Meaning END will fully rotate when n * a / b is in N.
=> lcm(a,b) * a / b.

I.E: 
Choosing 2,4 we only get 4 distinct possibilities.
BUT: 2,5 => 10 which is much better.

Now this needs to be tweaked as high as possible.

So keep this in mind when tweaking the list.

At the time of writing it was at 
- len(START)=17
- len(END)=16
=> 272
```

Remember to check for duplicates `^(.+)$[^#]+^\1$`

This can generate `2 720 000` unique values in format `StartEnd#0000`.

Check this for how the number generation works
[Wikipedia, LCG](https://en.wikipedia.org/wiki/Linear_congruential_generator)

```
Then numbering uses a LCG with parameters:

- m = 10000
- a = 21
- c = 1
=> period: 10000

Which is used to produce the whole range [0, 9999]

The counts are generated for the whole sum function.
Initially the choice of starting sum is random.
This step uses random.randint(a,b)

The state can be loaded and saved at will.

Since the way LCG's work the state can even be 
recovered from the DB if necessary.

The combined generation limit is set by:
- PERIOD_OF_SUM_FUNCTION * LCG_M

After which the values will repeat.
```

Previously used this to regain hybrid state instead of _rowid_

````python
# Regain state
cnt = 0
i = next_start
j = next_end
while len(unsorted) > 0:
    for idx, item in enumerate(unsorted):
        if i == item.start.id and j == item.end.id:
            del unsorted[idx]
            self.queue.append(item)
            break
    cnt += 1
    i = i + 1 if i < max_start else 1
    j = j + 1 if j < max_end else 1
````
