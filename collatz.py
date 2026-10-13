"""The 3x+1 (Collatz) problem.

Start with a positive integer n. If n is even, divide it by 2; if odd,
replace it with 3n + 1. Repeat. The Collatz conjecture says every starting
value eventually reaches 1.

Usage:
    python collatz.py 27            # print the sequence for 27
    python collatz.py 27 --plot     # also save a graph to collatz-27.html
    python collatz.py --max 1000000 # find the longest chain below a limit
"""

import argparse
import json


def collatz_step(n: int) -> int:
    """Return the next value in the 3x+1 sequence."""
    return n // 2 if n % 2 == 0 else 3 * n + 1


def collatz_sequence(n: int) -> list[int]:
    """Return the full sequence from n down to 1, inclusive."""
    if n < 1:
        raise ValueError("n must be a positive integer")
    seq = [n]
    while n != 1:
        n = collatz_step(n)
        seq.append(n)
    return seq


def stopping_time(n: int, cache: dict[int, int] | None = None) -> int:
    """Return the number of steps for n to reach 1, memoized via cache."""
    if n < 1:
        raise ValueError("n must be a positive integer")
    if cache is None:
        cache = {}
    cache.setdefault(1, 0)
    path = []
    while n not in cache:
        path.append(n)
        n = collatz_step(n)
    steps = cache[n]
    for value in reversed(path):
        steps += 1
        cache[value] = steps
    return steps


def longest_chain(limit: int) -> tuple[int, int]:
    """Return (start, steps) for the start value below limit with the most steps."""
    if limit < 2:
        raise ValueError("limit must be at least 2")
    cache: dict[int, int] = {1: 0}
    best_start, best_steps = 1, 0
    for start in range(1, limit):
        steps = stopping_time(start, cache)
        if steps > best_steps:
            best_start, best_steps = start, steps
    return best_start, best_steps


_PLOT_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Collatz Sequence __START__</title>
<style>
:root {
  color-scheme: light;
  --surface-1: #fcfcfb;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --text-muted: #7a7974;
  --grid: #e6e5e1;
  --axis: #b9b8b2;
  --series-1: #2a78d6;
  --tip-bg: #0b0b0b;
  --tip-text: #f0efec;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --surface-1: #1a1a19;
    --text-primary: #f0efec;
    --text-secondary: #c3c2b7;
    --text-muted: #8f8e88;
    --grid: #2e2e2c;
    --axis: #4a4a47;
    --series-1: #3987e5;
    --tip-bg: #f0efec;
    --tip-text: #0b0b0b;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface-1: #1a1a19;
  --text-primary: #f0efec;
  --text-secondary: #c3c2b7;
  --text-muted: #8f8e88;
  --grid: #2e2e2c;
  --axis: #4a4a47;
  --series-1: #3987e5;
  --tip-bg: #f0efec;
  --tip-text: #0b0b0b;
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 24px 16px;
  background: var(--surface-1); color: var(--text-primary);
  font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
}
.wrap { max-width: 760px; margin: 0 auto; }
h1 { font-size: 18px; margin: 0 0 4px; font-weight: 600; }
.sub { color: var(--text-secondary); margin: 0 0 16px; }
.stats { display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 12px; }
.stat .k { color: var(--text-muted); font-size: 12px; }
.stat .v { font-size: 22px; font-weight: 600; font-variant-numeric: tabular-nums; }
.chart { position: relative; }
svg { display: block; width: 100%; overflow: visible; }
.grid line { stroke: var(--grid); stroke-width: 1; }
.axis text, .lbl { fill: var(--text-secondary); font-size: 12px; font-variant-numeric: tabular-nums; }
.axis-title { fill: var(--text-muted); font-size: 12px; }
.baseline { stroke: var(--axis); stroke-width: 1; }
.line { fill: none; stroke: var(--series-1); stroke-width: 2; stroke-linejoin: round; }
.dot { fill: var(--series-1); stroke: var(--surface-1); stroke-width: 2; }
.dot.hidden { opacity: 0; }
.dot.active { opacity: 1; r: 6; }
.cross { stroke: var(--axis); stroke-width: 1; stroke-dasharray: 3 3; }
.tip {
  position: absolute; pointer-events: none; opacity: 0;
  background: var(--tip-bg); color: var(--tip-text);
  padding: 6px 8px; border-radius: 6px; font-size: 12px; white-space: nowrap;
  transform: translate(-50%, calc(-100% - 12px)); transition: opacity .1s;
}
details { margin-top: 16px; color: var(--text-secondary); }
table { border-collapse: collapse; margin-top: 8px; font-variant-numeric: tabular-nums; }
th, td { padding: 4px 12px; text-align: right; border-bottom: 1px solid var(--grid); }
th { color: var(--text-muted); font-weight: 500; }
td { color: var(--text-primary); }
</style>
</head>
<body>
<div class="wrap">
  <h1>Collatz sequence starting at __START__</h1>
  <p class="sub">Value at each step of the 3x+1 process until it reaches 1</p>
  <div class="stats">
    <div class="stat"><div class="k">Steps to reach 1</div><div class="v" id="s-steps"></div></div>
    <div class="stat"><div class="k">Peak value</div><div class="v" id="s-peak"></div></div>
  </div>
  <div class="chart" id="chart">
    <svg id="svg" role="img" aria-label="Line chart of the Collatz sequence starting at __START__"></svg>
    <div class="tip" id="tip"></div>
  </div>
  <details>
    <summary>Show data table</summary>
    <table id="tbl"><thead><tr><th>Step</th><th>Value</th><th>Rule applied</th></tr></thead><tbody></tbody></table>
  </details>
</div>
<script>
const seq = __SEQ__;
const steps = seq.length - 1;
const peak = Math.max(...seq);
const peakIdx = seq.indexOf(peak);
document.getElementById('s-steps').textContent = steps.toLocaleString();
document.getElementById('s-peak').textContent = peak.toLocaleString();
const ruleFor = (i) => {
  if (i === 0) return null;
  const prev = seq[i - 1];
  return prev % 2 === 0 ? `${prev} ÷ 2` : `3×${prev} + 1`;
};

const NS = 'http://www.w3.org/2000/svg';
const svg = document.getElementById('svg');
const tip = document.getElementById('tip');
const chart = document.getElementById('chart');
const el = (tag, attrs, parent = svg) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };
const niceStep = (v) => { const p = Math.pow(10, Math.floor(Math.log10(v))); for (const f of [1, 2, 5, 10]) if (f * p >= v) return f * p; };
const yStep = niceStep(peak / 4);
const yMax = Math.ceil((peak * 1.08) / yStep) * yStep;
const fmt = (v) => Number(v.toFixed(6)).toLocaleString();

function render() {
  svg.replaceChildren(); tip.style.opacity = 0;
  const W = Math.max(280, chart.clientWidth), H = W < 500 ? 260 : 340;
  const yLabelW = 8 * fmt(yMax).length + 12;
  const m = { t: 24, r: 16, b: 44, l: Math.max(40, yLabelW) };
  const iw = W - m.l - m.r, ih = H - m.t - m.b;
  const x = (i) => m.l + (steps ? (i / steps) * iw : iw / 2);
  const y = (v) => m.t + ih - (v / yMax) * ih;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.setAttribute('width', W); svg.setAttribute('height', H);

  const grid = el('g', { class: 'grid' });
  const axis = el('g', { class: 'axis' });
  for (let k = 0; k * yStep <= yMax + 1e-9; k++) {
    const v = k * yStep;
    if (k > 0) el('line', { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v) }, grid);
    el('text', { x: m.l - 8, y: y(v) + 4, 'text-anchor': 'end' }, axis).textContent = fmt(v);
  }
  el('line', { class: 'baseline', x1: m.l, x2: W - m.r, y1: y(0), y2: y(0) });
  const tickW = 8 * String(steps).length + 16;
  const every = niceStep(Math.max(1, steps / Math.max(1, Math.floor(iw / tickW))));
  for (let i = 0; i <= steps; i += every) {
    el('text', { x: x(i), y: H - m.b + 18, 'text-anchor': 'middle' }, axis).textContent = i;
  }
  el('text', { class: 'axis-title', x: m.l + iw / 2, y: H - 6, 'text-anchor': 'middle' }).textContent = 'Step';

  const cross = el('line', { class: 'cross', y1: m.t, y2: y(0), opacity: 0 });
  el('path', { class: 'line', d: seq.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join('') });
  // Show every marker only when there is room; otherwise just the hovered one.
  const showDots = steps === 0 || iw / steps >= 10;
  const dots = seq.map((v, i) => el('circle', { class: showDots ? 'dot' : 'dot hidden', cx: x(i), cy: y(v), r: 4 }));

  // Direct labels only on the peak and the end.
  const anchorAt = (px) => px < m.l + 40 ? 'start' : px > W - m.r - 40 ? 'end' : 'middle';
  el('text', { class: 'lbl', x: x(peakIdx), y: y(peak) - 12, 'text-anchor': anchorAt(x(peakIdx)) }).textContent = `Peak ${peak.toLocaleString()}`;
  if (peakIdx !== steps) {
    el('text', { class: 'lbl', x: x(steps), y: y(seq[steps]) - 12, 'text-anchor': 'end' }).textContent = `End ${seq[steps]}`;
  }

  const hit = el('rect', { x: m.l - 10, y: 0, width: iw + 20, height: H - m.b + 24, fill: 'transparent' });
  let active = -1;
  const show = (i) => {
    if (active >= 0) dots[active].classList.remove('active');
    active = i; dots[i].classList.add('active');
    cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i)); cross.setAttribute('opacity', 1);
    const prev = seq[i - 1];
    const rule = i === 0 ? 'starting value' : `${prev} is ${prev % 2 === 0 ? 'even' : 'odd'} → ${ruleFor(i)}`;
    tip.innerHTML = `<strong>Step ${i}: ${seq[i].toLocaleString()}</strong><br>${rule}`;
    const half = tip.offsetWidth / 2 + 4;
    tip.style.left = `${Math.min(Math.max(x(i), half), W - half)}px`;
    tip.style.top = `${y(seq[i])}px`; tip.style.opacity = 1;
  };
  const hide = () => {
    if (active >= 0) dots[active].classList.remove('active');
    active = -1; tip.style.opacity = 0; cross.setAttribute('opacity', 0);
  };
  const onMove = (e) => {
    const r = svg.getBoundingClientRect();
    show(steps ? Math.max(0, Math.min(steps, Math.round(((e.clientX - r.left - m.l) / iw) * steps))) : 0);
  };
  hit.addEventListener('pointermove', onMove);
  hit.addEventListener('pointerdown', onMove);
  hit.addEventListener('pointerleave', hide);
}
render();
new ResizeObserver(() => render()).observe(chart);

const tbody = document.querySelector('#tbl tbody');
seq.forEach((v, i) => {
  tbody.insertAdjacentHTML('beforeend', `<tr><td>${i}</td><td>${v.toLocaleString()}</td><td>${ruleFor(i) ?? '—'}</td></tr>`);
});
</script>
</body>
</html>
"""


def plot_html(n: int) -> str:
    """Return a standalone HTML page with an interactive line graph of n's sequence."""
    seq = collatz_sequence(n)
    return (_PLOT_TEMPLATE
            .replace("__START__", str(n))
            .replace("__SEQ__", json.dumps(seq)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore the 3x+1 (Collatz) problem.")
    parser.add_argument("n", nargs="?", type=int, help="starting value")
    parser.add_argument("--max", type=int, metavar="LIMIT",
                        help="find the start below LIMIT with the longest chain")
    parser.add_argument("--plot", nargs="?", const="", metavar="FILE",
                        help="save an HTML graph of the sequence for n "
                             "(default file: collatz-<n>.html)")
    args = parser.parse_args()

    if args.plot is not None and args.n is None:
        parser.error("--plot needs a starting value, e.g. collatz.py 13 --plot")

    if args.max is not None:
        start, steps = longest_chain(args.max)
        print(f"Longest chain below {args.max}: start={start}, steps={steps}")
    elif args.n is not None:
        seq = collatz_sequence(args.n)
        print(" -> ".join(map(str, seq)))
        print(f"Steps: {len(seq) - 1}, peak: {max(seq)}")
        if args.plot is not None:
            path = args.plot or f"collatz-{args.n}.html"
            with open(path, "w", encoding="utf-8") as f:
                f.write(plot_html(args.n))
            print(f"Graph saved to {path} (open it in a web browser)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
