import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

class PhishingSentinelModel(nn.Module):
    def __init__(self, input_size):
        super(PhishingSentinelModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.network(x)

def train_model(csv_path="Dataset.csv"):
    if not os.path.exists(csv_path):
        # Check in datasets subfolder if not in root
        csv_path = os.path.join("datasets", "Dataset.csv")
        if not os.path.exists(csv_path):
            print(f"Error: {csv_path} not found.")
            return

    print(f"[Sentinel] Loading Dataset: {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Ensure column order: Drop 'Type' and use the rest as features
    # This matches the extract_features order in preprocess.py
    X = df.drop('Type', axis=1).values
    y = df['Type'].values.reshape(-1, 1)
    
    print(f"[Sentinel] Features: {X.shape[1]}, Instances: {len(X)}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model_dir = "models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    # Save Scaler
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    train_data = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    test_data = TensorDataset(torch.FloatTensor(X_test), torch.FloatTensor(y_test))
    
    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

    model = PhishingSentinelModel(input_size=X.shape[1])
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print(f"[Sentinel] Starting Training...")
    for epoch in range(30):
        model.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
        if (epoch + 1) % 5 == 0:
            model.eval()
            with torch.no_grad():
                correct = 0
                total = 0
                for tx, ty in test_loader:
                    t_out = model(tx)
                    predicted = (t_out > 0.5).float()
                    total += ty.size(0)
                    correct += (predicted == ty).sum().item()
                print(f"Epoch [{epoch+1}/30], Accuracy: {100 * correct / total:.2f}%")
            
    torch.save(model.state_dict(), os.path.join(model_dir, "sentinel_v1.pth"))
    print(f"[Sentinel] Model training complete.")

if __name__ == "__main__":
    train_model()