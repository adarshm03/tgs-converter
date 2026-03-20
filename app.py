import os, sys, subprocess, threading, webbrowser
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

PYTHON    = sys.executable
LOTTIE    = os.path.join(os.path.dirname(PYTHON), "Scripts", "lottie_convert.py")
CAIRO_BIN = r"C:\msys64\ucrt64\bin"

progress_data = {"total": 0, "done": 0, "log": [], "running": False, "finished": False, "stopped": False}
stop_flag = threading.Event()

def make_env():
    env = os.environ.copy()
    env["PATH"] = CAIRO_BIN + os.pathsep + env.get("PATH", "")
    return env

def convert_worker(files, output_folder):
    global progress_data
    stop_flag.clear()
    progress_data = {"total": len(files), "done": 0, "log": [], "running": True, "finished": False, "stopped": False}
    env = make_env()
    os.makedirs(output_folder, exist_ok=True)

    for f in files:
        if stop_flag.is_set():
            progress_data["running"]  = False
            progress_data["finished"] = True
            progress_data["stopped"]  = True
            return

        name   = os.path.basename(f)
        out    = os.path.join(output_folder, name.replace(".tgs", ".gif"))
        result = subprocess.run([PYTHON, LOTTIE, f, out], env=env, capture_output=True, text=True)
        ok     = result.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0
        progress_data["done"] += 1
        progress_data["log"].append({
            "name": name,
            "ok":   ok,
            "msg":  "" if ok else (result.stderr.strip().splitlines() or ["unknown error"])[-1]
        })

    progress_data["running"]  = False
    progress_data["finished"] = True

def _run_picker(script: str):
    """Run a PowerShell picker script, returning stripped stdout."""
    # Wrap in a hidden helper window so the dialog always appears on top
    wrapper = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "Add-Type -AssemblyName Microsoft.VisualBasic;"
        # Create an invisible owner form so the dialog gets focus
        "$owner = New-Object System.Windows.Forms.Form;"
        "$owner.TopMost = $true;"
        "$owner.StartPosition = 'Manual';"
        "$owner.Location = New-Object System.Drawing.Point(0,0);"
        "$owner.Size = New-Object System.Drawing.Size(1,1);"
        "$owner.Show();"
        "$owner.Hide();"
        + script.replace("ShowDialog()", "ShowDialog($owner)")
        + " $owner.Dispose();"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", wrapper],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def powershell_pick_folder(title="Select Folder"):
    """Use modern Windows folder picker via PowerShell (always on top)."""
    script = (
        "[System.Windows.Forms.Application]::EnableVisualStyles();"
        "$d = New-Object System.Windows.Forms.FolderBrowserDialog;"
        f"$d.Description = '{title}';"
        "$d.UseDescriptionForTitle = $true;"
        "$d.ShowNewFolderButton = $true;"
        "if($d.ShowDialog() -eq 'OK'){$d.SelectedPath}else{''}"
    )
    return _run_picker(script)

def powershell_pick_files():
    """Use modern Windows multi-file picker via PowerShell (always on top)."""
    script = (
        "[System.Windows.Forms.Application]::EnableVisualStyles();"
        "$d = New-Object System.Windows.Forms.OpenFileDialog;"
        "$d.Title = 'Select TGS Sticker Files';"
        "$d.Filter = 'Telegram Stickers (*.tgs)|*.tgs|All Files (*.*)|*.*';"
        "$d.Multiselect = $true;"
        "if($d.ShowDialog() -eq 'OK'){$d.FileNames -join [char]10}else{''}"
    )
    raw = _run_picker(script)
    if not raw:
        return []
    return [f.strip() for f in raw.splitlines() if f.strip()]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/browse-folder", methods=["POST"])
def browse_folder():
    title = request.json.get("title", "Select Folder")
    path = powershell_pick_folder(title)
    return jsonify({"path": path})

@app.route("/browse-output", methods=["POST"])
def browse_output():
    path = powershell_pick_folder("Select Output Folder")
    return jsonify({"path": path})

@app.route("/browse-files", methods=["POST"])
def browse_files():
    files = powershell_pick_files()
    return jsonify({"files": files})

@app.route("/convert", methods=["POST"])
def convert():
    global progress_data
    if progress_data["running"]:
        return jsonify({"error": "Already running"}), 400
    data   = request.json
    files  = data.get("files", [])
    outdir = data.get("output", "").strip()
    if not files or not outdir:
        return jsonify({"error": "Missing files or output folder"}), 400
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        return jsonify({"error": f"File not found: {missing[0]}"}), 400
    threading.Thread(target=convert_worker, args=(sorted(files), outdir), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/stop", methods=["POST"])
def stop():
    stop_flag.set()
    return jsonify({"ok": True})

@app.route("/progress")
def progress():
    return jsonify(progress_data)

@app.route("/open-folder", methods=["POST"])
def open_folder():
    folder = request.json.get("folder", "")
    if os.path.isdir(folder):
        os.startfile(folder)
    return jsonify({"ok": True})

@app.route("/scan-folder", methods=["POST"])
def scan_folder():
    folder = request.json.get("folder", "").strip()
    if not os.path.isdir(folder):
        return jsonify({"files": [], "error": "Folder not found"})
    files = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".tgs")
    ])
    return jsonify({"files": files, "count": len(files)})

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=False, port=5000)