# NeuroStride - Gait Forensics System

A real-time gait analysis system that uses computer vision and machine learning to identify individuals based on their walking patterns.

## Architecture

- **Backend**: Flask API with MediaPipe pose detection and PyTorch neural network
- **Frontend**: Web interface with webcam/video upload capabilities
- **AI Model**: Convolutional LSTM network for gait pattern recognition

## Setup Instructions

### Prerequisites

1. Python 3.8+ installed
2. Webcam access for real-time analysis
3. Modern web browser with WebRTC support

### Installation

1. **Quick Setup (Windows)**
   ```bash
   # Install dependencies
   install.bat
   
   # Start the application
   start.bat
   ```

2. **Manual Setup**
   ```bash
   # Install backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   
   # Create models directory
   mkdir backend/models
   ```

3. **Start the Application**
   
   **Option A: Use the startup script (Windows)**
   ```bash
   start.bat
   ```
   
   **Option B: Manual startup**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py
   
   # Terminal 2 - Frontend  
   cd frontend
   python serve.py
   ```

4. **Test the Connection**
   ```bash
   python test_connection.py
   ```

5. **Access the Application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5000

## Usage

1. **Start Webcam**: Click "Start Webcam" to begin real-time capture
2. **Upload Video**: Use "Upload Video" to analyze pre-recorded footage
3. **Analyze Gait**: Click "Analyze Gait" to process the current frame
4. **View Results**: See match confidence, suspect ID, and behavioral metrics
5. **Save Report**: Generate PDF reports with analysis results

## API Endpoints

### POST /analyze_frame
Analyzes a single frame for gait patterns.

**Request:**
```json
{
  "image": "data:image/png;base64,...",
  "session_id": "optional_session_id",
  "force": false
}
```

**Response:**
```json
{
  "matched": true,
  "confidence": 0.85,
  "suspect_id": "SUS-1234",
  "suspicious_behaviors": ["Abrupt change in walking speed"]
}
```

## Model Training

The system includes a placeholder for model training. To train your own model:

1. Prepare gait sequence data
2. Run `python train_gait.py` 
3. The trained model will be saved to `models/gait_model.pth`

## Features

- Real-time pose detection using MediaPipe
- Gait pattern analysis with deep learning
- Suspect matching with confidence scores
- Behavioral anomaly detection
- PDF report generation
- Session-based frame buffering
- Cross-origin resource sharing (CORS) enabled

## Technical Details

- **Pose Detection**: 33 body landmarks extracted per frame
- **Sequence Length**: 48 frames for temporal analysis
- **Model Architecture**: Conv1D + Bidirectional LSTM + FC layers
- **Embedding Dimension**: 256-dimensional feature vectors
- **Similarity Search**: FAISS index for fast nearest neighbor lookup

## Troubleshooting

**Backend Issues:**
- Ensure all Python dependencies are installed
- Check that port 5000 is available
- Verify camera permissions if using webcam

**Frontend Issues:**
- Enable camera permissions in browser
- Check browser console for CORS errors
- Ensure backend is running before frontend requests

**Model Issues:**
- Train the model first using `train_gait.py`
- Check that model files exist in `models/` directory
- Verify CUDA availability if using GPU acceleration