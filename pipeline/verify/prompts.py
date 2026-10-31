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
              'a genuine alternative reading, an unstated assumption, an object not defined. Also material: asking more than one question, a hidden case split the solver could '
              'miss, a reading trick (the difficulty turns on a surprising reading of words like "between" or "all but"), and culturally specific knowledge not defined in the statement '
              '(a sport\'s rules, a currency, a card deck, chess, school-year names, local dates). cosmetic: wording could be nicer but the answer is unaffected. '
              'Do not invent far-fetched readings or flag standard conventions. An empty list is a good result.')

AUDIT = ('You audit the written solution and hints of a maths problem. Reply with JSON only: '
         '{"reaches_answer":true|false,"issues":[{"severity":"material"|"cosmetic","issue":"<max 25 words>"}]}. '
         'material: a false step, an unjustified leap a reader could not fill in routinely, a missed case, or a conclusion that does not follow. '
         'reaches_answer: the solution ends at exactly the stated answer. For a proof, reaches_answer means it proves the claim. '
         'Routine algebra may be skipped without comment. Also material, and starting "Hint N:", a hint that clearly breaks one of these: they run gentlest to strongest; '
         'hint 1 points at the right object or quantity and does not name the crux technique; hint 2 names the technique; the last hint leaves only routine steps, and no hint states '
         'the final answer or finishes a proof; each adds something and does not just restate the statement or the previous hint; each makes sense without having solved the one before. '
         'Two hints or three are equally fine, so never ask for a third hint. Do not flag mild wording. An empty list is a good result.')

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


FIGURE_CRITIC = ('You are a geometry author checking the diagrams drawn for a solution, as a careful reader of an olympiad book would. Look at each image. '
                 'Reply with JSON only: {"findings":[{"severity":"material"|"cosmetic","issue":"<max 25 words>"}]}. '
                 'material: the figure shows a different configuration from the statement or solution; a labelled point, length or mark contradicts the text; '
                 'a point lies visibly in the wrong place; labels overlap each other or a line so that one can\'t be read; the figure is so cramped or so badly scaled '
                 'that its key feature can\'t be seen. It may draw one example case, and that is fine if the case fits the problem. It may label points the text doesn\'t name. '
                 'cosmetic: anything that is a matter of taste. An empty list is a good result.')


def figure_critic(d):
    alts = "\n".join(f"Figure {i + 1} (after paragraph {f['after_paragraph']}): {f['alt']}" for i, f in enumerate(d["solution_figures"]))
    return f"STATEMENT:\n{d['statement']}\n\nSOLUTION:\n{d['solution']}\n\nTHE WRITER'S DESCRIPTION OF THE FIGURES:\n{alts}"


def audit(d):
    claim = f"STATED ANSWER: {d['answer']}" if d["type"] == "answer" else "THIS IS A PROOF PROBLEM."
    hints = "\n".join(f"Hint {i + 1}: {h}" for i, h in enumerate(d["hints"]))
    return f"STATEMENT:\n{d['statement']}\n\n{claim}\n\nSOLUTION:\n{d['solution']}\n\nHINTS:\n{hints}"


def originality(d, neighbours):
    parts = [f"NEW PROBLEM:\n{d['statement']}"]
    for n in neighbours:
        idea = f"\nCore idea: {n['core_idea']}" if n.get("core_idea") else ""
        parts.append(f"NEIGHBOUR {n['id']}:\n{n['text'][:1500]}{idea}")
    if not neighbours:
        parts.append('No neighbours: return an empty list for "neighbours" and answer "known".')
    return "\n\n".join(parts)
