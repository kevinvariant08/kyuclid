"""The variation recipes, and which suit a given analysis record."""
from collections import Counter

RECIPES = {
    "transplant": "Transplant. Use the same technique on a different mathematical object, so the setup looks nothing like the original.",
    "invert": "Invert. Ask for what the original gave, or build the problem around the reverse question, so the solver has to run the idea backwards.",
    "combine": "Combine. Merge the core idea with the second technique named below, so that both are really needed.",
    "generalise-specialise": "Generalise then specialise. Find the family the idea belongs to and pick a fresh member of it, one that needs its own thought.",
    "change-route": "Change the route. Build a problem where the less common route below is the natural one, and the original's usual route no longer works well.",
    "new-context": "New context. Put the same structure on a combinatorial or geometric model the original did not use, so that seeing the model is part of the problem.",
}


def suitable(record):
    names = ["transplant", "invert", "combine", "generalise-specialise", "new-context"]
    if len(record.get("solution_paths") or []) >= 2:
        names.append("change-route")
    return names


def pick(record, rng, n=3):
    """Different recipes for each candidate, so the model isn't choosing between three versions of one idea."""
    names = suitable(record)
    return rng.sample(names, min(n, len(names)))


def rare_partner(record, records, rng):
    """A second technique from the same kyu that rarely appears with this record's main technique."""
    same_kyu = [r for r in records if r.get("kyu") == record.get("kyu")]
    main = (record.get("techniques") or [None])[0]
    counts = Counter(t for r in same_kyu for t in r.get("techniques") or [])
    together = Counter(t for r in same_kyu if main in (r.get("techniques") or []) for t in r["techniques"])
    own = set(record.get("techniques") or [])
    # Seen at least three times, so it belongs at this kyu; least often with the main technique first.
    options = sorted((together[t], t) for t, c in counts.items() if c >= 3 and t not in own)
    if not options:
        return None
    rarest = [t for k, t in options if k == options[0][0]]
    return rng.choice(sorted(rarest))
