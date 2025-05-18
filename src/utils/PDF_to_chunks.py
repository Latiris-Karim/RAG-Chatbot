from pypdf import PdfReader
from transformers import AutoTokenizer
import os
import re

def split_into_sentences(text):
    return re.findall(r'[^.!?\n]+[.!?\n]', text)

def get_chunks(docs_folder, max_tokens=192, overlap_tokens=50):
    all_chunks = []
    files = [f for f in os.listdir(docs_folder) if os.path.isfile(os.path.join(docs_folder, f))]
    # Initialize the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    for file in files:
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
                # If adding this sentence would exceed max_tokens, save the current chunk
                if current_chunk:
                    chunk_text = tokenizer.convert_tokens_to_string(current_chunk)
                    file_chunks.append(chunk_text)
                
                # Start a new chunk, keeping the overlap
                overlap_start = max(0, len(current_chunk) - overlap_tokens)
                current_chunk = current_chunk[overlap_start:] + sentence_tokens
                current_chunk_tokens = len(current_chunk)
            else:
                # Add the sentence to the current chunk
                current_chunk.extend(sentence_tokens)
                current_chunk_tokens += sentence_token_count

        # Add any remaining text as a final chunk
        if current_chunk:
            chunk_text = tokenizer.convert_tokens_to_string(current_chunk)
            file_chunks.append(chunk_text)

        # Add all chunks from this file to the main list, including the filename at the end
        all_chunks.extend([f"{chunk}' '{file}" for chunk in file_chunks])

    return all_chunks

if __name__ == "__main__":
    path = r"..."
    x = get_chunks(path)
    print(x)
