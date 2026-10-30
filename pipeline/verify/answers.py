"""Answer comparison through js/lib/answers.js, plus tidying what a model writes into something canon() reads."""
import json
import re
import subprocess

from .config import HERE

BRIDGE = HERE / "js" / "answers_bridge.mjs"


def _bridge(req):
    r = subprocess.run(["node", str(BRIDGE)], input=json.dumps(req), capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def canon_many(values):
    return _bridge({"canon": [str(v) for v in values]})["canon"] if values else []


def canon(value):
    return canon_many([value])[0]


def answer_hash(pid, answer):
    return _bridge({"hash": [[pid, str(answer)]]})["hash"][0]


def tidy(s):
    """'$\\dfrac{25}{4}$', '130^\\circ' and '20 km/h' become '25/4', '130' and '20'."""
    s = str(s).strip().strip("$").strip()
    s = re.sub(r"\\boxed\{(.*)\}", r"\1", s)
    s = re.sub(r"\\[dt]?frac\{(-?[\d.,\s]+)\}\{(-?[\d.,\s]+)\}", r"\1/\2", s)
    s = s.replace("\\,", "").replace("\\%", "").replace("^\\circ", "").replace("°", "")
    s = s.rstrip(".").strip()
    m = re.match(r"^(-?[\d,]*\.?\d+(?:\s*/\s*-?\d+)?)\s*[A-Za-z/%\s]*$", s)
    return m.group(1) if m else s
