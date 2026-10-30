"""Every model prompt. They're short on purpose: they run many times per draft."""

SOLVE = ('You are solving a maths contest problem alone, with no tools. Work it out carefully and concisely. '
         'Finish with one final line of JSON: {"answer":"<value>"}. The value is a single exact number: an integer, '
         'a fraction a/b or a terminating decimal. If the wording seems unclear, answer the most natural reading.')

PROGRAM_JUDGE = ('You audit a Python program meant to verify a maths problem\'s answer independently. Reply with JSON only: '
                 '{"verdict":"computes"|"restates"|"hardcoded"|"wrong_problem","reason":"<max 30 words>"}. '
                 'computes: it searches, enumerates, simulates exactly or does a symbolic computation of the quantity asked, from the problem\'s '
                 'own definitions (exact coordinates for geometry are fine). restates: it only evaluates the closed formula or final arithmetic '
                 'from the written solution, so it would repeat any error there. hardcoded: the answer, or a constant that decides it, is written in. '
                 'wrong_problem: it computes something other than what the statement asks. Bounded searches are fine if the bound is justified or clearly generous.')

WELL_POSED = ('You review a maths contest statement for defects before publication. Reply with JSON only: '
              '{"findings":[{"severity":"material"|"cosmetic","issue":"<max 25 words>"}]}. '
              'material: a competent solver could reasonably reach a different answer or be unable to proceed: ambiguity, a missing condition, '
              'a genuine alternative reading, an unstated assumption, an object not defined. cosmetic: wording could be nicer but the answer is unaffected. '
              'Do not invent far-fetched readings or flag standard conventions. An empty list is a good result.')

AUDIT = ('You audit a written solution to a maths problem. Reply with JSON only: '
         '{"reaches_answer":true|false,"issues":[{"severity":"material"|"cosmetic","issue":"<max 25 words>"}]}. '
         'material: a false step, an unjustified leap a reader could not fill in routinely, a missed case, or a conclusion that does not follow. '
         'reaches_answer: the solution ends at exactly the stated answer. For a proof, reaches_answer means it proves the claim. '
         'Routine algebra may be skipped without comment. An empty list is a good result.')

ORIGINALITY = ('You protect a problem bank from disguised copies. A reskin keeps the same mathematical structure and solution path and changes only the setting, '
               'names or numbers. Sharing a technique is not a reskin. Reply with JSON only: {"neighbours":[{"id":"<id>","reskin":true|false,"reason":"<max 20 words>"}],'
               '"known":{"is_known":true|false,"name":"<source or name, else empty>","reason":"<max 20 words>"}}. '
               'known asks about your own memory: is the new problem, up to setting and numbers, a specific published contest problem, a named classic or a '
               'well-known puzzle? A generic technique exercise with no recognisable source is not known. Describe in your own words; never quote any problem.')

ABSTRACT = ('State the abstract core idea of this maths problem in one or two sentences, with no numbers, names or story, in terms of the mathematical structure '
            'and the key technique. Reply with the sentences only.')


def solve(draft):
    return draft["statement"] + (f"\n\nFigure: {draft['figure_alt']}" if draft.get("figure_alt") else "")


def program_judge(d):
    return f"STATEMENT:\n{d['statement']}\n\nWRITTEN SOLUTION:\n{d['solution']}\n\nPROGRAM:\n{d['check_program']}"


def well_posed(d):
    return f"STATEMENT:\n{d['statement']}\n\nSOLUTION (to show the intended reading):\n{d['solution']}"


def audit(d):
    claim = f"STATED ANSWER: {d['answer']}" if d["type"] == "answer" else "THIS IS A PROOF PROBLEM."
    return f"STATEMENT:\n{d['statement']}\n\n{claim}\n\nSOLUTION:\n{d['solution']}"


def originality(d, neighbours):
    parts = [f"NEW PROBLEM:\n{d['statement']}"]
    for n in neighbours:
        idea = f"\nCore idea: {n['core_idea']}" if n.get("core_idea") else ""
        parts.append(f"NEIGHBOUR {n['id']}:\n{n['text'][:1500]}{idea}")
    if not neighbours:
        parts.append('No neighbours: return an empty list for "neighbours" and answer "known".')
    return "\n\n".join(parts)
