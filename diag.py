# diag.py - explain why two runs of the quarterly trend disagree.
#
# Hypothesis: the earlier run filtered sale_price > 100000 (strictly greater)
# while main.py filters >= 100000, so transactions recorded at exactly
# $100,000 are included here and were excluded there. That would raise every
# transaction count slightly and pull every median down or leave it unchanged,
# which is the pattern actually observed.
#
# This script runs the trend both ways against the live API and reports which
# filter reproduces the earlier figures. It writes nothing and changes nothing.
#
#     python diag.py

import main
from check import EXPECTED


def trend_with(op):
    original = main._where

    def patched(borough, start, end, quoted):
        return original(borough, start, end, quoted).replace(
            "sale_price >= %d" % main.MIN_PRICE,
            "sale_price %s %d" % (op, main.MIN_PRICE),
        )

    main._where = patched
    try:
        ctx = main.build_context("3", "Brooklyn")
    finally:
        main._where = original
    return {q["label"]: (q["median"], q["count"]) for q in ctx["trend"]}


def score(got):
    hits = []
    for label, want in sorted(EXPECTED.items()):
        have = got.get(label)
        hits.append((label, want, have, have == want))
    return hits


print("Running the quarterly trend twice against the live NYC API.")
print("This takes about a minute.\n")

results = {}
for op in (">=", ">"):
    print("  filtering sale_price %s %d ..." % (op, main.MIN_PRICE))
    results[op] = trend_with(op)

print()
print("%-9s %-22s %-22s %-22s" % ("QUARTER", "recorded earlier", ">= 100000", "> 100000"))
agree = {">=": 0, ">": 0}
for label, want, _h, _ok in score(results[">="]):
    row = "%-9s %-22s" % (label, "$%s / %s" % (format(want[0], ",d"), format(want[1], ",d")))
    for op in (">=", ">"):
        have = results[op].get(label)
        if have is None or have[0] is None:
            cell = "no data"
        else:
            cell = "$%s / %s" % (format(have[0], ",d"), format(have[1], ",d"))
            if have == want:
                agree[op] += 1
                cell += "  OK"
        row += " %-22s" % cell
    print(row)

total = len(EXPECTED)
print()
print("  sale_price >= 100000 reproduces %d of %d quarters" % (agree[">="], total))
print("  sale_price >  100000 reproduces %d of %d quarters" % (agree[">"], total))
print()
if agree[">"] == total and agree[">="] < total:
    print("CONFIRMED. The earlier run excluded sales recorded at exactly")
    print("$100,000. The difference is the boundary of the filter, nothing else.")
elif agree[">="] == total:
    print("The current filter already reproduces the earlier figures. The")
    print("disagreement came from somewhere else in this run.")
elif agree[">"] > agree[">="]:
    print("PARTLY EXPLAINED. The boundary accounts for some quarters but not")
    print("all, so something else differs as well.")
else:
    print("NOT EXPLAINED by the filter boundary. The cause is elsewhere -")
    print("most likely the source dataset changed between the two runs.")
