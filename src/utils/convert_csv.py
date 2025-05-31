# RAGAPI\src\utils\convert_csv.py
import pandas as pd
import torch
import os

def csv_to_pt():
    print("Current directory:", os.getcwd())
    csv_path = 'embeddings.csv' 

    print("Looking for CSV at:", os.path.abspath(csv_path))

    if not os.path.exists(csv_path):
        print("CSV file not found!")
        exit()

    print("Loading CSV...")
    df = pd.read_csv(csv_path)
    print(f"CSV loaded! Shape: {df.shape}")

    print("Converting to tensor...")
    embeddings_tensor = torch.from_numpy(df.to_numpy()).to(torch.float)
    print(f"Tensor shape: {embeddings_tensor.shape}")

    print("Saving as PyTorch file...")
    torch.save(embeddings_tensor, 'embeddings.pt')
    print("embeddings.pt saved in:", os.path.abspath('embeddings.pt'))
    print("Done!")
