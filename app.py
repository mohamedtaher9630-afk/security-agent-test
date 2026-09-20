import os
import subprocess
import ipaddress
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part", 400
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return "No selected file", 400
    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(UPLOAD_FOLDER, filename))
        return "File uploaded successfully!"
    return "Invalid file type", 400

@app.route("/ping", methods=["GET"])
def ping_host():
    ip_address = request.args.get("ip")
    if not ip_address:
        return "Missing IP parameter", 400
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return "Invalid IP address", 400
    subprocess.run(["ping", "-c", "1", ip_address], check=True)
    return "Ping completed!"

if __name__ == "__main__":
    app.run(debug=False)
