# diag.py - explain why two runs of the quarterly trend disagree.
#
# Observed: every quarter's transaction count was 1 to 6 higher than an
# earlier run recorded, and every median was equal or lower, never higher.
#
# Candidate explanation, not the only one: main.py filters
# sale_price >= 100000 while the earlier run filtered > 100000, so sales
# recorded at exactly $100,000 are included here and were excluded there.
#
# Other explanations remain open until this one is measured: the source
# dataset may have been revised between the runs, or another filter or date
# boundary may differ. This script tests only the price-boundary explanation
# and says plainly how much of the difference it accounts for.
#
# One fetch serves both variants, because they differ only by which rows at
# the bottom of the price filter are kept. That also makes it possible to
# check that the two variants are identical apart from those rows.
#
#     python diag.py
#
# Read-only: writes nothing, changes nothing.

from check import EXPECTED, BOROUGH, NAME

import main

AT = main.MIN_PRICE


def fmt(median, count):
    if median is None:
        return "no data"
    return "$%s / %s" % (format(median, ",d"), format(count, ",d"))


print("Fetching %s sales once, then computing both price boundaries from the"
      % NAME)
print("same rows. This takes 10-30 seconds.\n")

coverage = main.coverage_info()
latest = coverage["latest"]
cur_end = latest + main.timedelta(days=1)
quarters = main.quarters_ending(latest, 12)
span_start = min(main.add_months(cur_end, -24), quarters[0][0])
sales = main.parse_rows(main.fetch_span(coverage, BOROUGH, span_start, cur_end))
print("rows fetched: %s\n" % format(len(sales), ",d"))

rows = []
for q_start, q_end in quarters:
    label = "%d Q%d" % (q_start.year, (q_start.month - 1) // 3 + 1)
    prices = main.window(sales, q_start, q_end)
    at = [p for p in prices if p == AT]
    above = [p for p in prices if p > AT]
    rows.append(
        {
            "label": label,
            "ge": main.median_of(prices),
            "gt": main.median_of(above),
            "n_at": len(at),
            "partial": q_end > cur_end,
        }
    )

print("%-9s %-20s %-20s %-20s %7s" % ("QUARTER", "recorded earlier",
                                      ">= 100000 (now)", "> 100000",
                                      "at 100k"))
gt_hits = ge_hits = 0
delta_explained = 0
compared = 0
residuals = []
for r in rows:
    want = EXPECTED.get(r["label"])
    cells = "%-9s %-20s %-20s %-20s %7d" % (
        r["label"],
        fmt(*want) if want else ("incomplete" if r["partial"] else "-"),
        fmt(*r["ge"]), fmt(*r["gt"]), r["n_at"],
    )
    marks = []
    if want:
        compared += 1
        if r["ge"] == want:
            ge_hits += 1
            marks.append("matches now")
        if r["gt"] == want:
            gt_hits += 1
            marks.append("matches with >")
        residual = (r["ge"][1] - want[1]) - r["n_at"]
        residuals.append((r["label"], residual))
        if residual == 0:
            delta_explained += 1
        else:
            marks.append("%+d transactions unaccounted for" % residual)
    print(cells + ("   " + "; ".join(marks) if marks else ""))

print()
print("1. sales at exactly $%s per quarter: %s"
      % (format(AT, ",d"), ", ".join(str(r["n_at"]) for r in rows if not r["partial"])))
print("2. those counts account for the whole count difference in %d of %d quarters"
      % (delta_explained, compared))
print("3. they came through the same query as every other row, so they already")
print("   satisfy the borough, property-class and date filters")
print("4. filtering > $%s reproduces the earlier figures in %d of %d quarters"
      % (format(AT, ",d"), gt_hits, compared))
print("   (the current >= filter reproduces %d of %d)" % (ge_hits, compared))
print()

if gt_hits == compared and delta_explained == compared:
    print("CONFIRMED. The only difference between the two runs is whether sales")
    print("recorded at exactly $%s are kept. Nothing else differs."
          % format(AT, ","))
    print()
    print("That settles what caused it. It does not settle which boundary is")
    print("correct - see spec section 14 on nominal consideration. A sale")
    print("recorded at a round $%s may be a genuine low-priced home or a"
          % format(AT, ",d"))
    print("nominal transfer, and the spec should state which this project means.")
elif gt_hits == compared:
    print("MOSTLY CONFIRMED. The > boundary reproduces the earlier medians and")
    print("counts, but the per-quarter counts at exactly $%s do not account"
          % format(AT, ",d"))
    print("for the whole difference:")
    for label, residual in residuals:
        if residual:
            print("   %-9s %+d transactions unaccounted for" % (label, residual))
    print("Something else differs as well. Do not close this yet.")
elif ge_hits == compared:
    print("The current filter already reproduces the earlier figures. The")
    print("disagreement reported earlier came from somewhere else.")
else:
    print("NOT EXPLAINED by the price boundary. Neither filter reproduces the")
    print("earlier figures, so the cause is elsewhere - the source dataset")
    print("having been revised between the two runs is the next thing to check.")
