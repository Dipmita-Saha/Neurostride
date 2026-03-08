"""
train_gait.py — Training script for NeuroStride gait recognition
---------------------------------------------------------------
1. Extracts gait features from labeled videos (one folder per person ID)
2. Uses MediaPipe Pose to get skeleton keypoints
3. Converts keypoints into gait features (angles, distances, stride metrics)
4. Trains an ML model (RandomForest)
5. Saves the trained model for backend inference
"""

import os
import cv2
import numpy as np
import mediapipe as mp
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Paths
DATASET_DIR = "dataset_gait"  # e.g., dataset_gait/person1/*.mp4
MODEL_PATH = "gait_model.pkl"

# MediaPipe Pose setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

def extract_pose_features_from_video(video_path):
    """Extract gait features from a video file using MediaPipe Pose."""
    cap = cv2.VideoCapture(video_path)
    features = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            # Example: extract normalized distances & angles
            hip_left = np.array([lm[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                 lm[mp_pose.PoseLandmark.LEFT_HIP.value].y])
            hip_right = np.array([lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                  lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y])
            ankle_left = np.array([lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                   lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].y])
            ankle_right = np.array([lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                    lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y])

            hip_distance = np.linalg.norm(hip_left - hip_right)
            step_length = np.linalg.norm(ankle_left - ankle_right)

            features.append([hip_distance, step_length])

    cap.release()

    if len(features) == 0:
        return None

    # Average features over the video
    return np.mean(features, axis=0)

def load_dataset():
    """Loads dataset from folder structure: dataset_gait/person_id/*.mp4"""
    X, y = [], []
    for person_id in os.listdir(DATASET_DIR):
        person_folder = os.path.join(DATASET_DIR, person_id)
        if not os.path.isdir(person_folder):
            continue
        for file in os.listdir(person_folder):
            if file.lower().endswith((".mp4", ".avi", ".mov")):
                path = os.path.join(person_folder, file)
                feats = extract_pose_features_from_video(path)
                if feats is not None:
                    X.append(feats)
                    y.append(person_id)
    return np.array(X), np.array(y)

if __name__ == "__main__":
    print("[INFO] Loading dataset...")
    X, y = load_dataset()
    print(f"[INFO] Loaded {len(X)} samples from {len(set(y))} people.")

    if len(X) == 0:
        print("[ERROR] No data found. Make sure dataset_gait/ is populated.")
        exit()

    print("[INFO] Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("[INFO] Training model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    print("[INFO] Evaluating model...")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))

    print(f"[INFO] Saving model to {MODEL_PATH}...")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    print("[INFO] Done.")
