import os
from flask import Flask, request

app = Flask(__name__)

# ثغرة 1: Unrestricted File Upload - قبول رفع أي ملف دون الفحص أو التحقق من الامتداد
@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    # حفظ الملف مباشرة في المجلد العام بدون تنظيف اسم الملف أو فحص امتداده
    uploaded_file.save(os.path.join("./uploads", uploaded_file.filename))
    return "File uploaded successfully!"

# ثغرة 2: Command Injection - تنفيذ أوامر النظام مباشرة باستخدام مدخلات المستخدم
@app.route("/ping", methods=["GET"])
def ping_host():
    ip_address = request.args.get("ip")
    # دمج مدخلات المستخدم مباشرة داخل أمر النظام يتيح للمخترق تنفيذ أي أمر عبر os.system
    command = f"ping -c 1 {ip_address}"
    os.system(command)
    return "Ping completed!"

if __name__ == "__main__":
    app.run(debug=True)
