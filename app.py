import os
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/next")
def next_page():
    return render_template("verification.html")


@app.route("/voice-verification")
def voice_verification():
    return render_template("voice_verification.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "No file field named 'image'."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "No selected file."}), 400

    if not allowed_file(file.filename):
        return jsonify({"ok": False, "error": "File type not allowed."}), 400

    filename = secure_filename(file.filename)

    # avoid overwrite: add simple suffix if name exists
    name, ext = os.path.splitext(filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    counter = 1
    while os.path.exists(save_path):
        filename = f"{name}_{counter}{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        counter += 1

    file.save(save_path)
    return jsonify({"ok": True, "filename": filename})


@app.route("/admin")
def admin():
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if allowed_file(f):
            files.append(f)
    files.sort(reverse=True)
    return render_template("admin.html", files=files)

@app.route("/download/<path:filename>")
def download_file(filename):
    # force download (save to device/gallery)
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    # basic safe delete
    safe_name = secure_filename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)

    if not os.path.isfile(file_path):
        abort(404)

    os.remove(file_path)
    return redirect(url_for("admin"))

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)