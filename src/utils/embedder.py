from .PDF_to_chunks import get_chunks
import pandas as pd
import csv
from sentence_transformers import SentenceTransformer

def get_embedding(texts, model: SentenceTransformer):
     embeddings = model.encode(texts)
     return embeddings


if __name__ == "__main__":
    path = r"C:\Users\einma\Desktop\Projects\RAGAPI\resources"
    chunks = get_chunks(path)
    print(len(chunks))
    embeddings = get_embedding(chunks)
    print(len(embeddings))

    embedding = pd.DataFrame(embeddings)
    #index=False prevents exporting row indices to csv file
    embedding.to_csv("embeddings.csv", index=False)

    with open('chunks.csv', 'w') as f:
        write = csv.writer(f)
        write.writerow(chunks)
        

