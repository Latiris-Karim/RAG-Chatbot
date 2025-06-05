from openai import OpenAIError, AsyncOpenAI
import os
import torch
import time
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search
from dotenv import load_dotenv
import asyncio
import csv
from src.utils.PDF_to_chunks import get_chunks
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
load_dotenv()

#imports these reuseable variables just once on module import, instead of on every rag object creation, saves roughly 2 seconds respone time and that on a small dataset
embeddings = torch.load('embeddings.pt', map_location='cpu', weights_only=True)
sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
openai_client = AsyncOpenAI(api_key=os.getenv('llm_api'), base_url="https://api.deepseek.com")

with open("chunks.csv", encoding="utf-8", errors="replace") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            texts = [txtchunk for txtchunk in reader]
class RAG:
    def __init__(self):
        
        self.client = openai_client
        self.embeddings = embeddings
        self.model: SentenceTransformer = sentence_model
        self.texts = texts
        
        
    async def get_embedding(self, texts):
        embeddings = await asyncio.get_event_loop().run_in_executor(
            None, self.model.encode, texts
        )
        return embeddings
    

    async def get_context(self, user_input):
        output = await self.get_embedding(user_input)
        query_embeddings = torch.FloatTensor(output)  
    
        hits = await asyncio.get_event_loop().run_in_executor(
            None, semantic_search, query_embeddings, self.embeddings, 2
        )
        
        # Retrieve and return the matching context chunks
        context = [self.texts[0][hits[0][i]['corpus_id']] for i in range(len(hits[0]))]
        return context
   

    def format_query(self, question, context):
        context_str = " ".join(context)
        return f"""
        The following is relevant context extracted from a document:
        {context_str}

        Question: {question}

        Respond in exactly two parts:
        1. Your answer to the question based on the context.
        2. On a new line, only the filename of the most relevant PDF, without any labels or additional text.

        Do not include any labels like "Answer:" or "Filename:". Just provide the two parts as described above.
        """


    async def get_response(self, query):
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": query}],
                temperature=0.0
            )
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                return "Error: No response from API."
        except OpenAIError as e:  
            return f"OpenAI API Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"
    

    async def pipeline(self, question):
        t0 = time.time()
        context = await self.get_context(question)
        t1 = time.time()
        query = self.format_query(question, context)
        t2 = time.time()
        response = await self.get_response(query)
        t3 = time.time()
        print(f"Context time: {t1 - t0:.2f}s")
        print(f"Formatting time: {t2 - t1:.2f}s")
        print(f"LLM time: {t3 - t2:.2f}s")
        return response
        
       

if __name__ == "__main__":
    rag = RAG()
    path = "..."
    chunks = get_chunks(path)
    embeddings = rag.get_embedding(chunks)
    
    # export embeddings to CSV
    embedding = pd.DataFrame(embeddings)
    embedding.to_csv("embeddings.csv", index=False)
    
