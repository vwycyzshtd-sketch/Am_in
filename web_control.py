from __future__ import annotations

import atexit
import os
import secrets
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

PROJECT_ROOT = Path(__file__).resolve().parent
RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", PROJECT_ROOT / "runtime"))
LOG_PATH = RUNTIME_DIR / "mcp.log"
CONTROL_USER = os.getenv("CONTROL_USER", "amin")
CONTROL_PASSWORD = os.getenv("CONTROL_PASSWORD", "")

security = HTTPBasic(auto_error=False)
app = FastAPI(title="Am_in Control", version="1.0.0")


class MCPProcessManager:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._proc: subprocess.Popen[str] | None = None
        self._started_at: float | None = None
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    def _refresh(self) -> None:
        if self._proc is not None and self._proc.poll() is not None:
            self._proc = None
            self._started_at = None

    def status(self) -> dict[str, object]:
        with self._lock:
            self._refresh()
            running = self._proc is not None
            return {
                "running": running,
                "pid": self._proc.pid if running else None,
                "uptime_seconds": int(time.time() - self._started_at) if running and self._started_at else 0,
                "compression_level": os.getenv("MCP_COMPRESSION_LEVEL", "medium"),
            }

    def start(self) -> dict[str, object]:
        with self._lock:
            self._refresh()
            if self._proc is not None:
                return self.status()

            env = os.environ.copy()
            env.setdefault("PYTHONUNBUFFERED", "1")
            log_file = LOG_PATH.open("a", encoding="utf-8", buffering=1)
            try:
                self._proc = subprocess.Popen(
                    [sys.executable, "run_mcp_compressed.py"],
                    cwd=PROJECT_ROOT,
                    env=env,
                    stdin=subprocess.PIPE,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    start_new_session=True,
                )
            finally:
                log_file.close()

            self._started_at = time.time()
            time.sleep(0.35)
            self._refresh()
            if self._proc is None:
                raise RuntimeError("MCP process exited during startup. Check /api/logs.")
            return self.status()

    def stop(self) -> dict[str, object]:
        with self._lock:
            self._refresh()
            if self._proc is None:
                return self.status()

            proc = self._proc
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=8)
            except ProcessLookupError:
                pass
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait(timeout=3)
            finally:
                if proc.stdin:
                    try:
                        proc.stdin.close()
                    except OSError:
                        pass
                self._proc = None
                self._started_at = None
            return self.status()

    def restart(self) -> dict[str, object]:
        self.stop()
        return self.start()

    def tail_logs(self, lines: int = 100) -> str:
        if not LOG_PATH.exists():
            return "No MCP logs yet."
        lines = max(1, min(lines, 300))
        with LOG_PATH.open("r", encoding="utf-8", errors="replace") as fh:
            data = fh.readlines()
        return "".join(data[-lines:])


manager = MCPProcessManager()
atexit.register(manager.stop)


def require_auth(credentials: HTTPBasicCredentials | None = Depends(security)) -> None:
    if not CONTROL_PASSWORD:
        raise HTTPException(status_code=503, detail="CONTROL_PASSWORD is not configured")
    if credentials is None:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": 'Basic realm="Am_in Control"'})
    user_ok = secrets.compare_digest(credentials.username, CONTROL_USER)
    pass_ok = secrets.compare_digest(credentials.password, CONTROL_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": 'Basic realm="Am_in Control"'})


def require_control_action(x_control_action: str | None = Header(default=None)) -> None:
    if x_control_action != "Am-in-web-control":
        raise HTTPException(status_code=403, detail="Missing control action header")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/status", dependencies=[Depends(require_auth)])
def api_status() -> dict[str, object]:
    return manager.status()


@app.post("/api/start", dependencies=[Depends(require_auth), Depends(require_control_action)])
def api_start() -> dict[str, object]:
    try:
        return manager.start()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/stop", dependencies=[Depends(require_auth), Depends(require_control_action)])
def api_stop() -> dict[str, object]:
    return manager.stop()


@app.post("/api/restart", dependencies=[Depends(require_auth), Depends(require_control_action)])
def api_restart() -> dict[str, object]:
    try:
        return manager.restart()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/logs", response_class=PlainTextResponse, dependencies=[Depends(require_auth)])
def api_logs(lines: int = Query(default=100, ge=1, le=300)) -> str:
    return manager.tail_logs(lines)


@app.get("/", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
def dashboard() -> str:
    return """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
  <title>Am_in MCP Control</title>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0b1020;color:#eef2ff;margin:0;padding:24px}
    .wrap{max-width:720px;margin:auto}.card{background:#151b2f;border:1px solid #2a3352;border-radius:18px;padding:18px;margin-bottom:14px}
    h1{font-size:24px;margin:0 0 8px}.muted{color:#a7b0cc}.status{font-size:18px;font-weight:700}
    button{border:0;border-radius:12px;padding:14px 18px;margin:6px;font-size:16px;font-weight:700;cursor:pointer}
    .start{background:#d1fae5}.stop{background:#fee2e2}.restart{background:#dbeafe}
    pre{white-space:pre-wrap;word-break:break-word;background:#090d18;padding:14px;border-radius:12px;max-height:340px;overflow:auto;font-size:12px}
  </style>
</head>
<body><div class="wrap">
  <div class="card"><h1>Am_in MCP Control</h1><div class="muted">کنترل Docker/MCP از موبایل</div></div>
  <div class="card"><div id="status" class="status">در حال دریافت وضعیت…</div><div id="meta" class="muted"></div></div>
  <div class="card">
    <button class="start" onclick="act('start')">Start</button>
    <button class="stop" onclick="act('stop')">Stop</button>
    <button class="restart" onclick="act('restart')">Restart</button>
  </div>
  <div class="card"><div class="status">Logs</div><pre id="logs">—</pre></div>
</div>
<script>
async function refresh(){
  const s=await fetch('/api/status').then(r=>r.json());
  document.getElementById('status').textContent=s.running?'🟢 MCP روشن است':'⚫ MCP خاموش است';
  document.getElementById('meta').textContent=`PID: ${s.pid??'-'} | Uptime: ${s.uptime_seconds}s | Compression: ${s.compression_level}`;
  const l=await fetch('/api/logs?lines=120').then(r=>r.text()); document.getElementById('logs').textContent=l;
}
async function act(name){
  const r=await fetch('/api/'+name,{method:'POST',headers:{'X-Control-Action':'Am-in-web-control'}});
  if(!r.ok){alert(await r.text());} await refresh();
}
refresh(); setInterval(refresh,5000);
</script></body></html>"""
