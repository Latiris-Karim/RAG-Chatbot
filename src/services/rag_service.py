from openai import OpenAI, OpenAIError
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from src.utils.context_retriever import get_context
import torch
from datasets import load_dataset


class RAG:
    def __init__(self):
        
        self.client = OpenAI(api_key=os.getenv('llm_api'), base_url="https://api.deepseek.com")
    
       
        rag_embeddings = load_dataset('fox133/testing123')
        self.embeddings = torch.from_numpy(rag_embeddings["train"]
                                           .to_pandas()
                                           .to_numpy()).to(torch.float)

    async def get_context(self, question):
        return get_context(question, self.embeddings)
    
   
    
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
        context = await self.get_context(question)
        query = await self.format_query(question, context)
        return await self.get_response(query)
       

if __name__ == "__main__":
    rag = RAG()
    user_question = "Was ist eine Risikoanalyse?"
   
    output= rag.get_response(user_question)
    print(output)

