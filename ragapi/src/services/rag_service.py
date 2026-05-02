from openai import OpenAIError, AsyncOpenAI
import os
import time
from dotenv import load_dotenv
import asyncio
from src.utils.PDF_to_chunks import get_chunks
from src.services.vector_db import VectorDB

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
load_dotenv()

openai_client = AsyncOpenAI(api_key=os.getenv('llm_api'), base_url="https://api.deepseek.com")
vector_db = VectorDB()


class RAG:
    def __init__(self):
        self.client = openai_client
        self.vector_db = vector_db

    async def get_context(self, user_input):
        return await self.vector_db.query(user_input)

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
                temperature=1.3
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
        query = self.format_query(chathistory, question, context)
        t2 = time.time()
        response = await self.get_response(query)
        t3 = time.time()
        print(f"Context time: {t1 - t0:.2f}s")
        print(f"Formatting time: {t2 - t1:.2f}s")
        print(f"LLM time: {t3 - t2:.2f}s")
        return response


async def main():
    #Store chunks in vector DB
    path = os.getenv('pdf_path')
    chunks = get_chunks(path)
    await asyncio.get_event_loop().run_in_executor(None, vector_db.ingest, chunks)


if __name__ == "__main__":
    asyncio.run(main())
