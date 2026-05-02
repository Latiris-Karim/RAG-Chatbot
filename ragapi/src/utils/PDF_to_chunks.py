from pypdf import PdfReader
from transformers import AutoTokenizer
import os
import re

def split_into_sentences(text):
    return re.findall(r'[^.!?\n]+[.!?\n]', text)

def get_chunks(docs_folder, max_tokens=192, overlap_tokens=50) -> list[tuple[str, str]]:
    all_chunks = []
    files = [f for f in os.listdir(docs_folder) if os.path.isfile(os.path.join(docs_folder, f))]
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    for file in files:
        filename = os.path.splitext(file)[0]
        pdf_path = os.path.join(docs_folder, file)
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        sentences = split_into_sentences(text)

        current_chunk = []
        current_chunk_tokens = 0
        file_chunks = []

        for sentence in sentences:
            sentence_tokens = tokenizer.tokenize(sentence)
            sentence_token_count = len(sentence_tokens)

            if current_chunk_tokens + sentence_token_count > max_tokens:
                if current_chunk:
                    chunk_text = tokenizer.convert_tokens_to_string(current_chunk)
                    file_chunks.append(chunk_text)

                overlap_start = max(0, len(current_chunk) - overlap_tokens)
                current_chunk = current_chunk[overlap_start:] + sentence_tokens
                current_chunk_tokens = len(current_chunk)
            else:
                current_chunk.extend(sentence_tokens)
                current_chunk_tokens += sentence_token_count

        if current_chunk:
            chunk_text = tokenizer.convert_tokens_to_string(current_chunk)
            file_chunks.append(chunk_text)

        all_chunks.extend([(chunk, filename) for chunk in file_chunks])

    return all_chunks

if __name__ == "__main__":
    path = r"..."
    x = get_chunks(path)
    print(x)
