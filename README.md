# Namegen

#### Two drivers are available:

- SQLite - persists as sqlite database
    - Might be safer storage and portable
    - Slower
- Memory - persists as compressed file on disk
    - Saves as compressed file on disk
    - Not as portable
    - Much Faster

#### Test

- Coverage is 100%
- Two tests are marked _skip_ because of comparatively long runtime
    - These generate all values available

#### Generation Speed

```
1000 Samples:
- Memory: 0.5-0.8 ms
- SQLite: 30-90 ms
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
