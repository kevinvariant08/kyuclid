"""Reads a figure's .tex: its exact coordinates, its facts and its metadata, all in %! comments.

A figure is real tkz-euclide. Every point is one line of it, with its exact value beside it:

    %! scale 1/27
    %! let R = 195/2
    \\tkzDefPoint(0.000000,3.611111){A} %! A = (0, R)
    %! fact on_circle(A, O, R)
    %! fact dist(X, P) == 64

Exact values are evaluated at 50 digits, and the decimals TeX draws with must equal value times scale, so
the picture can't drift from what the facts were checked on. `sync` fills in the decimals.
"""
import ast
import re

from mpmath import mp, mpf

mp.dps = 50
TOLERANCE = mpf("1e-9")
DECIMAL_TOLERANCE = 2e-6

DEF_POINT = re.compile(r"\\tkzDefPoint\(\s*([^,)]*),\s*([^)]*)\)\{([A-Za-z][A-Za-z0-9']*)\}[ \t]*%!\s*([A-Za-z][A-Za-z0-9']*)\s*=\s*(.+?)\s*$", re.M)
ANY_DEF_POINT = re.compile(r"\\tkzDefPoints?\b")
DIRECTIVE = re.compile(r"^\s*%!\s*(scale|let|fact|alt|after_paragraph)\b\s*(.*?)\s*$", re.M)

# No package, file, shell or catcode tricks: this text can come from a model, and TeX is a programming language.
BANNED_TEX = re.compile(r"\\(usepackage|RequirePackage|documentclass|write|immediate|openin|openout|read|readline|include|includegraphics|catcode|csname|expandafter|directlua|pdffiledump|pdfximage|pdfobj|special|def|gdef|edef|xdef|let|newcommand|renewcommand|loop|foreach)\b")
# Points come from exact values, not from TeX's low-precision arithmetic. The old circle options also loop forever.
BANNED_TKZ = re.compile(r"\\tkz(Def|Get|Inter|Calc|Duplicate|Show)(?!Point\()\w*|\\tkzDrawCircle\[[^\]]*\b(circum|in|ex|euler|apollonius)\b")


class FigureError(Exception):
    """The figure is wrong: it doesn't compile, contradicts itself or breaks a drawing rule."""


class Vec(tuple):
    pass


def _point(x, y):
    return Vec((mpf(x), mpf(y)))


def _dist(a, b):
    return mp.hypot(a[0] - b[0], a[1] - b[1])


def _cross(a, b, c, d):
    return (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])


def _dot(a, b, c, d):
    return (b[0] - a[0]) * (d[0] - c[0]) + (b[1] - a[1]) * (d[1] - c[1])


def _lerp(a, b, t):
    return _point(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _foot(p, a, b):
    return _lerp(a, b, _dot(a, p, a, b) / _dot(a, b, a, b))


def _meet(a, b, c, d):
    den = _cross(a, b, c, d)
    if den == 0:
        raise FigureError("meet: the lines are parallel")
    return _lerp(a, b, _cross(a, c, c, d) / den)


def _circumcentre(a, b, c):
    ab, ac = (mid(a, b), _rot90(a, b)), (mid(a, c), _rot90(a, c))
    return _meet(ab[0], _point(ab[0][0] + ab[1][0], ab[0][1] + ab[1][1]), ac[0], _point(ac[0][0] + ac[1][0], ac[0][1] + ac[1][1]))


def _rot90(a, b):
    return (-(b[1] - a[1]), b[0] - a[0])


def mid(a, b):
    return _lerp(a, b, mpf(1) / 2)


def _rotate(p, o, deg):
    t = mp.radians(deg)
    x, y = p[0] - o[0], p[1] - o[1]
    return _point(o[0] + x * mp.cos(t) - y * mp.sin(t), o[1] + x * mp.sin(t) + y * mp.cos(t))


def _incentre(a, b, c):
    la, lb, lc = _dist(b, c), _dist(a, c), _dist(a, b)
    s = la + lb + lc
    return _point((la * a[0] + lb * b[0] + lc * c[0]) / s, (la * a[1] + lb * b[1] + lc * c[1]) / s)


def _area(*pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


def _angle(a, b, c):
    return mp.degrees(mp.acos(_dot(b, a, b, c) / (_dist(a, b) * _dist(b, c))))


def _bad(condition):
    """A predicate's answer as a residual: 0 if it holds, 1 if not, so it reads like the others."""
    return mpf(0) if condition else mpf(1)


def _collinear(p, a, b):
    return abs(_cross(a, b, a, p)) / _dist(a, b)


def _on_segment(p, a, b):
    return max(_collinear(p, a, b), _bad(_dot(a, p, a, b) >= -TOLERANCE and _dot(b, p, b, a) >= -TOLERANCE))


def _concyclic(a, b, c, *rest):
    o = _circumcentre(a, b, c)
    r = _dist(o, a)
    return max(abs(_dist(o, p) - r) for p in rest)


def _tangent(o, r, a, b):
    return abs(_collinear(o, a, b) - r)


def _tangent_circles(o1, r1, o2, r2):
    d = _dist(o1, o2)
    return min(abs(d - (r1 + r2)), abs(d - abs(r1 - r2)))


VALUES = {"pi": mp.pi}
NUMBER_FUNCS = {
    "sqrt": mp.sqrt, "sin": mp.sin, "cos": mp.cos, "tan": mp.tan, "asin": mp.asin, "acos": mp.acos, "atan": mp.atan, "atan2": mp.atan2,
    "sind": lambda d: mp.sin(mp.radians(d)), "cosd": lambda d: mp.cos(mp.radians(d)), "tand": lambda d: mp.tan(mp.radians(d)), "abs": abs,
    "dist": _dist, "angle": _angle, "area": _area, "x": lambda p: p[0], "y": lambda p: p[1],
    "inradius": lambda a, b, c: 2 * _area(a, b, c) / (_dist(a, b) + _dist(b, c) + _dist(a, c)),
    "circumradius": lambda a, b, c: _dist(_circumcentre(a, b, c), a),
}
POINT_FUNCS = {
    "mid": mid, "lerp": _lerp, "foot": _foot, "meet": _meet, "rotate": _rotate, "circumcentre": _circumcentre, "incentre": _incentre,
    "reflect": lambda p, a, b: _lerp(p, _foot(p, a, b), 2),
    "polar": lambda o, r, deg: _point(o[0] + r * mp.cos(mp.radians(deg)), o[1] + r * mp.sin(mp.radians(deg))),
    "shift": lambda p, dx, dy: _point(p[0] + dx, p[1] + dy),
}
# Each returns a residual: the fact holds when it is below TOLERANCE.
PREDICATES = {
    "collinear": _collinear, "on_line": _collinear, "on_segment": _on_segment, "on_circle": lambda p, o, r: abs(_dist(o, p) - r),
    "concyclic": _concyclic, "perp": lambda a, b, c, d: abs(_dot(a, b, c, d)) / (_dist(a, b) * _dist(c, d)),
    "parallel": lambda a, b, c, d: abs(_cross(a, b, c, d)) / (_dist(a, b) * _dist(c, d)), "tangent": _tangent, "tangent_circles": _tangent_circles,
    "midpoint": lambda m, a, b: _dist(m, mid(a, b)), "equal": lambda a, b: abs(a - b),
}
BINOPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b, ast.Pow: lambda a, b: a ** b}
ORDER = {ast.Lt: lambda a, b: a < b, ast.LtE: lambda a, b: a <= b + TOLERANCE, ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a + TOLERANCE >= b}


def evaluate(text, names):
    """Evaluates one expression. Only arithmetic, known names and the functions above: no attributes, no eval."""
    try:
        tree = ast.parse(text.replace("'", "_prime"), mode="eval").body
    except SyntaxError as e:
        raise FigureError(f"can't read the expression {text!r}") from e

    def walk(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return mpf(str(n.value))
        if isinstance(n, ast.Name):
            key = n.id.replace("_prime", "'")
            if key in names:
                return names[key]
            if key in VALUES:
                return VALUES[key]
            raise FigureError(f"unknown name {key} in {text!r}")
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -walk(n.operand)
        if isinstance(n, ast.BinOp) and type(n.op) in BINOPS:
            return BINOPS[type(n.op)](walk(n.left), walk(n.right))
        if isinstance(n, ast.Tuple) and len(n.elts) == 2:
            return _point(walk(n.elts[0]), walk(n.elts[1]))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and not n.keywords:
            f = {**NUMBER_FUNCS, **POINT_FUNCS, **PREDICATES}.get(n.func.id)
            if f is None:
                raise FigureError(f"unknown function {n.func.id} in {text!r}")
            try:
                return f(*[walk(a) for a in n.args])
            except (TypeError, IndexError, ZeroDivisionError, ValueError) as e:
                raise FigureError(f"can't evaluate {text!r}: {e}") from e
        raise FigureError(f"not allowed in a figure expression: {text!r}")

    return tree, walk


class Figure:
    def __init__(self, name, tex):
        self.name, self.tex = name, tex
        self.scale, self.alt, self.after_paragraph = None, None, None
        self.names, self.points, self.facts, self.drawn = {}, {}, [], {}
        self._parse()

    def _parse(self):
        for m in BANNED_TEX.finditer(re.sub(r"%.*", "", self.tex.replace(r"\input{preamble}", ""))):
            raise FigureError(f"{m.group()} isn't allowed in a figure: use the shared preamble's styles")
        if not self.tex.lstrip("% \n").startswith(("\\input{preamble}", "alt", "!")) or r"\input{preamble}" not in self.tex:
            raise FigureError(r"a figure must start from \input{preamble}")
        if re.search(r"\\input\{(?!preamble\})", self.tex):
            raise FigureError(r"the only \input allowed is the shared preamble")
        m = BANNED_TKZ.search(re.sub(r"%.*", "", self.tex))
        if m:
            raise FigureError(f"{m.group()} computes in TeX: give every point an exact value with \\tkzDefPoint instead")

        # Lets, points and facts are read in file order, so a point can use anything above it.
        events = sorted([(m.start(), "point", m) for m in DEF_POINT.finditer(self.tex)] + [(m.start(), m.group(1), m) for m in DIRECTIVE.finditer(self.tex)], key=lambda e: e[0])
        matched = {m.start() for _, kind, m in events if kind == "point"}
        for m in ANY_DEF_POINT.finditer(self.tex):
            if m.start() not in matched:
                line = self.tex[m.start():].split("\n", 1)[0]
                raise FigureError(f"every point needs its exact value on the same line, as \\tkzDefPoint(x,y){{P}} %! P = (a, b). Found: {line[:60]}")
        fact_texts = []
        for _, kind, m in events:
            if kind == "scale":
                self.scale = self._number(m.group(2))
            elif kind == "alt":
                self.alt = m.group(2)
            elif kind == "after_paragraph":
                self.after_paragraph = int(m.group(2))
            elif kind == "let":
                k, _, v = m.group(2).partition("=")
                self.names[k.strip()] = self._value(v.strip())
            elif kind == "fact":
                fact_texts.append(m.group(2))
            else:
                if m.group(3) != m.group(4):
                    raise FigureError(f"the line defining {m.group(3)} gives the exact value of {m.group(4)}")
                value = self._value(m.group(5))
                if not isinstance(value, Vec):
                    raise FigureError(f"{m.group(3)} must be a point, not a number")
                self.names[m.group(3)] = self.points[m.group(3)] = value
                self.drawn[m.group(3)] = (m.group(1).strip(), m.group(2).strip())
        if self.scale is None:
            raise FigureError("no %! scale line")
        self.facts = fact_texts

    def _number(self, text):
        tree, walk = evaluate(text, self.names)
        return walk(tree)

    _value = _number

    def synced_tex(self):
        """The source with the decimals TeX draws with recomputed from the exact values."""
        def fill(m):
            p = self.points[m.group(3)]
            return f"\\tkzDefPoint({mp.nstr(p[0] * self.scale, 8, strip_zeros=False, min_fixed=-mp.inf, max_fixed=mp.inf)},{mp.nstr(p[1] * self.scale, 8, strip_zeros=False, min_fixed=-mp.inf, max_fixed=mp.inf)}){{{m.group(3)}}} %! {m.group(4)} = {m.group(5)}"
        return DEF_POINT.sub(fill, self.tex)

    def check_decimals(self):
        for k, (dx, dy) in self.drawn.items():
            try:
                x, y = float(dx), float(dy)
            except ValueError as e:
                raise FigureError(f"{k} is drawn at ({dx}, {dy}), which isn't a pair of decimals") from e
            ex, ey = self.points[k]
            if abs(x - float(ex * self.scale)) > DECIMAL_TOLERANCE or abs(y - float(ey * self.scale)) > DECIMAL_TOLERANCE:
                raise FigureError(f"{k} is drawn at ({dx}, {dy}) but its exact value scales to ({float(ex * self.scale):.6f}, {float(ey * self.scale):.6f})")

    def check_facts(self):
        """Returns how many facts held. Raises on the first that doesn't."""
        for text in self.facts:
            self._check_fact(text)
        return len(self.facts)

    def _check_fact(self, text):
        tree, walk = evaluate(text, self.names)
        if isinstance(tree, ast.Compare) and len(tree.ops) == 1:
            a, b = walk(tree.left), walk(tree.comparators[0])
            op = type(tree.ops[0])
            if op is ast.Eq:
                if abs(a - b) > TOLERANCE:
                    raise FigureError(f"fact fails: {text}: left is {mp.nstr(a, 12)}, right is {mp.nstr(b, 12)}")
            elif op in ORDER:
                if not ORDER[op](a, b):
                    raise FigureError(f"fact fails: {text}: left is {mp.nstr(a, 12)}, right is {mp.nstr(b, 12)}")
            else:
                raise FigureError(f"can't read the fact {text!r}")
            return
        if not (isinstance(tree, ast.Call) and isinstance(tree.func, ast.Name) and tree.func.id in PREDICATES):
            raise FigureError(f"a fact is a predicate such as concyclic(A,B,C,D), or a comparison such as dist(A,B) == 5, not {text!r}")
        residual = walk(tree)
        if residual > TOLERANCE:
            raise FigureError(f"fact fails: {text}: off by {mp.nstr(residual, 6)}")


def fact_numbers(figure):
    """The plain numbers a fact claims, like 64 in dist(X,P) == 64, so the gate can look for them in the solution."""
    out = []
    for text in figure.facts:
        m = re.search(r"==\s*(\d+(?:\.\d+)?(?:\s*/\s*\d+)?)\s*$", text)
        if m:
            out.append((text, re.sub(r"\s", "", m.group(1))))
    return out
