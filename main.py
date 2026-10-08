# Before You Buy NYC - V1
# main.py : Flask routes, NYC Open Data access, all price calculation.
# Presentation lives in templates/index.html - nothing in this file writes HTML.
#
# No AI calls in this file. Running it costs nothing.
# Spec sections implemented here: 5 (two-column workflow), 6 (market context),
# 14 (eligible residential, price basis, transaction counts), 15 (data access),
# 16 (reproducibility shown on screen).

import json
import os
import statistics
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

from flask import Flask, render_template, request

# ---------------------------------------------------------------------------
# Constants - spec section 14
# ---------------------------------------------------------------------------

ANNUAL = "w2pb-icbu"   # Citywide Annualized Calendar Sales - long comparable history
ROLLING = "usep-8jbt"  # Citywide Rolling Calendar Sales  - most recent months

RESIDENTIAL = [
    "01 ONE FAMILY DWELLINGS",
    "02 TWO FAMILY DWELLINGS",
    "03 THREE FAMILY DWELLINGS",
    "04 TAX CLASS 1 CONDOS",
    "09 COOPS - WALKUP APARTMENTS",
    "10 COOPS - ELEVATOR APARTMENTS",
    "12 CONDOS - WALKUP APARTMENTS",
    "13 CONDOS - ELEVATOR APARTMENTS",
    "15 CONDOS - 2-10 UNIT RESIDENTIAL",
]

MIN_PRICE = 100000  # excludes nominal and zero-consideration transfers

ALL_BOROUGHS = [
    ("1", "Manhattan"),
    ("2", "Bronx"),
    ("3", "Brooklyn"),
    ("4", "Queens"),
    ("5", "Staten Island"),
]
AVAILABLE_BOROUGHS = ["3"]  # V1 ships one borough. Spec section 3.

PAGE = 50000  # Socrata per-request maximum
TIMEOUT = 90

APP_TOKEN = os.environ.get("SOCRATA_APP_TOKEN", "").strip()

# ---------------------------------------------------------------------------
# Socrata access
# ---------------------------------------------------------------------------


def _get(url):
    headers = {"Accept": "application/json", "User-Agent": "BeforeYouBuyNYC/1.0"}
    if APP_TOKEN:
        headers["X-App-Token"] = APP_TOKEN
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def soql(dataset, params):
    url = "https://data.cityofnewyork.us/resource/%s.json?%s" % (
        dataset,
        urllib.parse.urlencode(params),
    )
    return _get(url)


def _iso(d):
    return d.strftime("%Y-%m-%d")


def _in_clause():
    values = ",".join("'" + c.replace("'", "''") + "'" for c in RESIDENTIAL)
    return "building_class_category in(%s)" % values


def _where(borough, start, end, quoted):
    # start inclusive, end exclusive
    borough_term = "borough='%s'" % borough if quoted else "borough=%s" % borough
    return " AND ".join(
        [
            borough_term,
            "sale_price >= %d" % MIN_PRICE,
            "sale_date >= '%s'" % _iso(start),
            "sale_date < '%s'" % _iso(end),
            _in_clause(),
        ]
    )


def dataset_range(dataset):
    """Earliest and latest sale_date actually present in a dataset."""
    row = soql(
        dataset,
        {"$select": "min(sale_date) as mn, max(sale_date) as mx, count(1) as n"},
    )[0]
    return (
        datetime.strptime(row["mn"][:10], "%Y-%m-%d").date(),
        datetime.strptime(row["mx"][:10], "%Y-%m-%d").date(),
        int(row["n"]),
    )


def dataset_updated(dataset):
    """Timestamp NYC last refreshed the dataset. Returns None if unavailable."""
    try:
        meta = _get("https://data.cityofnewyork.us/api/views/%s.json" % dataset)
        stamp = meta.get("rowsUpdatedAt")
        if stamp:
            return datetime.utcfromtimestamp(int(stamp)).date()
    except Exception:
        pass
    return None


def fetch_one_dataset(dataset, borough, start, end):
    """All eligible residential rows in [start, end) from one dataset.

    The borough column's type is not documented, so an unquoted numeric
    comparison is tried first and a quoted one is used if the server rejects it.
    """
    last_error = None
    for quoted in (False, True):
        rows = []
        offset = 0
        try:
            while True:
                page = soql(
                    dataset,
                    {
                        "$select": "sale_date,sale_price,building_class_category",
                        "$where": _where(borough, start, end, quoted),
                        "$order": ":id",
                        "$limit": PAGE,
                        "$offset": offset,
                    },
                )
                rows.extend(page)
                if len(page) < PAGE:
                    return rows
                offset += PAGE
        except urllib.error.HTTPError as exc:
            last_error = exc
            continue
    raise last_error


def fetch_span(coverage, borough, start, end):
    """Rows in [start, end), each date served by exactly one dataset.

    The annualized dataset is authoritative up to its own last sale date; the
    rolling dataset serves everything after that. The two overlap in the source
    data, so a single boundary is the only way to avoid double counting.
    """
    boundary = coverage["annual_max"] + timedelta(days=1)
    rows = []
    if start < boundary:
        rows += fetch_one_dataset(ANNUAL, borough, start, min(end, boundary))
    if end > boundary:
        rows += fetch_one_dataset(ROLLING, borough, max(start, boundary), end)
    return rows


def coverage_info():
    a_min, a_max, a_n = dataset_range(ANNUAL)
    r_min, r_max, r_n = dataset_range(ROLLING)
    return {
        "annual_min": a_min,
        "annual_max": a_max,
        "annual_n": a_n,
        "rolling_min": r_min,
        "rolling_max": r_max,
        "rolling_n": r_n,
        "latest": max(a_max, r_max),
        "annual_updated": dataset_updated(ANNUAL),
        "rolling_updated": dataset_updated(ROLLING),
    }


# ---------------------------------------------------------------------------
# Calculation - the AI never touches any of this (spec section 13)
# ---------------------------------------------------------------------------


def parse_rows(rows):
    out = []
    for r in rows:
        raw_date = r.get("sale_date")
        raw_price = r.get("sale_price")
        category = r.get("building_class_category")
        if not raw_date or raw_price is None or not category:
            continue
        try:
            d = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
            p = int(float(raw_price))
        except (ValueError, TypeError):
            continue
        if p < MIN_PRICE:
            continue
        out.append((d, p, category))
    return out


def median_of(prices):
    if not prices:
        return None, 0
    return int(statistics.median(prices)), len(prices)


def add_months(d, n):
    total = (d.year * 12 + d.month - 1) + n
    year, month = divmod(total, 12)
    month += 1
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(year, month, min(d.day, days[month - 1]))


def pct_change(before, after):
    if not before or not after:
        return None
    return round((after - before) / before * 100, 2)


def window(sales, start, end):
    """Prices with start <= sale_date < end."""
    return [p for (d, p, _c) in sales if start <= d < end]


def by_class(sales, start, end):
    buckets = {c: [] for c in RESIDENTIAL}
    for d, p, c in sales:
        if start <= d < end and c in buckets:
            buckets[c].append(p)
    return buckets


def quarters_ending(latest, count=12):
    """The `count` calendar quarters up to and including the one holding `latest`."""
    anchor = date(latest.year, ((latest.month - 1) // 3) * 3 + 1, 1)
    out = []
    for i in range(count - 1, -1, -1):
        start = add_months(anchor, -3 * i)
        out.append((start, add_months(start, 3)))
    return out


def build_context(borough, borough_name):
    coverage = coverage_info()
    latest = coverage["latest"]

    # Current and prior 12-month windows, ending with the last day of data.
    cur_end = latest + timedelta(days=1)
    cur_start = add_months(cur_end, -12)
    prior_start = add_months(cur_start, -12)

    # Three years of quarters, plus the prior-year window, in one fetch.
    quarters = quarters_ending(latest, 12)
    span_start = min(prior_start, quarters[0][0])
    sales = parse_rows(fetch_span(coverage, borough, span_start, cur_end))

    classes = []
    cur_buckets = by_class(sales, cur_start, cur_end)
    prior_buckets = by_class(sales, prior_start, cur_start)
    for c in RESIDENTIAL:
        cur_med, cur_n = median_of(cur_buckets[c])
        prior_med, prior_n = median_of(prior_buckets[c])
        classes.append(
            {
                "category": c,
                "median": cur_med,
                "count": cur_n,
                "prior_median": prior_med,
                "prior_count": prior_n,
                "change": pct_change(prior_med, cur_med),
            }
        )

    all_cur_med, all_cur_n = median_of(window(sales, cur_start, cur_end))
    all_prior_med, all_prior_n = median_of(window(sales, prior_start, cur_start))

    trend = []
    for q_start, q_end in quarters:
        med, n = median_of(window(sales, q_start, q_end))
        trend.append(
            {
                "label": "%d Q%d" % (q_start.year, (q_start.month - 1) // 3 + 1),
                "median": med,
                "count": n,
                "partial": q_end > cur_end,
                "through": latest if q_end > cur_end else q_end - timedelta(days=1),
            }
        )

    return {
        "borough": borough_name,
        "borough_code": borough,
        "coverage": coverage,
        "cur_start": cur_start,
        "cur_end": cur_end - timedelta(days=1),
        "prior_start": prior_start,
        "prior_end": cur_start - timedelta(days=1),
        "classes": classes,
        "all_median": all_cur_med,
        "all_count": all_cur_n,
        "all_prior_median": all_prior_med,
        "all_prior_count": all_prior_n,
        "all_change": pct_change(all_prior_med, all_cur_med),
        "trend": trend,
        "span_start": span_start,
        "rows_examined": len(sales),
        "annual_label": ANNUAL,
        "rolling_label": ROLLING,
        "min_price": MIN_PRICE,
        "class_count": len(RESIDENTIAL),
    }


# ---------------------------------------------------------------------------
# Chart geometry - spec section 6 wants one line for all eligible residential.
# Only coordinates are computed here; templates/index.html draws the SVG.
#
# A line, not bars: medians sit in a narrow band, so zero-based bars would all
# look identical, while non-zero-based bars would exaggerate. A line may sit on
# a non-zero axis, and the axis range is printed so nothing is hidden.
# ---------------------------------------------------------------------------

CHART = {"w": 448, "h": 176, "pl": 78, "pr": 436, "pt": 14, "pb": 130}


def chart_geometry(trend):
    plotted = [q for q in trend if q["median"]]
    if len(plotted) < 2:
        return None

    g = dict(CHART)
    lo_v = min(q["median"] for q in plotted)
    hi_v = max(q["median"] for q in plotted)
    pad = (hi_v - lo_v) * 0.12 or max(hi_v * 0.02, 1.0)
    lo, hi = lo_v - pad, hi_v + pad
    n = len(trend)

    def px(i):
        return round(g["pl"] + i * (g["pr"] - g["pl"]) / (n - 1), 1)

    def py(v):
        return round(g["pb"] - (v - lo) / (hi - lo) * (g["pb"] - g["pt"]), 1)

    g["label_x"] = g["pl"] - 8
    g["grid"] = [
        {"y": py(v), "label": money(int(v))}
        for v in (hi_v, (hi_v + lo_v) / 2, lo_v)
    ]

    solid = [(px(i), py(q["median"])) for i, q in enumerate(trend)
             if q["median"] and not q["partial"]]
    g["solid"] = " ".join("%s,%s" % p for p in solid) if len(solid) > 1 else ""

    g["dash"] = None
    tail = [(i, q) for i, q in enumerate(trend) if q["median"] and q["partial"]]
    if tail and solid:
        i, q = tail[0]
        g["dash"] = {"x1": solid[-1][0], "y1": solid[-1][1],
                     "x2": px(i), "y2": py(q["median"])}

    g["markers"] = []
    for i, q in enumerate(trend):
        if not q["median"]:
            continue
        g["markers"].append(
            {
                "x": px(i),
                "y": py(q["median"]),
                "partial": q["partial"],
                "title": "%s%s: %s, %s sales%s" % (
                    q["label"], " (incomplete)" if q["partial"] else "",
                    money(q["median"]), num(q["count"]),
                    " through " + q["through"].isoformat() if q["partial"] else "",
                ),
            }
        )

    ticks = [i for i in range(n) if i % 3 == 0 and i < n - 3] + [n - 1]
    g["xticks"] = [
        {
            "x": px(i),
            "y": g["pb"] + 20,
            "anchor": "end" if i == n - 1 else ("start" if i == 0 else "middle"),
            "label": trend[i]["label"] + ("*" if trend[i]["partial"] else ""),
        }
        for i in ticks
    ]

    g["axis_lo"] = money(int(lo))
    g["axis_hi"] = money(int(hi))
    return g


# ---------------------------------------------------------------------------
# Formatting helpers, registered as template filters
# ---------------------------------------------------------------------------


def money(n):
    return "-" if n is None else "$%s" % format(n, ",d")


def num(n):
    return "-" if n is None else format(n, ",d")


def signed(v):
    if v is None:
        return "-"
    return ("+%.2f%%" % v) if v >= 0 else ("%.2f%%" % v)


# ---------------------------------------------------------------------------

app = Flask(__name__)
app.jinja_env.filters["money"] = money
app.jinja_env.filters["num"] = num
app.jinja_env.filters["signed"] = signed


def borough_options(selected=None):
    return [
        {
            "code": code,
            "name": name,
            "available": code in AVAILABLE_BOROUGHS,
            "selected": code == selected,
        }
        for code, name in ALL_BOROUGHS
    ]


def view(ctx=None, error=None, question=""):
    partial = None
    chart = None
    if ctx:
        chart = chart_geometry(ctx["trend"])
        partial = next((q for q in ctx["trend"] if q["partial"]), None)
    return render_template(
        "index.html",
        today=date.today().isoformat(),
        boroughs=borough_options(ctx["borough_code"] if ctx else None),
        ctx=ctx,
        chart=chart,
        partial=partial,
        error=error,
        question=question,
    )


@app.route("/", methods=["GET", "POST"])
def home():
    return view()


@app.route("/confirm", methods=["POST"])
def confirm():
    borough = (request.form.get("borough") or "").strip()
    names = dict(ALL_BOROUGHS)
    if borough not in AVAILABLE_BOROUGHS:
        return view(error="That region is not available in V1.")
    try:
        ctx = build_context(borough, names[borough])
    except urllib.error.HTTPError as exc:
        return view(error="NYC Open Data returned HTTP %s. The official source "
                          "rejected the query, so nothing is shown rather than "
                          "a guess." % exc.code)
    except Exception as exc:
        return view(error="Could not reach NYC Open Data (%s: %s). No figures "
                          "are shown rather than stale or estimated ones."
                          % (type(exc).__name__, exc))
    if not ctx["all_count"]:
        return view(error="No eligible residential transactions were returned "
                          "for that region. An empty result is a correct result.")
    return view(ctx=ctx)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
