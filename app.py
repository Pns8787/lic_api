from flask import Flask, request, jsonify, send_from_directory
import os, uuid
from anpr_engine import detect_and_read_plate

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to ANPR API"})

@app.route('/readnumberplate', methods=['POST'])
def read_plate():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"}), 400

    file = request.files['image']
    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        text, (cx, cy), plate_found = detect_and_read_plate(path)
        cx, cy = int(cx), int(cy)  # ✅ Fix: convert NumPy int to Python int

        return jsonify({
            "status": "success" if plate_found else "fail",
            "data": {
                "message": "ANPR successful" if plate_found else "Plate not found",
                "number_plate": text,
                "plate_Xcenter": cx,
                "plate_Ycenter": cy,
                "state": "Unknown",
                "view_image": f"/static/{filename}"
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/static/<filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
