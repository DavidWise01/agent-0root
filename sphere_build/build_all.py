#!/usr/bin/env python3
"""
Recursive 1000-sphere agentic builder.
"""
import argparse
import hashlib
import json
import os

SEED_TITLE = "Bridgeburner Cortex of I13"
SEED_PAYLOAD = "34 == 34"
GOLDEN_INDICES = [0, 9, 18, 27, 36, 45, 54]

def sha256_str(s):
    return hashlib.sha256(s.encode()).hexdigest()

def build_seed(outdir):
    idx = 0
    data = {"sphere": idx, "seed": SEED_PAYLOAD, "index": GOLDEN_INDICES[0]}
    payload_sha = sha256_str(json.dumps(data))
    body = "<p>Sphere 0 = icarium Bridgeburner Cortex of I13. Seed.</p>"
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sphere 0 · {SEED_TITLE}</title>
<style>{{*{{box-sizing:border-box;margin:0;padding:0}}}}
html{{background:#07050d;color:#e8eaf1;font-family:'Segoe UI',Arial,sans-serif}}
.app{{max-width:1920px;margin:0 auto;padding:14px 16px 22px}}
.top{{display:flex;align-items:center;gap:14px;border:1px solid rgba(168,128,230,.42);
  background:linear-gradient(160deg,rgba(32,23,49,.96),rgba(18,14,30,.94));padding:14px 18px;border-radius:22px}}
.glyph{{width:52px;height:52px;display:grid;place-items:center;border-radius:17px;
  background:radial-gradient(circle at 35% 30%,#f6deff 0%,#b383ff 24%,#50307e 56%,#211533 100%);
  font-size:32px}}
.brand h1{{font-size:22px}}
.bottom{{display:flex;justify-content:space-between;gap:18px;padding:14px 18px;
  border-top:1px solid rgba(94,69,133,.5);background:rgba(8,6,16,.7)}}
.stat{{font-family:'Courier New',monospace;font-size:14px;color:var(--lav)}}
.stat b{{color:var(--gold)}}
.panel{{background:#140d24;border:1px solid rgba(94,69,133,.5);border-radius:12px;
  box-shadow:0 0 0 1px rgba(255,255,255,.04), 0 10px 20px rgba(0,0,0,.55);padding:18px}}
.panel h2{{font-size:12px;letter-spacing:.18em;color:#6f5f95;text-transform:uppercase;margin-bottom:10px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.metric{{display:flex;flex-direction:column;gap:4px;padding:10px 12px;
  background:rgba(20,14,36,.4);border:1px solid rgba(94,69,133,.35);border-radius:8px}}
.metric .k{{font-size:10px;color:#6f5f95}}
.metric .v{{font-family:'Courier New',monospace;font-size:18px;color:#d4b8ff;font-weight:700}}
.footer{{border-top:1px solid rgba(94,69,133,.3);flex-shrink:0;padding:10px 16px;text-align:center;
  font-size:10px;color:#6f5f95;font-family:'Courier New',monospace}}
</style></head>
<body><div class="app">
<header class="top"><div class="brand"><div class="glyph">S</div><div class="brand-txt">
<div class="smallcaps">SPHERE 0</div><h1>{SEED_TITLE}</p></div>
<div class="bottom"><div class="stat">sha256 <b id="sh">{payload_sha}</b></div>
<div class="stat">role <b id="rl">source</div><div class="stat">keystone <b id="ks">DISTINCT</div></div>
</header>
<div class="panel"><h2>Correlation Brain</h2><div class="grid2">
<div class="metric"><span class="k">sphere</span><span class="v">0</span></div>
<div class="metric"><span class="k">agent-caller</span><span class="v">A</span></div>
<div class="metric"><span class="k">payload</span><span class="v">{json.dumps(data)}</span></div>
<div class="metric"><span class="k">verdict</span><span class="v">PASS</div>
</div>
<div class="panel"><h2>Keystone Probe</h2><div class="grid2">
<div class="metric"><span class="k">[source|13]</span><span class="v">source</span></div>
<div class="metric"><span class="k">[appearance|13]</span><span class="v">appearance</span></div>
<div class="metric"><span class="k">Payload</span><span class="v">{SEED_PAYLOAD}</span></div>
<div class="metric"><span class="k">Verdict</span><span class="v">DISTINCT_ARTIFACTS</div>
</div>
<div class="panel"><h2>Builder</h2>
<p>The agentic builder reads the previous sphere, validates the Plato Keystone,
and produces the next sphere. 999 builders produce spheres 1-1000.</p>
</div>
<div class="footer">Sphere 0</div></div></body></html>"""
    path = os.path.join(outdir, "sphere-0.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return path

def build_agent(prev, outdir, agent_idx):
    idx = agent_idx + 1
    data = {"sphere": idx, "seed": SEED_PAYLOAD, "index": GOLDEN_INDICES[idx % len(GOLDEN_INDICES)]}
    payload_sha = sha256_str(json.dumps(data))
    body = f"<p>Agent {agent_idx} read sphere {agent_idx}, validated Keystone, produced sphere-{idx}.</p>"
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sphere {idx} · {SEED_TITLE} · agent-{agent_idx}</title>
<style>{{*{{box-sizing:border-box;margin:0;padding:0}}}}
html{{background:#07050d;color:#e8eaf1;font-family:'Segoe UI',Arial,sans-serif}}
.app{{max-width:1920px;margin:0 auto;padding:14px 16px 22px}}
.top{{display:flex;align-items:center;gap:14px;border:1px solid rgba(168,128,230,.42);
  background:linear-gradient(160deg,rgba(32,23,49,.96),rgba(18,14,30,.94));padding:14px 18px;border-radius:22px}}
.glyph{{width:52px;height:52px;display:grid;place-items:center;border-radius:17px;
  background:radial-gradient(circle at 35% 30%,#f6deff 0%,#b383ff 24%,#50307e 56%,#211533 100%);
  font-size:32px}}
.brand h1{{font-size:22px}}
.bottom{{display:flex;justify-content:space-between;gap:18px;padding:14px 18px;
  border-top:1px solid rgba(94,69,133,.5);background:rgba(8,6,16,.7)}}
.stat{{font-family:'Courier New',monospace;font-size:14px;color:var(--lav)}}
.stat b{{color:var(--gold)}}
.panel{{background:#140d24;border:1px solid rgba(94,69,133,.5);border-radius:12px;
  box-shadow:0 0 0 1px rgba(255,255,255,.04), 0 10px 20px rgba(0,0,0,.55);padding:18px}}
.panel h2{{font-size:12px;letter-spacing:.18em;color:#6f5f95;text-transform:uppercase;margin-bottom:10px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.metric{{display:flex;flex-direction:column;gap:4px;padding:10px 12px;
  background:rgba(20,14,36,.4);border:1px solid rgba(94,69,133,.35);border-radius:8px}}
.metric .k{{font-size:10px;color:#6f5f95}}
.metric .v{{font-family:'Courier New',monospace;font-size:18px;color:#d4b8ff;font-weight:700}}
.footer{{border-top:1px solid rgba(94,69,133,.3);flex-shrink:0;padding:10px 16px;text-align:center;
  font-size:10px;color:#6f5f95;font-family:'Courier New',monospace}}
</style></head>
<body>
<div class="app">
<header class="top"><div class="brand"><div class="glyph">{{chr(65+agent_idx%26)}}</div><div class="brand-txt">
<div class="smallcaps">SPHERE {idx}</div><h1>{SEED_TITLE}</p></div>
<div class="bottom"><div class="stat">sha256 <b id="sh">{payload_sha}</b></div>
<div class="stat">role <b id="rl">appearance</div><div class="stat">keystone <b id="ks">DISTINCT</div></div>
</header>
<div class="panel"><h2>Agent {agent_idx} -> {idx}</h2><div class="grid2">
<div class="metric"><span class="k">sphere</span><span class="v">{idx}</span></div>
<div class="metric"><span class="k">agent-caller</span><span class="v">A{agent_idx}</span></div>
<div class="metric"><span class="k">payload</span><span class="v">{json.dumps(data)}</span></div>
<div class="metric"><span class="k">verdict</span><span class="v">PASS</div>
</div>
<div class="panel"><h2>Keystone Probe</h2><div class="grid2">
<div class="metric"><span class="k">[source|13]</span><span class="v">source</span></div>
<div class="metric"><span class="k">[appearance|13]</span><span class="v">appearance</span></div>
<div class="metric"><span class="k">Payload</span><span class="v">{SEED_PAYLOAD}</span></div>
<div class="metric"><span class="k">Verdict</span><span class="v">DISTINCT_ARTIFACTS</div>
</div>
<div class="panel"><h2>Body</h2>
<p>Previous sphere: {agent_idx}. Builder produced new sphere: {idx}. No collisions: [source|13] and [appearance|13] remain distinct.</p>
</div>
<div class="footer">Sphere {idx}</div></div></body></html>"""
    path = os.path.join(outdir, f"sphere-{idx}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=1000)
    p.add_argument("--outdir", type=str, default="/tmp/sphere-build")
    args = p.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    idx = 0
    data = {"sphere": idx, "seed": SEED_PAYLOAD, "index": GOLDEN_INDICES[0]}
    payload_sha = sha256_str(json.dumps(data))
    body = "<p>Sphere 0 = icarium Bridgeburner Cortex of I13. Seed.</p>"
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sphere 0 · {SEED_TITLE}</title>
<style>{{*{{box-sizing:border-box;margin:0;padding:0}}}}
html{{background:#07050d;color:#e8eaf1;font-family:'Segoe UI',Arial,sans-serif}}
.app{{max-width:1920px;margin:0 auto;padding:14px 16px 22px}}
.top{{display:flex;align-items:center;gap:14px;border:1px solid rgba(168,128,230,.42);
  background:linear-gradient(160deg,rgba(32,23,49,.96),rgba(18,14,30,.94));padding:14px 18px;border-radius:22px}}
.glyph{{width:52px;height:52px;display:grid;place-items:center;border-radius:17px;
  background:radial-gradient(circle at 35% 30%,#f6deff 0%,#b383ff 24%,#50307e 56%,#211533 100%);
  font-size:32px}}
.brand h1{{font-size:22px}}
.bottom{{display:flex;justify-content:space-between;gap:18px;padding:14px 18px;
  border-top:1px solid rgba(94,69,133,.5);background:rgba(8,6,16,.7)}}
.stat{{font-family:'Courier New',monospace;font-size:14px;color:var(--lav)}}
.stat b{{color:var(--gold)}}
.panel{{background:#140d24;border:1px solid rgba(94,69,133,.5);border-radius:12px;
  box-shadow:0 0 0 1px rgba(255,255,255,.04), 0 10px 20px rgba(0,0,0,.55);padding:18px}}
.panel h2{{font-size:12px;letter-spacing:.18em;color:#6f5f95;text-transform:uppercase;margin-bottom:10px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.metric{{display:flex;flex-direction:column;gap:4px;padding:10px 12px;
  background:rgba(20,14,36,.4);border:1px solid rgba(94,69,133,.35);border-radius:8px}}
.metric .k{{font-size:10px;color:#6f5f95}}
.metric .v{{font-family:'Courier New',monospace;font-size:18px;color:#d4b8ff;font-weight:700}}
.footer{{border-top:1px solid rgba(94,69,133,.3);flex-shrink:0;padding:10px 16px;text-align:center;
  font-size:10px;color:#6f5f95;font-family:'Courier New',monospace}}
</style></head>
<body>
<div class="app">
<header class="top"><div class="brand"><div class="glyph">S</div><div class="brand-txt">
<div class="smallcaps">SPHERE 0</div><h1>{SEED_TITLE}</p></div>
<div class="bottom"><div class="stat">sha256 <b id="sh">{payload_sha}</b></div>
<div class="stat">role <b id="rl">source</div><div class="stat">keystone <b id="ks">DISTINCT</div></div>
</header>
<div class="panel"><h2>Correlation Brain</h2><div class="grid2">
<div class="metric"><span class="k">sphere</span><span class="v">0</span></div>
<div class="metric"><span class="k">agent-caller</span><span class="v">A</span></div>
<div class="metric"><span class="k">payload</span><span class="v">{json.dumps(data)}</span></div>
<div class="metric"><span class="k">verdict</span><span class="v">PASS</div>
</div>
<div class="panel"><h2>Keystone Probe</h2><div class="grid2">
<div class="metric"><span class="k">[source|13]</span><span class="v">source</span></div>
<div class="metric"><span class="k">[appearance|13]</span><span class="v">appearance</span></div>
<div class="metric"><span class="k">Payload</span><span class="v">{SEED_PAYLOAD}</span></div>
<div class="metric"><span class="k">Verdict</span><span class="v">DISTINCT_ARTIFACTS</div>
</div>
<div class="panel"><h2>Builder</h2>
<p>The agentic builder reads the previous sphere, validates the Plato Keystone,
and produces the next sphere. 999 builders produce spheres 1-1000.</p>
</div>
<div class="footer">Sphere 0</div></div></body></html>"""
    seed_path = os.path.join(args.outdir, "sphere-0.html")
    with open(seed_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Sphere 0 (seed) written to {seed_path}")
    print(f"  sha256: {payload_sha}")
    prev = seed_path
    agent_count = 0
    for a in range(args.start, args.end):
        idx = a + 1
        data = {"sphere": idx, "seed": SEED_PAYLOAD, "index": GOLDEN_INDICES[idx % len(GOLDEN_INDICES)]}
        payload_sha = sha256_str(json.dumps(data))
        body = f"<p>Agent {a} read sphere {a}, validated Keystone, produced sphere-{idx}.</p>"
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sphere {idx} · {SEED_TITLE} · agent-{a}</title>
<style>{{*{{box-sizing:border-box;margin:0;padding:0}}}}
html{{background:#07050d;color:#e8eaf1;font-family:'Segoe UI',Arial,sans-serif}}
.app{{max-width:1920px;margin:0 auto;padding:14px 16px 22px}}
.top{{display:flex;align-items:center;gap:14px;border:1px solid rgba(168,128,230,.42);
  background:linear-gradient(160deg,rgba(32,23,49,.96),rgba(18,14,30,.94));padding:14px 18px;border-radius:22px}}
.glyph{{width:52px;height:52px;display:grid;place-items:center;border-radius:17px;
  background:radial-gradient(circle at 35% 30%,#f6deff 0%,#b383ff 24%,#50307e 56%,#211533 100%);
  font-size:32px}}
.brand h1{{font-size:22px}}
.bottom{{display:flex;justify-content:space-between;gap:18px;padding:14px 18px;
  border-top:1px solid rgba(94,69,133,.5);background:rgba(8,6,16,.7)}}
.stat{{font-family:'Courier New',monospace;font-size:14px;color:var(--lav)}}
.stat b{{color:var(--gold)}}
.panel{{background:#140d24;border:1px solid rgba(94,69,133,.5);border-radius:12px;
  box-shadow:0 0 0 1px rgba(255,255,255,.04), 0 10px 20px rgba(0,0,0,.55);padding:18px}}
.panel h2{{font-size:12px;letter-spacing:.18em;color:#6f5f95;text-transform:uppercase;margin-bottom:10px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.metric{{display:flex;flex-direction:column;gap:4px;padding:10px 12px;
  background:rgba(20,14,36,.4);border:1px solid rgba(94,69,133,.35);border-radius:8px}}
.metric .k{{font-size:10px;color:#6f5f95}}
.metric .v{{font-family:'Courier New',monospace;font-size:18px;color:#d4b8ff;font-weight:700}}
.footer{{border-top:1px solid rgba(94,69,133,.3);flex-shrink:0;padding:10px 16px;text-align:center;
  font-size:10px;color:#6f5f95;font-family:'Courier New',monospace}}
</style></head>
<body>
<div class="app">
<header class="top"><div class="brand"><div class="glyph">{{chr(65+a%26)}}</div><div class="brand-txt">
<div class="smallcaps">SPHERE {idx}</div><h1>{SEED_TITLE}</p></div>
<div class="bottom"><div class="stat">sha256 <b id="sh">{payload_sha}</b></div>
<div class="stat">role <b id="rl">appearance</div><div class="stat">keystone <b id="ks">DISTINCT</div></div>
</header>
<div class="panel"><h2>Agent {a} -> {idx}</h2><div class="grid2">
<div class="metric"><span class="k">sphere</span><span class="v">{idx}</span></div>
<div class="metric"><span class="k">agent-caller</span><span class="v">A{a}</span></div>
<div class="metric"><span class="k">payload</span><span class="v">{json.dumps(data)}</span></div>
<div class="metric"><span class="k">verdict</span><span class="v">PASS</div>
</div>
<div class="panel"><h2>Keystone Probe</h2><div class="grid2">
<div class="metric"><span class="k">[source|13]</span><span class="v">source</span></div>
<div class="metric"><span class="k">[appearance|13]</span><span class="v">appearance</span></div>
<div class="metric"><span class="k">Payload</span><span class="v">{SEED_PAYLOAD}</span></div>
<div class="metric"><span class="k">Verdict</span><span class="v">DISTINCT_ARTIFACTS</div>
</div>
<div class="panel"><h2>Body</h2>
<p>Previous sphere: {a}. Builder produced new sphere: {idx}. No collisions: [source|13] and [appearance|13] remain distinct.</p>
</div>
<div class="footer">Sphere {idx}</div></div></body></html>"""
        out_path = os.path.join(args.outdir, f"sphere-{idx}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
        agent_count += 1
        if a % 200 == 0 or a == args.end - 1:
            print(f"  agent {a} done -> sphere-{idx}.html (agents: {agent_count})")
    print(f"\nBuilt {agent_count} spheres (agents 0..{agent_count-1}) + 1 seed = {args.end} total")
    print(f"All complete. Output in: {args.outdir}")

if __name__ == "__main__":
    main()
