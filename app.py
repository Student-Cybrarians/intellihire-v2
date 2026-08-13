from flask import Flask, jsonify, request, render_template
from pathlib import Path
from ml_engine import rank_candidates, analyze_resume, demo_candidates

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({"status":"ok","engine":"IntelliHire ML Engine","version":"1.0"})

@app.get("/api/candidates")
def candidates():
    return jsonify(demo_candidates())

@app.post("/api/rank")
def rank():
    payload = request.get_json(silent=True) or {}
    job = payload.get("job", "")
    candidates = payload.get("candidates") or demo_candidates()
    return jsonify({"results": rank_candidates(job, candidates)})

@app.post("/api/analyze-resume")
def resume():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    return jsonify(analyze_resume(text))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
