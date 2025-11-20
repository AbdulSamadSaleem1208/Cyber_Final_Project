# streamlit_app.py -- place this at project root (next to the src/ folder)
import sys
from pathlib import Path
import importlib
import traceback

# Ensure src/ is importable
ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Try to import modules from src/ but fail gracefully
def safe_import(module_name):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        # don't crash; return a dummy module
        class _M: pass
        m = _M()
        m.__error__ = e
        return m

scanner = safe_import("scanner")
auth_test = safe_import("auth_test")
stress_mod = safe_import("stress")
footprint = safe_import("footprint")
pcap_mod = safe_import("pcap")
reporting = safe_import("reporting")
logger_mod = safe_import("logger")

# Map expected function names to whatever exists in modules (fallbacks)
def get_callable(mod, *names, fallback=None):
    for n in names:
        if hasattr(mod, n):
            return getattr(mod, n)
    return fallback

# scanner
run_scan = get_callable(scanner, "run_scan", "sync_port_scan", fallback=lambda *a, **k: {"error":"scanner module missing"})
sync_port_scan = get_callable(scanner, "sync_port_scan", fallback=run_scan)

# auth functions: your repo has both policy_check/offline_hash_check and check_password_strength/simulate_hash_check variants
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
generate_json_summary = get_callable(reporting, "generate_json_summary", "generate_manifest", fallback=lambda: {"error":"reporting missing"})
generate_docx_report = get_callable(reporting, "generate_docx_report", fallback=lambda: {"error":"reporting missing"})

# logger tail
read_log_tail = get_callable(logger_mod, "read_log_tail", "tail_logs",
                             fallback=lambda n=200: "No logs available (logger module missing)")

# Streamlit UI
import streamlit as st
import os, json, time

st.set_page_config(page_title="PayBuddy Toolkit", layout="wide")
st.title("PayBuddy Hybrid Toolkit — PayBuddy QA Labs")
st.caption("Offline + Safe security testing (lab-only). Check terminal for backend errors.")

# quick developer diagnostics
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

# Sidebar to choose module
menu = st.sidebar.selectbox("Module", [
    "Dashboard", "Port Scanner", "Password Assessment", "Stress Tester",
    "Footprint", "Packet Capture", "Reporting", "Evidence", "Toolkit Logs"
])

EVIDENCE_DIR = str(ROOT / "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)
OUTPUT_DIR = os.path.join(EVIDENCE_DIR, "outputs"); os.makedirs(OUTPUT_DIR, exist_ok=True)
PCAP_DIR = os.path.join(EVIDENCE_DIR, "pcaps"); os.makedirs(PCAP_DIR, exist_ok=True)
SS_DIR = os.path.join(EVIDENCE_DIR, "screenshots"); os.makedirs(SS_DIR, exist_ok=True)

if menu == "Dashboard":
    st.header("Toolkit Overview")
    st.write("""
    Features (if corresponding backend modules are available):
    - Port scanner (run_scan / sync_port_scan)
    - Password assessment (check_password_strength / policy_check)
    - Stress tester (run_stress_test / stress_test)
    - Footprint (check_paths / probe_subdomains)
    - Packet capture (capture_scapy / pyshark)
    - Reporting (generate_json_summary / generate_docx_report)
    """)
    st.info("If a module is missing you will see a warning in Diagnostics above.")
    st.success("UI loaded — click modules in the sidebar.")

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
            out = os.path.join(OUTPUT_DIR, f"scan_{int(time.time())}_{target.replace(':','_')}.json")
            with open(out, "w") as f:
                json.dump(res, f, indent=2)
            st.success(f"Saved result to {out}")

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
        outpath = os.path.join(OUTPUT_DIR, f"hashsim_{int(time.time())}.json")
        with open(outpath, "w") as fp:
            json.dump(out, fp, indent=2)
        st.success(f"Saved to {outpath}")

elif menu == "Stress Tester":
    st.header("Stress Tester (lab only)")
    url = st.text_input("Target URL", "http://127.0.0.1:8000")
    clients = st.number_input("Clients", 1, 200, 20)
    duration = st.number_input("Duration (s)", 1, 30, 5)
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

elif menu == "Packet Capture":
    st.header("Packet capture")
    secs = st.slider("Duration (s)", 1, 20, 5)
    if st.button("Capture"):
        with st.spinner("Capturing..."):
            pcap_file, summary = capture_packets(secs)
        st.success(f"PCAP saved: {pcap_file}")
        st.json(summary)

elif menu == "Reporting":
    st.header("Reporting")
    if st.button("Generate manifest (JSON)"):
        out = generate_json_summary()
        st.success(f"Generated: {out}")
    if st.button("Generate DOCX"):
        out = generate_docx_report()
        st.success(f"Generated: {out}")

elif menu == "Evidence":
    st.header("Evidence files")
    files = []
    for p in Path(EVIDENCE_DIR).glob("**/*"):
        if p.is_file():
            files.append(str(p.relative_to(ROOT)))
    st.write(files)

elif menu == "Toolkit Logs":
    st.header("Toolkit logs (tail)")
    tail = read_log_tail()
    st.code(tail)
