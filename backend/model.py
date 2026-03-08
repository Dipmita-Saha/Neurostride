# backend/model.py
import os
import numpy as np
import torch
import faiss

# Example small network skeleton — when training, your saved model must match this class
import torch.nn as nn
import torch.nn.functional as F

class GaitNet(nn.Module):
    def __init__(self, seq_len=48, feat_dim=34, emb_dim=256):
        super().__init__()
        self.conv1 = nn.Conv1d(feat_dim, 128, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(128, 256, kernel_size=3, padding=1)
        self.lstm = nn.LSTM(256, 128, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(nn.Linear(256, 512), nn.ReLU(), nn.Linear(512, emb_dim))

    def forward(self, x):
        # x: (B, T, F)
        x = x.transpose(1,2)           # (B, F, T)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.transpose(1,2)          # (B, T, C)
        out, _ = self.lstm(x)
        out = out.mean(dim=1)
        emb = self.fc(out)
        emb = F.normalize(emb, dim=1)
        return emb

class GaitModel:
    def __init__(self, model_path="models/gait_model.pth", device='cpu'):
        self.device = device
        self.model_path = model_path
        self.model = GaitNet().to(device)
        if os.path.exists(model_path):
            ckpt = torch.load(model_path, map_location=device)
            self.model.load_state_dict(ckpt['model_state'])
            print("Loaded model:", model_path)
        else:
            print("Model not found, running with untrained weights. Train and save to", model_path)

        # FAISS index: for demo we create an empty index; populate after training with known embeddings
        self.index = None
        self.id_to_label = {}  # map index id -> suspect id
        self._load_faiss_index_if_exists()

    def _load_faiss_index_if_exists(self):
        # if you have a saved faiss index file, load it here (optional)
        idx_path = "models/faiss.index"
        mapping_path = "models/faiss_map.npy"
        if os.path.exists(idx_path) and os.path.exists(mapping_path):
            self.index = faiss.read_index(idx_path)
            self.id_to_label = np.load(mapping_path, allow_pickle=True).item()
            print("Loaded FAISS index.")
        else:
            print("No FAISS index found - create and save after building DB.")

    def infer_embedding(self, seq):
        """
        seq: np.array (T, F)
        returns normalized embedding (D,)
        """
        self.model.eval()
        with torch.no_grad():
            x = torch.tensor(seq[None].astype(np.float32)).to(self.device)  # (1, T, F)
            emb = self.model(x).cpu().numpy()[0]
        return emb

    def match_embedding(self, emb, topk=1):
        if self.index is None:
            return {"matched": False, "confidence": 0.0, "suspect_id": None}
        # faiss uses L2; if we use normalized embeddings, inner product = cosine similarity if using index for dot product
        D, I = self.index.search(emb.astype('float32').reshape(1, -1), topk)
        # D contains distances; for inner product index, D is -similarity; interpret accordingly
        # For simplicity assume index stores L2 distances: lower is better
        best_idx = int(I[0,0])
        dist = float(D[0,0])
        # convert distance to pseudo confidence (this is domain-specific — calibrate on val data)
        confidence = max(0.0, 1.0 - dist)  # demo only
        suspect_id = self.id_to_label.get(best_idx, None)
        return {"matched": True if suspect_id else False, "confidence": float(confidence), "suspect_id": suspect_id}

    def infer_and_match(self, seq):
        # seq shape: (T, F)
        emb = self.infer_embedding(seq)
        match = self.match_embedding(emb, topk=1)
        # suspicious behaviors can be added by a separate detector (e.g., sudden speed change). For demo, mock.
        suspicious_behaviors = []
        # detect quick horizontal displacement as "sprint" example (very naive)
        # seq is (T, F) -> we used x,y pairs: so len(F)=2*K
        try:
            coords = seq.reshape(seq.shape[0], -1, 2)  # (T, K, 2)
            pelvis = coords[:, 0, :]  # if pelvis is keypoint 0; adapt as needed
            displacements = np.linalg.norm(np.diff(pelvis, axis=0), axis=1)
            if np.mean(displacements) > 0.03:
                suspicious_behaviors.append("Abrupt change in walking speed")
        except Exception:
            pass

        return {
            "matched": match["matched"],
            "confidence": float(match["confidence"]),
            "suspect_id": match["suspect_id"],
            "suspicious_behaviors": suspicious_behaviors
        }
