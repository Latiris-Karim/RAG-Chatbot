import os
import shutil
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from openai import OpenAI, OpenAIError
from chonkie import RecursiveChunker
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from markitdown import MarkItDown
load_dotenv()

openai_client = OpenAI(api_key=os.getenv('llm_api'), base_url="https://api.deepseek.com")
rec_chunker = RecursiveChunker.from_recipe("markdown", tokenizer="gpt2", chunk_size=300)
md = MarkItDown()

class ContextualChunker:
    def __init__(self, file_path, user_interface):
        self.file_path = file_path
        self.user_interface = user_interface

    def chunk(self) -> list[tuple[str, str, str]]:
        ingested_dir = os.path.join(self.file_path, "ingested")
        os.makedirs(ingested_dir, exist_ok=True)

        chunks = []
        for file in os.listdir(self.file_path):
            full_path = os.path.join(self.file_path, file)
            if not os.path.isfile(full_path):
                continue
            if file.endswith('.md'):
                text = open(full_path, encoding='utf-8').read()
            else:
                text = md.convert(full_path).markdown
            res = rec_chunker.chunk(text)
            contexualsummary = self._summary_for_chunk(text, res)
            chunks.extend((file, contexualsummary[chunk], res[chunk].text) for chunk in range(len(res)))
            shutil.move(full_path, os.path.join(ingested_dir, file))
        return chunks
    
    def _summary_for_chunk(self, document, chunks):
        prompt = f"Summarize the main purpose of the chunk based on the document content. The summary should be a short sentence that explains the role this chunk plays in the overall document. Document: {document}\n\n"

        with ThreadPoolExecutor(max_workers=10) as executor:
            summaries = list(executor.map(
                lambda chunk: self.user_interface.simple_query(prompt + f"Chunk: {chunk.text}"),
                chunks
            ))

        return summaries

class LLMInterface:
    def simple_query(self, query):
        try:
            response = openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": query}],
                temperature=0.2,
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return "Sorry, I couldn't process your request at the moment."
