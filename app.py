import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, abort
from dotenv import load_dotenv


from analysis import run_scan


load_dotenv()


app = Flask(__name__)


# In‑memory store: { scan_id: {repo, files, issues} }
SCANS = {}


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/scan")
def scan():
    repo_url = request.form.get("repo_url", "").strip()
    if not repo_url.startswith("http") or "github.com" not in repo_url:
        return render_template("index.html", error="Please enter a valid public GitHub URL."), 400


    scan_id = str(uuid.uuid4())
    try:
        result = run_scan(repo_url)
        SCANS[scan_id] = result
        return redirect(url_for("issues", scan_id=scan_id))
    except Exception as e:
        return render_template("index.html", error=f"Scan failed: {e}"), 500


@app.get("/issues/<scan_id>")
def issues(scan_id: str):
    scan = SCANS.get(scan_id)
    if not scan:
        abort(404)
    return render_template("issues.html", scan_id=scan_id, scan=scan)


@app.get("/issues/<scan_id>/<issue_id>")
def issue_detail(scan_id: str, issue_id: str):
    scan = SCANS.get(scan_id)
    if not scan:
        abort(404)
    issue = next((i for i in scan["issues"] if i["id"] == issue_id), None)
    if not issue:
        abort(404)
    file = next((f for f in scan["files"] if f["path"] == issue["filePath"]), None)
    if not file:
        abort(404)
    return render_template("issue_detail.html", scan=scan, issue=issue, file=file)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_ENV") == "development")