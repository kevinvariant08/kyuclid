"""Chooses inputs across idea families, so a family with 40 problems doesn't produce 40 near-siblings.

The task 03 synthesis doesn't exist yet, so a record's first listed technique stands in for its family.
"""
import random
from collections import defaultdict

TOPICS = "ACGN"


def eligible(r, kyus):
    return r.get("kyu") in kyus and r.get("generation_potential") != "low" and not r.get("figure_needed") and not r.get("source_defect") and not (r.get("analysis_meta") or {}).get("source_defect")


def sample(records, kyus=(5, 4, 3), per_kyu=10, seed=6):
    """Each kyu gets every topic, with the odd extras rotating, and no family repeats while another is free."""
    rng = random.Random(seed)
    used, chosen = set(), []
    for k_i, kyu in enumerate(kyus):
        pool = defaultdict(list)
        for r in records:
            if eligible(r, kyus) and r["kyu"] == kyu:
                pool[r["topic"]].append(r)
        order = TOPICS[k_i:] + TOPICS[:k_i]
        quota = {t: per_kyu // 4 + (i < per_kyu % 4) for i, t in enumerate(order)}
        for t in order:
            # "high" potential first, then shuffled, so the sample isn't one kind of problem.
            rows = sorted(pool[t], key=lambda r: (r["generation_potential"] != "high", rng.random()))
            taken = 0
            for repeat_ok in (False, True):
                for r in rows:
                    fam = r["techniques"][0] if r.get("techniques") else r["id"]
                    if taken < quota[t] and r["id"] not in {c["id"] for c in chosen} and (repeat_ok or fam not in used):
                        used.add(fam)
                        chosen.append(dict(id=r["id"], kyu=kyu, topic=t, family=fam))
                        taken += 1
    return dict(seed=seed, kyus=list(kyus), per_kyu=per_kyu, family_rule="first listed technique", inputs=chosen)
