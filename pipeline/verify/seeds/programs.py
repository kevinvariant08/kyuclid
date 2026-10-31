"""An answer and an independent check program for each answer seed. Each works from the statement, not the written solution."""

SEEDS = {
    "circle-in-the-square": ("25/4", """
from sympy import symbols, solve, Rational
h, k, r = symbols('h k r', real=True)
# Centre (h, k), through A=(0,0) and B=(10,0), tangent to the line y=10.
sols = solve([h**2 + k**2 - r**2, (h - 10)**2 + k**2 - r**2, (10 - k)**2 - r**2], [h, k, r])
print(next(s[2] for s in sols if s[2] > 0))
"""),
    "closest-approach": ("4", """
from sympy import symbols, diff, solve
x = symbols('x', real=True)
y = (10 - 3*x) / 4
f = x**2 + y**2
print(min(f.subs(x, c) for c in solve(diff(f, x), x)))
"""),
    "cube-the-reciprocal": ("110", """
from sympy import symbols, solve, simplify
x = symbols('x')
vals = {simplify(c**3 + 1/c**3) for c in solve(x + 1/x - 5, x)}
assert len(vals) == 1
print(vals.pop())
"""),
    "divisor-census": ("24", "print(sum(1 for d in range(1, 361) if 360 % d == 0))"),
    "domino-corridor": ("89", """
def fill(grid, n):
    for c in range(n):
        for r in range(2):
            if not grid[r][c]:
                total = 0
                if r == 0 and not grid[1][c]:
                    grid[0][c] = grid[1][c] = 1
                    total += fill(grid, n)
                    grid[0][c] = grid[1][c] = 0
                if c + 1 < n and not grid[r][c + 1]:
                    grid[r][c] = grid[r][c + 1] = 1
                    total += fill(grid, n)
                    grid[r][c] = grid[r][c + 1] = 0
                return total
    return 1
print(fill([[0] * 10, [0] * 10], 10))
"""),
    "egyptian-pairs": ("15", """
from fractions import Fraction
count = 0
for a in range(1, 2000):
    rest = Fraction(1, 12) - Fraction(1, a)
    if rest > 0 and rest.numerator == 1:
        count += 1
print(count)
"""),
    "factorial-sandwich": ("23", """
from math import factorial
best = 0
for n in range(4, 150):
    target = factorial(n)
    length = n - 3
    start = 1
    while True:
        p = 1
        for v in range(start, start + length):
            p *= v
        if p == target:
            best = max(best, n)
        if p >= target:
            break
        start += 1
print(best)
"""),
    "floor-staircase": ("600", """
# Every floor changes only at a multiple of 1/24, so testing those x sees every value.
seen = set()
for k in range(0, 24 * 60):
    seen.add(2 * k // 24 + 4 * k // 24 + 6 * k // 24 + 8 * k // 24)
print(sum(1 for v in range(1, 1001) if v in seen))
"""),
    "last-two-digits": ("29", """
v = 1
for _ in range(2026):
    v = v * 3 % 100
print(v)
"""),
    "neither-fizz-nor-buzz": ("533", "print(sum(1 for n in range(1, 1001) if n % 3 and n % 5))"),
    "polygon-from-one-angle": ("9", "print(next(n for n in range(3, 1000) if (n - 2) * 180 == 140 * n))"),
    "round-table-no-neighbours": ("322", """
n = 12
print(sum(1 for m in range(1 << n) if all(not (m >> i & 1 and m >> ((i + 1) % n) & 1) for i in range(n))))
"""),
    "square-hunting": ("1196", """
from math import isqrt
total = 0
for n in range(1, 100000):
    v = n * n + 12 * n - 2028
    if v >= 0 and isqrt(v) ** 2 == v:
        total += n
print(total)
"""),
    "the-13-14-15-triangle": ("4", """
from sympy import Triangle
print(Triangle(sss=(13, 14, 15)).inradius)
"""),
    "there-and-back": ("20", """
from fractions import Fraction
# Add up the ride in one-kilometre steps.
minutes = Fraction(0)
for km in range(60):
    minutes += Fraction(60, 15) if km < 30 else Fraction(60, 30)
print(Fraction(60) / (minutes / 60))
"""),
    "twenty-to-four": ("130", """
from fractions import Fraction
hour, minute = Fraction(0), Fraction(0)
for _ in range(3 * 60 + 40):
    hour += Fraction(1, 2)
    minute = (minute + 6) % 360
d = abs(hour - minute)
print(min(d, 360 - d))
"""),
    "zeros-of-2026": ("505", """
from math import factorial
v = factorial(2026)
c = 0
while v % 10 == 0:
    v //= 10
    c += 1
print(c)
"""),
}
