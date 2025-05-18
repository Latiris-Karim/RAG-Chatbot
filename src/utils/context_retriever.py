import torch
from datasets import load_dataset
from sentence_transformers.util import semantic_search
from .embedder import get_embedding
import csv


def get_context(question, embeddings):
    """
    Function to find context for a query using cosine similarity search.
    
    Args:
        question (str): The user's question or query.
        embeddings (torch.Tensor): Pre-loaded tensor embeddings of a dataset.
    Returns:
        List[str]: A list of context chunks relevant to the query.
    """
    #Convert question to embeddings
    output = get_embedding(question)
    query_embeddings = torch.FloatTensor(output)  
    
    #Search for nearest neighbors using cosine similarity search
    hits = semantic_search(query_embeddings, embeddings, top_k=3)
    
    with open("chunks.csv", encoding="utf-8", errors="replace") as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        texts = [txtchunk for txtchunk in reader]
    
    #Retrieve and return the matching context chunks
    
    context = [texts[0][hits[0][i]['corpus_id']] for i in range(len(hits[0]))]#corpus id just means list index of that chunk 
    #if using local embedding retrieval i probably need to rewrite this differently
    return context

if __name__ == "__main__":
    schule_embeddings = load_dataset('fox133/testing123')#new account
    dataset_embeddings = torch.from_numpy(schule_embeddings["train"]
                                            .to_pandas()
                                            .to_numpy()).to(torch.float)
    question = "?"
    context = get_context(question, dataset_embeddings)

   
