import os
import json
import chromadb
from ollama import Client
from langchain_text_splitters import RecursiveCharacterTextSplitter

chat_bot = Client(host="http://localhost:11434")

client = chromadb.PersistentClient()
collection = client.get_or_create_collection(name="articles_db")
remote_client = Client(host="http://localhost:11434")

counter = 0
if os.path.exists("counter.txt"):
    print('counter.txt found. Resuming from last count.')
    with open("counter.txt", "r") as f:
        counter = int(f.read().strip())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0,
    separators=[".", "\n"]
   )

with open("articles.jsonl", "r", encoding="utf-8") as f:
    for a_i, article in enumerate(f):
        if a_i <= counter:
            print(f"Skipping line {a_i} with counter {counter}")  # Skip already processed articles          
            continue
        print(f"Adding new line {a_i}...")
        article = json.loads(article)
        content = article["content"]
        title = article["title"]
        
        sentences = [c.strip() for c in splitter.split_text(content) if c.strip()]

        for s_i, sentence in enumerate(sentences):
            response = remote_client.embed(
            model="nomic-embed-text", 
            input=f"search_document: {sentence}"
            )
            collection.add(
            ids=[f"article_{a_i}sentence_{s_i}"],
            embeddings=[response["embeddings"][0]],
            documents=[sentence],
            metadatas=[{"title": title, "article_index": a_i, "sentence_index": s_i}]
            )
        counter +=1

with open("counter.txt", "w") as f:
    f.write(str(counter))

print("Database built successfully!")

while True:
    user_input = input("What's your doubt? (Type 'exit' or 'quit' to stop) ")
    if user_input.lower() in ["exit", "quit"]:
        print("(Zzz) Goodbye!")
        break
    query_embed = remote_client.embed(
    model="nomic-embed-text", 
    input=f"query: {user_input}"
    )["embeddings"][0]
    results = collection.query(
    query_embeddings=[query_embed],
    n_results=2)
    
    context = "\n".join(results["documents"][0])
    
    prompt = f"""You are a helpful assistant. Answer ONLY from the provided context. If the answer is not in the context, say "I don't know".
    Context: {context}
    Question: {user_input}
    """

    response = chat_bot.generate(
    model="llama3:8b-instruct-q5_K_M", 
    prompt=prompt, 
    options={"temperature": 0.1}
    )
    print(f"Answer: {response['response']}")