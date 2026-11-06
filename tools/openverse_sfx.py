#!/usr/bin/env python3
"""Openverse sound library for sound design: search, download, measure, trim, credit.

Openverse (openverse.org) indexes millions of openly licensed sounds and tracks from
Freesound, Jamendo and Wikimedia Commons. No API key is needed (anonymous limit:
20 searches a minute, 200 a day; searches are cached so repeats cost nothing).

Commercial use only, always: the search never returns NC (non-commercial) or ND
(no derivatives) licences. Default licences are cc0, pdm and by. by needs a credit
line (written to CREDITS.md for the caption or description). by-sa is left out unless
--allow-sa is given, because share-alike can reach the finished video.

Claude can't listen, so every downloaded sound is measured instead: length, peak,
loudness, attack (how fast it hits), tail, brightness (dark / mid / bright) and the
number of hits. Use the numbers to choose between candidates, then place the trimmed WAV.

Usage
  python3 tools/openverse_sfx.py search "whoosh" --kind sfx --max-sec 3
  python3 tools/openverse_sfx.py pick "deep whoosh" --kind sfx --n 4 --project projects/reel-06
  python3 tools/openverse_sfx.py get <openverse-id> [<id> ...] --project projects/reel-06 --name whoosh-01
  python3 tools/openverse_sfx.py pick "cinematic hip hop" --kind music --n 3 --project projects/reel-06
  python3 tools/openverse_sfx.py credits --project projects/reel-06

Files land in <project>/assets/sfx/openverse/: orig/ (the download, committed), a trimmed
48 kHz stereo WAV per sound effect (<name>.wav, ready to place), credits.json and CREDITS.md.
Music tracks (over 60 s) are not trimmed; their WAV goes to work/audio/openverse/ (git
ignores it, `get` rebuilds it) and they are measured for BPM instead of attack and hits.

Hosts (checked 2026-11-06 from the cloud container): api.openverse.org and Jamendo work.
Freesound (most short SFX) answers 403 to this cloud IP, and Wikimedia often answers 429
(shared cloud IP). The tool never fakes a browser to get round that: it reports the block
and prints the sound's page link so the user can download it and upload it in the chat,
then `measure` handles the uploaded file the same way.
  python3 tools/openverse_sfx.py measure raw/whoosh.mp3 --project projects/reel-06 --id <openverse-id>
"""
import argparse, hashlib, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

import numpy as np

API = "https://api.openverse.org/v1/audio/"
UA = "VibeEditingSFX/1.0 (https://github.com/surajnair680/vibe_editing; openverse sound search)"
CACHE = Path.home() / ".cache" / "vibe" / "openverse"
SR = 48000
SAFE = ["cc0", "pdm", "by"]
SA = ["by-sa"]
RETRY = [5, 10, 20, 40]          # waits on 429, like the ElevenLabs rule
BLOCKED = {}                     # host -> reason, filled at run time


# ---------- network ----------
def _get(url, binary=False, timeout=60):
    """GET with an honest User-Agent; retries 429 and 5xx. Returns bytes/str or raises."""
    last = None
    for wait in [0] + RETRY:
        if wait:
            print(f"   waiting {wait}s ({last})", file=sys.stderr)
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json" if not binary else "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return data if binary else data.decode("utf-8")
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code == 429 or e.code >= 500:
                ra = e.headers.get("Retry-After")
                if ra and ra.isdigit() and int(ra) <= 60:
                    time.sleep(int(ra))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            continue
    raise RuntimeError(f"gave up after retries: {last}")


def api(params):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params, doseq=True)
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    f = CACHE / "search" / f"{key}.json"
    if f.exists() and time.time() - f.stat().st_mtime < 7 * 86400:
        return json.loads(f.read_text())
    data = json.loads(_get(url))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data))
    return data


def detail(oid):
    f = CACHE / "detail" / f"{oid}.json"
    if f.exists():
        return json.loads(f.read_text())
    d = json.loads(_get(f"{API}{oid}/?format=json"))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d))
    return d


# ---------- search ----------
def search(q, kind="any", allow_sa=False, cc0_only=False, min_sec=None, max_sec=None,
           source=None, n=10, pages=2):
    lic = ["cc0", "pdm"] if cc0_only else SAFE + (SA if allow_sa else [])
    p = {"q": q, "license": ",".join(lic), "page_size": 20, "mature": "false"}
    if kind == "sfx":
        p["length"] = "shortest"            # under 30 s
        max_sec = max_sec or 10
    elif kind == "music":
        min_sec = min_sec or 30
        p["category"] = "music" if not source else None
    if source:
        p["source"] = source
    p = {k: v for k, v in p.items() if v is not None}
    out, seen = [], set()
    for page in range(1, pages + 1):
        try:
            d = api(dict(p, page=page))
        except urllib.error.HTTPError as e:
            if e.code in (400, 401):        # past the anonymous page limit
                break
            raise
        for r in d.get("results", []):
            if r["id"] in seen or r.get("mature"):
                continue
            seen.add(r["id"])
            if r.get("category") == "pronunciation" or re.match(r"LL-Q\d+", r.get("title") or ""):
                continue                    # people saying the word, not the sound
            if r["license"] in ("by-nc", "by-nc-sa", "by-nd", "by-nc-nd", "sampling+", "nc-sampling+"):
                continue
            dur = (r.get("duration") or 0) / 1000
            if min_sec and dur and dur < min_sec:
                continue
            if max_sec and dur and dur > max_sec:
                continue
            out.append(r)
        if len(out) >= n or page >= d.get("page_count", 1):
            break
    return out[:n]


def host(url):
    return urllib.parse.urlparse(url).hostname or ""


def show(results):
    for i, r in enumerate(results, 1):
        dur = (r.get("duration") or 0) / 1000
        h = host(r["url"])
        flag = f"  [blocked here: {BLOCKED[h]}]" if h in BLOCKED else ""
        print(f"{i:2d}. {r['id']}  {dur:6.2f}s  {r['license']:6s} {r['source']:16s} {r['title'][:52]}{flag}")
        print(f"      by {r.get('creator') or '?'}   page: {r.get('foreign_landing_url')}")


# ---------- audio ----------
def decode(path):
    """Decode any audio file to float32 stereo at 48 kHz (decoded from the start, never seeked)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def db(x):
    return 20 * np.log10(max(float(x), 1e-9))


def measure(a):
    """Numbers that stand in for listening."""
    mono = a.mean(1)
    hop = SR // 100                                       # 10 ms envelope
    nfr = max(1, len(mono) // hop)
    env = np.sqrt(np.mean(mono[: nfr * hop].reshape(nfr, hop) ** 2, axis=1) + 1e-12)
    env_db = 20 * np.log10(env)
    peak_i = int(np.argmax(env))
    pk = env_db[peak_i]
    above = np.where(env_db > pk - 40)[0]
    start = above[0] if len(above) else 0
    tail = np.where(env_db > pk - 30)[0]
    end = tail[-1] if len(tail) else nfr - 1
    # brightness: spectral centroid of the loudest 300 ms
    s0 = max(0, peak_i * hop - SR // 10)
    seg = mono[s0: s0 + int(0.3 * SR)]
    if len(seg) < 1024:
        seg = np.pad(seg, (0, 1024 - len(seg)))
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1 / SR)
    cent = float((spec * freqs).sum() / (spec.sum() + 1e-12))
    low = float(spec[freqs < 150].sum() / (spec.sum() + 1e-12))
    # hits: onsets where the envelope jumps 9 dB within 30 ms
    jumps = env_db[3:] - env_db[:-3]
    ons = np.where((jumps > 9) & (env_db[3:] > pk - 25))[0]
    hits = int(np.sum(np.diff(np.r_[-100, ons]) > 10))
    rms_active = env[start: end + 1]
    return {
        "length_s": round(len(mono) / SR, 3),
        "sound_s": round((end - start + 1) / 100, 2),           # audible part (within 30 dB of peak)
        "peak_dbfs": round(db(np.abs(a).max()), 1),
        "loudness_db": round(db(np.sqrt(np.mean(rms_active ** 2))), 1),
        "attack_ms": int((peak_i - start) * 10),                 # up to 50 ms = hit, 50-400 = swoosh, 400+ = swell / riser
        "peak_at_s": round(peak_i / 100, 2),
        "tail_ms": int((end - peak_i) * 10),
        "brightness_hz": int(cent),
        "tone": "dark" if cent < 1200 else "bright" if cent > 4000 else "mid",
        "low_end": round(low, 2),                                # share of energy under 150 Hz
        "hits": hits,
        "shape": ("hit" if (peak_i - start) <= 5 else "swell" if (peak_i - start) >= 40 else "swoosh"),
    }


def measure_music(a):
    """Tempo, loudness and tone for a track (attack / hits mean nothing on a song)."""
    mono = a.mean(1)
    hop = SR // 100
    nfr = len(mono) // hop
    env = np.sqrt(np.mean(mono[: nfr * hop].reshape(nfr, hop) ** 2, axis=1) + 1e-12)
    seg = env[: 60 * 100]
    flux = np.maximum(np.diff(np.log(seg)), 0)
    flux -= flux.mean()
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    lags = np.arange(len(ac))
    ok = (lags >= 100 * 60 // 180) & (lags <= 100 * 60 // 70)          # 70 to 180 BPM
    lag = lags[ok][np.argmax(ac[ok])]
    spec = np.abs(np.fft.rfft(mono[: SR * 30]))
    freqs = np.fft.rfftfreq(min(len(mono), SR * 30), 1 / SR)
    cent = float((spec * freqs).sum() / (spec.sum() + 1e-12))
    return {
        "length_s": round(len(mono) / SR, 2),
        "bpm": round(6000 / lag, 1),
        "peak_dbfs": round(db(np.abs(a).max()), 1),
        "loudness_db": round(db(np.sqrt(np.mean(env ** 2))), 1),
        "quiet_start_s": round(float(np.argmax(env > env.max() * 0.1)) / 100, 2),
        "brightness_hz": int(cent),
        "tone": "dark" if cent < 1200 else "bright" if cent > 4000 else "mid",
        "shape": "music",
    }


def trim(a, floor_db=-50, pad=0.01, fade=0.006):
    """Cut leading and trailing silence (relative to the peak), keep the full decay, short fades."""
    mono = np.abs(a).max(1)
    pk = mono.max()
    if pk <= 0:
        return a
    thr = pk * 10 ** (floor_db / 20)
    idx = np.where(mono > thr)[0]
    s = max(0, idx[0] - int(pad * SR))
    e = min(len(a), idx[-1] + int(pad * SR * 4))
    b = a[s:e].copy()
    nf = min(int(fade * SR), len(b) // 4)
    if nf:
        b[:nf] *= np.linspace(0, 1, nf)[:, None]
        b[-nf:] *= np.linspace(1, 0, nf)[:, None]
    return b


def write_wav(path, a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                    "-c:a", "pcm_s24le", str(path)], input=a.astype(np.float32).tobytes(), check=True)


# ---------- project files ----------
def outdir(project):
    d = Path(project) / "assets" / "sfx" / "openverse"
    d.mkdir(parents=True, exist_ok=True)
    return d


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "sound").lower()).strip("-")[:40] or "sound"


def credit(project, r, name, m, files):
    d = outdir(project)
    cj = d / "credits.json"
    data = json.loads(cj.read_text()) if cj.exists() else {}
    data[name] = {
        "openverse_id": r["id"], "title": r.get("title"), "creator": r.get("creator"),
        "license": r["license"], "license_version": r.get("license_version"),
        "license_url": r.get("license_url"), "source": r.get("source"),
        "page": r.get("foreign_landing_url"), "attribution": r.get("attribution"),
        "needs_credit": r["license"] not in ("cc0", "pdm"), "files": files, "measure": m,
    }
    cj.write_text(json.dumps(data, indent=2))
    lines = ["# Sound credits (Openverse)", "",
             "Put the lines marked 'credit needed' in the post caption or video description.", ""]
    for k, v in sorted(data.items()):
        tag = "credit needed" if v["needs_credit"] else "no credit needed"
        lines.append(f"- **{k}** ({tag}): {v['attribution'] or v['title']}  {v['page']}")
    (d / "CREDITS.md").write_text("\n".join(lines) + "\n")


def fetch(r, project, name=None):
    """Download one result. Returns (wav_path, measure) or None when the host blocks us."""
    d = outdir(project)
    name = name or f"{slug(r['title'])}-{r['id'][:6]}"
    h = host(r["url"])
    if h in BLOCKED:
        return None
    ext = (r.get("filetype") or Path(urllib.parse.urlparse(r["url"]).path).suffix.strip(".") or "mp3").lower()
    ext = {"mp32": "mp3", "mpeg": "mp3", "oga": "ogg"}.get(ext, ext)[:4]
    orig = d / "orig" / f"{name}.{ext}"
    orig.parent.mkdir(exist_ok=True)
    if not orig.exists():
        try:
            data = _get(r["url"], binary=True, timeout=120)
        except (urllib.error.HTTPError, RuntimeError) as e:
            BLOCKED[h] = str(getattr(e, "code", e))
            print(f"   {h} refused the download ({BLOCKED[h]}). Download it by hand from:\n   {r.get('foreign_landing_url')}")
            return None
        orig.write_bytes(data)
    a = decode(orig)
    wav, t, m = place(a, project, name)
    credit(project, r, name, m, {"original": str(orig), "wav": str(wav)})
    return wav, m


def place(a, project, name):
    """Sound effects: trimmed WAV in assets (small, committed). Music: whole track as WAV in
    work/audio/openverse (ignored by git; the original mp3 in assets is committed)."""
    if len(a) > 60 * SR:
        wd = Path(project) / "work" / "audio" / "openverse"
        wd.mkdir(parents=True, exist_ok=True)
        wav = wd / f"{name}.wav"
        write_wav(wav, a)
        return wav, a, measure_music(a)
    t = trim(a)
    wav = outdir(project) / f"{name}.wav"
    write_wav(wav, t)
    return wav, t, measure(t)


def show_measure(name, m):
    if m.get("shape") == "music":
        print(f"   {name}: {m['length_s']}s track, about {m['bpm']} BPM (or half), {m['tone']} ({m['brightness_hz']} Hz), "
              f"music starts {m['quiet_start_s']}s in, peak {m['peak_dbfs']} dBFS, loudness {m['loudness_db']} dB")
        return
    print(f"   {name}: {m['sound_s']}s audible ({m['length_s']}s file), {m['shape']}, attack {m['attack_ms']} ms, "
          f"peak at {m['peak_at_s']}s, tail {m['tail_ms']} ms, {m['tone']} ({m['brightness_hz']} Hz), "
          f"low end {m['low_end']}, hits {m['hits']}, peak {m['peak_dbfs']} dBFS, loudness {m['loudness_db']} dB")


# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--kind", choices=["sfx", "music", "any"], default="any")
        p.add_argument("--allow-sa", action="store_true", help="also allow CC BY-SA")
        p.add_argument("--cc0-only", action="store_true", help="only CC0 / public domain (no credit needed)")
        p.add_argument("--min-sec", type=float)
        p.add_argument("--max-sec", type=float)
        p.add_argument("--source", help="freesound, jamendo or wikimedia_audio")

    s = sub.add_parser("search"); s.add_argument("query"); common(s); s.add_argument("--n", type=int, default=10)
    s.add_argument("--json", help="also save the results here")
    p = sub.add_parser("pick", help="search, download the first N that download, measure them")
    p.add_argument("query"); common(p); p.add_argument("--n", type=int, default=4)
    p.add_argument("--project", required=True); p.add_argument("--name", help="name prefix, e.g. whoosh")
    g = sub.add_parser("get"); g.add_argument("ids", nargs="+"); g.add_argument("--project", required=True)
    g.add_argument("--name", help="file name (single id) or prefix")
    mm = sub.add_parser("measure", help="trim, measure and credit a file the user downloaded by hand")
    mm.add_argument("file"); mm.add_argument("--project", required=True); mm.add_argument("--id", required=True)
    mm.add_argument("--name")
    c = sub.add_parser("credits"); c.add_argument("--project", required=True)
    a = ap.parse_args()

    kw = lambda: dict(kind=a.kind, allow_sa=a.allow_sa, cc0_only=a.cc0_only, min_sec=a.min_sec,
                      max_sec=a.max_sec, source=a.source)
    if a.cmd == "search":
        res = search(a.query, n=a.n, **kw())
        show(res)
        if a.json:
            Path(a.json).write_text(json.dumps(res, indent=2))
    elif a.cmd == "pick":
        res = search(a.query, n=max(a.n * 4, 12), **kw())
        got, skipped = 0, []
        for r in res:
            if got >= a.n:
                break
            name = f"{a.name}-{got + 1:02d}" if a.name else None
            print(f"-> {r['title'][:60]} ({r['license']}, {r['source']})")
            out = fetch(r, a.project, name)
            if out is None:
                skipped.append(r)
                continue
            got += 1
            show_measure(out[0].stem, out[1])
        print(f"\n{got} downloaded to {outdir(a.project)}")
        if skipped:
            print(f"{len(skipped)} blocked by their host. Download by hand and run `measure`:")
            for r in skipped[:8]:
                print(f"   {r['id']}  {r['title'][:50]}  {r['foreign_landing_url']}")
    elif a.cmd == "get":
        for i, oid in enumerate(a.ids):
            r = detail(oid)
            name = a.name if (a.name and len(a.ids) == 1) else (f"{a.name}-{i + 1:02d}" if a.name else None)
            out = fetch(r, a.project, name)
            if out:
                show_measure(out[0].stem, out[1])
    elif a.cmd == "measure":
        r = detail(a.id)
        name = a.name or f"{slug(r['title'])}-{r['id'][:6]}"
        wav, t, m = place(decode(a.file), a.project, name)
        credit(a.project, r, name, m, {"original": str(a.file), "wav": str(wav)})
        show_measure(name, m)
    elif a.cmd == "credits":
        f = outdir(a.project) / "CREDITS.md"
        print(f.read_text() if f.exists() else "no Openverse sounds in this project yet")


if __name__ == "__main__":
    main()
