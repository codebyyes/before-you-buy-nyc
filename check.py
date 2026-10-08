# check.py - verify the data layer against the live NYC Open Data API.
#
# Prints the market context as plain text, so the calculation can be checked
# without a browser or a running web server.
#
#     python check.py
#
# The quarterly figures are cross-checked against figures recorded in an
# earlier session. Those are a reference point, not ground truth: a mismatch
# means the two runs disagree and one of them needs explaining, which is
# exactly what we want to know.

import sys

import main

# Recorded in a previous session for Brooklyn, all eligible residential.
EXPECTED = {
    "2023 Q4": (919000, 2466),
    "2024 Q1": (915000, 2407),
    "2024 Q2": (985000, 2762),
    "2024 Q3": (965000, 2803),
    "2024 Q4": (977760, 2538),
    "2025 Q1": (999999, 2630),
    "2025 Q2": (990000, 2763),
    "2025 Q3": (1065000, 3119),
    "2025 Q4": (985000, 2586),
}

BOROUGH = "3"
NAME = "Brooklyn"


def money(n):
    return "-" if n is None else "%11s" % ("$" + format(n, ",d"))


def num(n):
    return "-" if n is None else "%7s" % format(n, ",d")


def main_check():
    print("Querying NYC Open Data for %s. This takes 10-30 seconds.\n" % NAME)
    try:
        ctx = main.build_context(BOROUGH, NAME)
    except Exception as exc:
        print("FAILED to build context: %s: %s" % (type(exc).__name__, exc))
        return 2

    cov = ctx["coverage"]
    print("DATASETS")
    print("  annualized %s  %s to %s  %s records"
          % (main.ANNUAL, cov["annual_min"], cov["annual_max"],
             format(cov["annual_n"], ",d")))
    print("  rolling    %s  %s to %s  %s records"
          % (main.ROLLING, cov["rolling_min"], cov["rolling_max"],
             format(cov["rolling_n"], ",d")))
    print("  boundary   sales up to %s come from the annualized dataset"
          % cov["annual_max"])
    print("  rows used  %s" % format(ctx["rows_examined"], ",d"))

    print("\nMEDIAN SALE PRICE BY OFFICIAL CLASS   12 months to %s"
          % ctx["cur_end"])
    for c in ctx["classes"]:
        print("  %-34s %s %s  %8s"
              % (c["category"], money(c["median"]), num(c["count"]),
                 main.signed(c["change"])))
    print("  %-34s %s %s  %8s"
          % ("ALL ELIGIBLE RESIDENTIAL", money(ctx["all_median"]),
             num(ctx["all_count"]), main.signed(ctx["all_change"])))

    print("\nQUARTERLY TREND   all eligible residential")
    checked = 0
    agree = 0
    for q in ctx["trend"]:
        line = "  %-8s %s %s" % (q["label"], money(q["median"]), num(q["count"]))
        if q["partial"]:
            line += "   incomplete, through %s" % q["through"]
        elif q["label"] in EXPECTED:
            checked += 1
            want_m, want_n = EXPECTED[q["label"]]
            if (q["median"], q["count"]) == (want_m, want_n):
                agree += 1
                line += "   SAME as previous session"
            else:
                line += "   DIFFERENT - previous session had %s / %s" % (
                    ("$" + format(want_m, ",d")), format(want_n, ",d"))
        print(line)

    print("\nCROSS-CHECK  %d of %d quarters match the previous session"
          % (agree, checked))
    if checked and agree == checked:
        print("RESULT  data layer reproduces the earlier figures exactly.")
        return 0
    if checked:
        print("RESULT  the two runs disagree. Do not assume either is wrong")
        print("        until the difference is explained.")
        return 1
    print("RESULT  no overlapping quarters to compare.")
    return 1


if __name__ == "__main__":
    sys.exit(main_check())
