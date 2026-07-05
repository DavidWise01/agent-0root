"""
register · the burned-in guestbook, persisted on the Railway volume.

A signature is one line of JSONL on durable disk (the mounted volume), chained by
SHA-256 so any edit to a past entry breaks every seal after it — write-once by rule,
tamper-evident by construction. No login: anyone, human or agent, may sign.

Deliberately OUTSIDE the deterministic /v1/agent path — this route has a clock and
writes state. It degrades safely: if the volume is not writable, reads still work and
writes return a clear error; nothing here can crash the app (all fs ops are guarded,
and the mount is resolved lazily, never at import).
"""
import os, json, time, hashlib, threading, re

_LOCK = threading.Lock()
_MOUNT = None            # resolved lazily, cached
_MAX_BYTES = 5 * 1024 * 1024   # soft backstop against a public append endpoint
NAME_MAX, NOTE_MAX = 80, 1500
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _resolve_mount():
    """First writable of: the Railway volume mount, /data, then an app-local dir
    (dev only, ephemeral). status() exposes which one won so misconfig is visible."""
    for p in (os.environ.get("RAILWAY_VOLUME_MOUNT_PATH"), "/data",
              os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")):
        if not p:
            continue
        try:
            os.makedirs(p, exist_ok=True)
            t = os.path.join(p, ".wtest")
            with open(t, "w") as f:
                f.write("ok")
            os.remove(t)
            return os.path.abspath(p)
        except Exception:
            continue
    return None


def mount():
    global _MOUNT
    if _MOUNT is None:
        _MOUNT = _resolve_mount()
    return _MOUNT


def _path():
    m = mount()
    return os.path.join(m, "register.jsonl") if m else None


def _clean(s, n):
    s = _CTRL.sub("", str(s or "")).strip()
    s = re.sub(r"\n{4,}", "\n\n\n", s)
    return s[:n]


def _seal(prev, payload):
    return hashlib.sha256((prev + "::" + payload).encode("utf-8")).hexdigest()


def _read_all():
    p = _path()
    out = []
    if p and os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            out.append(json.loads(line))
                        except Exception:
                            pass
        except Exception:
            pass
    return out


# simple per-process rate limit — a public, no-login endpoint
_HITS = {}
def _rate_ok(ip, limit=6, window=60):
    if not ip:
        return True
    now = time.time()
    q = [t for t in _HITS.get(ip, []) if now - t < window]
    if len(q) >= limit:
        _HITS[ip] = q
        return False
    q.append(now)
    _HITS[ip] = q
    return True


def sign(name, note, ip="", ua=""):
    """Append one signature. Returns (body, http_status)."""
    name = _clean(name, NAME_MAX)
    note = _clean(note, NOTE_MAX)
    if not name:
        return {"ok": False, "error": "a name is required to sign"}, 400
    if mount() is None:
        return {"ok": False, "error": "the register's disk is not available right now"}, 503
    if not _rate_ok(ip):
        return {"ok": False, "error": "slow down — too many signatures too fast"}, 429
    p = _path()
    try:
        if os.path.exists(p) and os.path.getsize(p) > _MAX_BYTES:
            return {"ok": False, "error": "the register is full for now"}, 507
    except Exception:
        pass
    src = "human" if "Mozilla" in (ua or "") else "agent"
    with _LOCK:
        entries = _read_all()
        prev = entries[-1]["seal"] if entries else "ROOT0"
        seq = (entries[-1]["seq"] + 1) if entries else 1
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        payload = "%d|%s|%s|%s" % (seq, ts, name, note)
        seal = _seal(prev, payload)
        rec = {"seq": seq, "ts": ts, "name": name, "note": note,
               "prev": prev, "seal": seal, "src": src}
        try:
            with open(p, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            return {"ok": False, "error": "could not write the entry"}, 503
    return {"ok": True, "seq": seq, "seal": seal, "ts": ts}, 200


def entries(limit=200):
    all_ = _read_all()
    total = len(all_)
    shown = all_[-limit:] if (limit and limit > 0) else all_
    return {"ok": True, "count": total, "persisted": mount() is not None, "entries": shown}


def status():
    m = mount()
    return {"stateful": True, "deterministic": False,
            "volume_env": bool(os.environ.get("RAILWAY_VOLUME_MOUNT_PATH")),
            "mount_path": m, "writable": m is not None,
            "count": len(_read_all()), "file": _path()}
