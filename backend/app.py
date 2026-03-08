# backend/app.py
import os, io, time, base64, random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000"])

# Mock model for demonstration (replace with real model when MediaPipe is available)
class MockGaitModel:
    def __init__(self):
        self.model_loaded = True
    
    def infer_and_match(self, seq):
        # Simulate processing time
        time.sleep(0.5)
        
        # Generate realistic mock results
        matched = random.random() > 0.4
        confidence = random.uniform(0.5, 0.95) if matched else random.uniform(0.1, 0.4)
        suspect_id = f"SUS-{random.randint(1000, 9999)}" if matched else None
        
        behaviors = []
        if random.random() > 0.7:
            behaviors.append("Abrupt change in walking speed")
        if random.random() > 0.8:
            behaviors.append("Irregular gait pattern detected")
            
        return {
            "matched": matched,
            "confidence": confidence,
            "suspect_id": suspect_id,
            "suspicious_behaviors": behaviors
        }

# Create mock model instance
gait_model = MockGaitModel()

# In-memory buffers keyed by session id -> list of frames
SEQ_LEN = 48
buffers = {}

@app.route("/")
def index():
    # serve frontend index.html
    return app.send_static_file('index.html')

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "demo_mode": True,
        "timestamp": time.time()
    })

@app.route("/analyze_frame", methods=["POST"])
def analyze_frame_route():
    # Expect JSON { "image": "data:image/png;base64,..." , "session_id": "optional id" }
    data = request.get_json(force=True)
    img_b64 = data.get("image", "")
    session_id = data.get("session_id", "default_session")
    force = data.get("force", False)

    if not img_b64:
        return jsonify({"error": "no image provided"}), 400

    try:
        # Decode and validate image
        if "," in img_b64:
            _, img_b64 = img_b64.split(",", 1)
        img_bytes = base64.b64decode(img_b64)
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        # Simple image analysis (mock pose detection)
        img_array = np.array(pil_img)
        
        # Check if image has enough variation (simple movement detection)
        if img_array.std() < 10:  # Very low variation = likely static
            return jsonify({
                "matched": False, 
                "confidence": 0.0, 
                "suspect_id": None, 
                "suspicious_behaviors": [], 
                "note": "no_movement"
            }), 200

        # Add to buffer (mock keypoints)
        buf = buffers.setdefault(session_id, [])
        mock_keypoints = np.random.rand(66).astype(np.float32)  # 33 landmarks * 2 coords
        buf.append(mock_keypoints)
        
        if len(buf) > SEQ_LEN:
            buf.pop(0)

        # Run analysis if we have enough frames or forced
        if len(buf) >= SEQ_LEN or force:
            # Mock sequence for analysis
            seq = np.stack(buf[-SEQ_LEN:], axis=0) if len(buf) >= SEQ_LEN else np.stack(buf, axis=0)
            result = gait_model.infer_and_match(seq)
            return jsonify(result)
        else:
            return jsonify({"status": "buffering", "have": len(buf), "need": SEQ_LEN})
            
    except Exception as e:
        return jsonify({"error": f"Image processing failed: {str(e)}"}), 400

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
