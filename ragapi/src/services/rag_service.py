from openai import OpenAIError, AsyncOpenAI
import os
import torch
import time
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search
from dotenv import load_dotenv
import asyncio
from src.utils.PDF_to_chunks import get_chunks
import pickle
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
load_dotenv()


sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
openai_client = AsyncOpenAI(api_key=os.getenv('llm_api'), base_url="https://api.deepseek.com")

if os.path.exists('embeddings.pt') and os.path.exists('chunks.pkl'):
    embeddings = torch.load('embeddings.pt', map_location='cpu', weights_only=True)

    with open('chunks.pkl', 'rb') as f:
        texts = pickle.load(f)
else:
    embeddings = None
    texts = None
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
        context = [self.texts[hits[0][i]['corpus_id']] for i in range(len(hits[0]))]
        return context
   

    def format_query(self, chathistory, question, context):

        context_str = " ".join(context)
        chat_section = f"\nChat history:\n{chathistory}" if chathistory else ""

        return f"""You are an expert assistant. Use the following context and chat history to answer the user's latest question.

        Context from documents:
        {context_str}

        {chat_section}

        User's latest question:
        {question}

        Answer the question based strictly on the context above.
        Do not include labels like "Answer:" or filenames. Respond with only the answer content.
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
    

    async def pipeline(self, chathistory, question):
        t0 = time.time()
        context = await self.get_context(question)
        t1 = time.time()
        query = self.format_query(chathistory,question, context)
        t2 = time.time()
        response = await self.get_response(query)
        t3 = time.time()
        print(f"Context time: {t1 - t0:.2f}s")
        print(f"Formatting time: {t2 - t1:.2f}s")
        print(f"LLM time: {t3 - t2:.2f}s")
        return response
        
       

async def main():
    rag = RAG()
    path = r""
    chunks = get_chunks(path)
    embeddings = await rag.get_embedding(chunks) 
    
    embeddings_tensor = torch.from_numpy(embeddings).to(torch.float)
    torch.save(embeddings_tensor, 'embeddings.pt')

    with open('chunks.pkl', 'wb') as f:
        pickle.dump(chunks, f)

if __name__ == "__main__":
    asyncio.run(main())
