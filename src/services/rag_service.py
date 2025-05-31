from openai import OpenAI, OpenAIError
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from src.utils.context_retriever import get_context
import torch
import time
from sentence_transformers import SentenceTransformer
import csv
class RAG:
    def __init__(self):
        
        self.client = OpenAI(api_key=os.getenv('llm_api'), base_url="https://api.deepseek.com")
        self.embeddings = torch.load('embeddings.pt', map_location='cpu', weights_only=True)
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        with open("chunks.csv", encoding="utf-8", errors="replace") as fp:
            reader = csv.reader(fp, delimiter=",", quotechar='"')
            self.texts = [txtchunk for txtchunk in reader]

    async def get_context(self, question):
        return get_context(question, self.embeddings, self.model, self.texts)
    
   
    async def format_query(self, question, context):
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
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": query}]
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
        query = await self.format_query(question, context)
        t2 = time.time()
        response = await self.get_response(query)
        t3 = time.time()
        print(f"Context time: {t1 - t0:.2f}s")
        print(f"Formatting time: {t2 - t1:.2f}s")
        print(f"LLM time: {t3 - t2:.2f}s")
        return response
        
       

if __name__ == "__main__":
    rag = RAG()
    user_question = "Was ist eine Risikoanalyse?"
   
    output= rag.get_response(user_question)
    print(output)

