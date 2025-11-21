# streamlit_app.py -- place this at project root (next to the src/ folder)
import sys
from pathlib import Path
import importlib
import traceback
import os
import json
import time
import random

# -------------------------
# Client-side animation HTML (complete document)
# -------------------------
ANIM_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <style>
    body { margin:0; font-family: "Source Code Pro", monospace; background: transparent; color:#00ffd8; }
    .pb-wrap { background: linear-gradient(180deg,#000 0%, #001212 60%); border-radius:8px; padding:16px; border:1px solid rgba(0,255,215,0.06); box-shadow:0 10px 30px rgba(0,0,0,0.6); }
    .ascii { white-space:pre; font-size:12px; color:#00ffd8; text-shadow:0 0 8px rgba(0,255,215,0.15); }
    .typing-line { border-left: 2px solid rgba(0,255,216,0.6); padding-left:8px; display:inline-block; animation: caret 1s steps(1) infinite; }
    @keyframes caret { 50% { border-color: transparent; } }
    .fake-log { background: rgba(0,0,0,0.6); color:#b8fff0; padding:10px; border-radius:6px; font-family: monospace; max-height:220px; overflow:auto; border:1px solid rgba(0,255,216,0.03); }
    .neon-bar { height:10px; background: linear-gradient(90deg,#00ffd8,#00a9ff); border-radius:999px; box-shadow:0 0 18px rgba(0,255,216,0.12); }
    .btn { padding:6px 10px; border-radius:6px; background:#021114; color:#00ffd8; border:1px solid rgba(0,255,216,0.2); cursor:pointer; font-weight:700; }
    .controls { display:flex; gap:8px; margin-top:8px; align-items:center; }
    .meta { font-size:12px; color:#9fffe9; margin-left:auto; }
    /* small responsive tweaks */
    @media (max-width:600px) {
      .pb-wrap { padding:10px; }
      .fake-log { max-height:160px; font-size:11px; }
    }
  </style>
</head>
<body>
  <div class="pb-wrap" id="pb-root">
    <div style="display:flex; align-items:center; gap:12px;">
      <div style="font-weight:900; font-size:14px; color:#00ffd8;">PAYBUDDY SECURITY SUITE</div>
      <div style="flex:1"></div>
      <div class="meta">Session: DEV • Console v1</div>
    </div>

    <div style="margin-top:8px;">
      <div class="ascii" id="ascii-banner"></div>
      <div style="margin-top:8px;">
        <div class="typing-line" id="boot-line"></div>
      </div>
      <div style="margin-top:12px;">
        <div class="neon-bar" id="neon-bar" style="width:0%"></div>
      </div>

      <div style="margin-top:12px; display:flex; gap:12px; align-items:flex-start;">
        <div style="flex:3">
          <div class="fake-log" id="fake-log">[console idle] — click PLAY to start demo logs...</div>
        </div>
        <div style="flex:1">
          <div style="display:flex; flex-direction:column; gap:8px;">
            <button class="btn" id="play-btn">▶ PLAY</button>
            <button class="btn" id="stop-btn">■ STOP</button>
            <button class="btn" id="clear-btn">✖ CLEAR</button>
            <div style="margin-top:8px; font-size:12px; color:#8affdf;">Demo controls</div>
          </div>
        </div>
      </div>
    </div>
  </div>

<script>
(function(){
  // ASCII art lines
  const ascii = [
"  ____  _            ____        _          _ _ ",
" |  _ \\| | __ _  ___| __ )  ___ | |__   ___| | |",
" | |_) | |/ _` |/ __|  _ \\ / _ \\| '_ \\ / _ \\ | |",
" |  __/| | (_| | (__| |_) | (_) | |_) |  __/ | |",
" |_|   |_|\\__,_|\\___|____/ \\___/|_.__/ \\___|_|_|"
  ];

  // Boot messages (typing)
  const boot = [
    "[*] Boot sequence initiated...",
    "[*] Loading modules...",
    "[*] Establishing secure session...",
    "[*] Verifying integrity checks...",
    "[*] System ready."
  ];

  const bannerEl = document.getElementById('ascii-banner');
  const bootEl = document.getElementById('boot-line');
  const neonBar = document.getElementById('neon-bar');
  const logEl = document.getElementById('fake-log');
  const playBtn = document.getElementById('play-btn');
  const stopBtn = document.getElementById('stop-btn');
  const clearBtn = document.getElementById('clear-btn');

  // Ensure elements exist
  if (!bannerEl || !bootEl || !neonBar || !logEl) return;

  // Type ASCII banner instantly (keeps spacing)
  bannerEl.textContent = ascii.join("\n");

  // Typing effect for boot messages
  let bootIndex = 0;
  let charIndex = 0;
  let bootInterval = null;
  function startBoot() {
    if (bootInterval) clearInterval(bootInterval);
    bootIndex = 0; charIndex = 0;
    bootEl.textContent = "";
    bootInterval = setInterval(()=> {
      if (bootIndex >= boot.length) { clearInterval(bootInterval); bootEl.textContent = boot.join(" "); bootInterval=null; return; }
      const line = boot[bootIndex];
      charIndex++;
      bootEl.textContent = line.slice(0, charIndex);
      if (charIndex >= line.length) { bootIndex++; charIndex=0; }
    }, 40);
  }

  // Neon progress simulation
  let progress = 0;
  let progressInterval = null;
  function startProgress() {
    if (progressInterval) clearInterval(progressInterval);
    progress = 0;
    neonBar.style.width = '0%';
    progressInterval = setInterval(()=> {
      if (progress >= 100) { clearInterval(progressInterval); progressInterval=null; return; }
      progress += Math.random()*6;
      neonBar.style.width = Math.min(100, progress) + '%';
    }, 150);
  }

  // Fake live logs stream
  const sample = [
    "Initialized module scanner",
    "Socket pool created",
    "Fingerprint signature verified",
    "Integrity hash OK",
    "Subdomain probe started",
    "PCAP writer ready",
    "Report manifest updated",
    "Stress test queued",
    "Banner grab successful",
    "Hash-check offline list loaded",
    "Connection timeout (retry)",
    "Response 200 OK",
    "Banner parse OK",
    "Saving evidence file",
    "Uploading to evidence store (simulated)"
  ];
  let logTimer = null;
  function startLogs() {
    stopLogs();
    logTimer = setInterval(()=> {
      const now = new Date();
      const t = now.toISOString().split('T')[1].split('.')[0];
      const sev = ["INFO","DBG","WARN","OK","ERR"][Math.floor(Math.random()*5)];
      const txt = sample[Math.floor(Math.random()*sample.length)];
      const line = `${t} [${sev}] -- ${txt}`;
      // prepend
      logEl.innerHTML = line + '<br>' + logEl.innerHTML;
      // keep only 200 lines visually
      const lines = logEl.innerHTML.split('<br>');
      if (lines.length > 200) { logEl.innerHTML = lines.slice(0,200).join('<br>'); }
    }, 350 + Math.random()*300);
  }
  function stopLogs() {
    if (logTimer) { clearInterval(logTimer); logTimer = null; }
  }

  // Buttons
  playBtn.addEventListener('click', ()=> {
    startBoot(); startProgress(); startLogs();
  });
  stopBtn.addEventListener('click', ()=> {
    stopLogs(); if (typeof progressInterval !== 'undefined' && progressInterval) { clearInterval(progressInterval); progressInterval=null; }
  });
  clearBtn.addEventListener('click', ()=> {
    logEl.innerHTML = '[console cleared]';
  });

  // auto-start small animation for UX, after load
  startBoot(); setTimeout(startProgress, 500); setTimeout(startLogs, 700);
})();
</script>
</body>
</html>
"""

# -------------------------
# Ensure src/ is importable
# -------------------------
ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# -------------------------
# Safe import helper (returns module or dummy with __error__)
# -------------------------
def safe_import(module_name):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        # create a minimal dummy object that carries the import exception for diagnostics
        class _M:
            pass
        m = _M()
        m.__error__ = e
        return m

# backend modules (optional)
scanner = safe_import("scanner")
auth_test = safe_import("auth_test")
stress_mod = safe_import("stress")
footprint = safe_import("footprint")
pcap_mod = safe_import("pcap")
reporting = safe_import("reporting")
logger_mod = safe_import("logger")

# -------------------------
# Map expected function names to whatever exists in modules (fallbacks)
# -------------------------
def get_callable(mod, *names, fallback=None):
    for n in names:
        if hasattr(mod, n):
            return getattr(mod, n)
    return fallback

# scanner
run_scan = get_callable(scanner, "run_scan", "sync_port_scan",
                        fallback=lambda *a, **k: {"error":"scanner module missing"})
sync_port_scan = get_callable(scanner, "sync_port_scan", fallback=run_scan)

# auth functions
check_password_strength = get_callable(auth_test, "check_password_strength", "policy_check",
                                       fallback=lambda pw: {"error":"auth module missing"})
simulate_hash_check = get_callable(auth_test, "simulate_hash_check", "offline_hash_check",
                                   fallback=lambda lst: {"error":"auth module missing"})

# stress
run_stress_test = get_callable(stress_mod, "run_stress_test", "stress_test",
                              fallback=lambda url, clients, duration: ({"error":"stress module missing"}, None))

# footprint
run_directory_finder = get_callable(footprint, "run_directory_finder", "check_paths",
                                    fallback=lambda url: {"error":"footprint missing"})
run_subdomain_finder = get_callable(footprint, "run_subdomain_finder", "probe_subdomains",
                                    fallback=lambda domain: {"error":"footprint missing"})

# pcap
capture_packets = get_callable(pcap_mod, "capture_packets", "capture_scapy",
                               fallback=lambda *a, **k: (None, {"error":"pcap missing"}))
analyze_pcap = get_callable(pcap_mod, "analyze_pcap_file", fallback=lambda *a, **k: {"error":"pcap missing"})

# reporting
generate_json_summary = get_callable(reporting, "generate_json_summary", "generate_manifest",
                                     fallback=lambda: {"error":"reporting missing"})
generate_docx_report = get_callable(reporting, "generate_docx_report", fallback=lambda: {"error":"reporting missing"})

# logger tail
read_log_tail = get_callable(logger_mod, "read_log_tail", "tail_logs",
                             fallback=lambda n=200: "No logs available (logger module missing)")

# -------------------------
# Streamlit UI
# -------------------------
import streamlit as st
import streamlit.components.v1 as components

# set page config as early as possible
st.set_page_config(page_title="PayBuddy Toolkit", layout="wide")

# GLOBAL HACKING THEME CSS (streamlit-level)
st.markdown(
    """
<style>
/* Base / background */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at top left, #001217 0%, #000000 60%);
    color: #00ffd8;
    font-family: "Source Code Pro", monospace;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#040404, #0a0a0a);
    color: #00ffd8;
    border-right: 1px solid rgba(0,255,215,0.06);
}

/* Titles neon */
h1, h2, h3 { color: #00ffd8 !important; text-shadow: 0 0 10px rgba(0,255,215,0.25); }

/* Buttons neon */
.stButton>button {
    background: linear-gradient(90deg,#021114, #001212);
    color: #00ffd8;
    border: 1px solid rgba(0,255,216,0.9);
    box-shadow: 0 0 12px rgba(0,255,216,0.08);
    border-radius: 6px;
    padding: 0.5em 1.0em;
    font-weight: 700;
}
.stButton>button:hover { transform: translateY(-1px); }

/* Inputs */
input, textarea, [role="textbox"] { background: #000; color: #00ffd8 !important; border: 1px solid rgba(0,255,216,0.2) !important; }

/* Code blocks */
.stCodeBlock pre, code { background: #000 !important; color: #00ffd8 !important; border-left: 4px solid #00ffd8; }

/* Panels */
.panel { background: rgba(0,0,0,0.45); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.02); box-shadow: 0 6px 24px rgba(0,0,0,0.5); }
.badge { display:inline-block; background: rgba(0,255,216,0.06); border: 1px solid rgba(0,255,216,0.12); color: #00ffd8; padding: 4px 8px; border-radius: 999px; font-weight:700; font-size:12px; }
</style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Render animation component
# -------------------------
# Using a full HTML document tends to be more robust in Streamlit's component sandbox.
components.html(ANIM_HTML, height=420, scrolling=True)

# -------------------------
# App directories
# -------------------------
EVIDENCE_DIR = ROOT / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = EVIDENCE_DIR / "outputs"; OUTPUT_DIR.mkdir(exist_ok=True)
PCAP_DIR = EVIDENCE_DIR / "pcaps"; PCAP_DIR.mkdir(exist_ok=True)
SS_DIR = EVIDENCE_DIR / "screenshots"; SS_DIR.mkdir(exist_ok=True)

# -------------------------
# Diagnostics + Sidebar
# -------------------------
with st.expander("Diagnostics (backend import errors)"):
    for name, mod in [
        ("scanner", scanner), ("auth_test", auth_test), ("stress", stress_mod),
        ("footprint", footprint), ("pcap", pcap_mod), ("reporting", reporting),
        ("logger", logger_mod)
    ]:
        if hasattr(mod, "__error__"):
            st.warning(f"Module '{name}' import failed: {mod.__error__}")
            tb = "".join(traceback.format_exception_only(type(mod.__error__), mod.__error__))
            st.code(tb)
        else:
            st.success(f"Module '{name}' loaded")

menu = st.sidebar.selectbox(
    "Module",
    [
        "Dashboard", "Port Scanner", "Password Assessment", "Stress Tester",
        "Footprint", "Packet Capture", "Reporting", "Evidence", "Toolkit Logs"
    ],
)

# -------------------------
# Dashboard
# -------------------------
if menu == "Dashboard":
    st.header("Toolkit Overview")
    st.markdown("### 🔧 Features (based on loaded backend modules)")
    st.markdown(
        """
- Port scanner (**run_scan / sync_port_scan**)  
- Password assessment (**check_password_strength / policy_check**)  
- Stress tester (**run_stress_test / stress_test**)  
- Footprint (**check_paths / probe_subdomains**)  
- Packet capture (**capture_scapy / pyshark**)  
- Reporting (**generate_json_summary / generate_docx_report**)  
        """
    )
    st.info("If a module is missing you will see a warning in Diagnostics above.")
    st.success("Console online — choose a module from the left panel.")

    st.markdown("### Live Console (Python-updated preview)")
    if st.button("Emit sample log"):
        t = time.strftime("%H:%M:%S", time.gmtime(time.time()))
        st.write(f"{t} [INFO] -- Sample log emitted from Python backend")

# -------------------------
# Port Scanner
# -------------------------
elif menu == "Port Scanner":
    st.header("Port Scanner")
    target = st.text_input("Target (IP or hostname)", "127.0.0.1")
    ports = st.text_input("Ports (comma separated)", "22,80,443")
    max_workers = st.slider("Max workers", 1, 200, 50)
    if st.button("Start Scan"):
        try:
            ports_list = [int(p.strip()) for p in ports.split(",") if p.strip()]
        except Exception:
            st.error("Invalid ports list")
            ports_list = []
        if ports_list:
            with st.spinner("Scanning..."):
                res = run_scan(target, ports_list, max_workers=max_workers)
            st.json(res)
            # save evidence
            safe_target = target.replace(":", "_").replace("/", "_")
            out = OUTPUT_DIR / f"scan_{int(time.time())}_{safe_target}.json"
            with open(out, "w") as f:
                json.dump(res, f, indent=2)
            st.success(f"Saved result to {out}")

# -------------------------
# Password Assessment
# -------------------------
elif menu == "Password Assessment":
    st.header("Password assessment")
    pw = st.text_input("Password", type="password")
    if st.button("Check strength"):
        res = check_password_strength(pw)
        st.json(res)
    st.markdown("---")
    st.subheader("Offline hash simulation")
    file = st.file_uploader("Upload hash list (.txt)", type=["txt"])
    if file and st.button("Simulate hash check"):
        hashes = file.getvalue().decode("utf-8").splitlines()
        out = simulate_hash_check(hashes)
        st.json(out)
        outpath = OUTPUT_DIR / f"hashsim_{int(time.time())}.json"
        with open(outpath, "w") as fp:
            json.dump(out, fp, indent=2)
        st.success(f"Saved to {outpath}")

# -------------------------
# Stress Tester
# -------------------------
elif menu == "Stress Tester":
    st.header("Stress Tester (lab only)")
    url = st.text_input("Target URL", "http://127.0.0.1:8000")
    clients = st.number_input("Clients", 1, 200, 20)
    duration = st.number_input("Duration (s)", 1, 120, 5)
    if st.button("Run test"):
        with st.spinner("Running..."):
            try:
                out = run_stress_test(url, clients, duration)
                # run_stress_test may return tuple (summary, figpath) or single dict
                if isinstance(out, tuple):
                    summary, fig = out
                else:
                    summary, fig = out, None
            except Exception as e:
                summary, fig = {"error": str(e)}, None
        st.json(summary)
        if fig:
            try:
                st.image(fig)
            except Exception:
                st.text(f"Plot saved at: {fig}")

# -------------------------
# Footprint
# -------------------------
elif menu == "Footprint":
    st.header("Footprint")
    base = st.text_input("Base URL", "http://127.0.0.1:8000")
    domain = st.text_input("Domain", "lab.local")
    if st.button("Run path check"):
        with st.spinner("Running path checks..."):
            res = run_directory_finder(base)
        st.json(res)
    if st.button("Probe subs"):
        with st.spinner("Probing subs..."):
            res = run_subdomain_finder(domain)
        st.json(res)

# -------------------------
# Packet Capture
# -------------------------
elif menu == "Packet Capture":
    st.header("Packet capture")
    secs = st.slider("Duration (s)", 1, 60, 5)
    if st.button("Capture"):
        with st.spinner("Capturing..."):
            pcap_file, summary = capture_packets(secs)
        st.success(f"PCAP saved: {pcap_file}")
        st.json(summary)

# -------------------------
# Reporting
# -------------------------
elif menu == "Reporting":
    st.header("Reporting")
    if st.button("Generate manifest (JSON)"):
        out = generate_json_summary()
        st.success(f"Generated: {out}")
    if st.button("Generate DOCX"):
        out = generate_docx_report()
        st.success(f"Generated: {out}")

# -------------------------
# Evidence
# -------------------------
elif menu == "Evidence":
    st.header("Evidence files")
    files = []
    for p in EVIDENCE_DIR.glob("**/*"):
        if p.is_file():
            files.append(str(p.relative_to(ROOT)))
    st.write(files)

# -------------------------
# Toolkit Logs
# -------------------------
elif menu == "Toolkit Logs":
    st.header("Toolkit logs (tail)")
    tail = read_log_tail()
    # if tail is dict/list convert to pretty JSON
    if isinstance(tail, (dict, list)):
        st.json(tail)
    else:
        st.code(str(tail))
