from PDF_to_chunks import get_chunks
import requests
import pandas as pd
import csv
from dotenv import load_dotenv
import os

#text to embedding converter
def get_embedding(texts):#old api url
     load_dotenv()
     
     hf_token = os.getenv('hf_token')
     model_id = os.getenv('model_id')

     api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
     headers = {"Authorization": f"Bearer {hf_token}"}

     response = requests.post(api_url, headers=headers, json={"inputs": texts, "options":{"wait_for_model":True}})

     return response.json()



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
        

 
