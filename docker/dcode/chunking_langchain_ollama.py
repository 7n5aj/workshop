import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ollama import Client

# 1. Setup ChromaDB
client = chromadb.Client()
collection = client.get_or_create_collection(name="chunking_demo")
ollama_client = Client(host="http://localhost:11434")

# 2. Fairly big text as string
raw_text = """
The scheduled March 5 election is just over a month away and the results will be out within the next fortnight. However, it remains unclear whether the Parliament building will be ready in time for lawmakers to take oath.

The Gallery Baithak on the Singha Durbar premises housed the country’s Parliament from the time of the first parliamentary elections in 1959 until the reinstatement of the House in 2006. The House that was reinstated after the second people’s movement, which saw the rebel Maoists represented for the first time, also functioned from the same building.

However, a significant rise in the number of representatives in the Constituent Assembly in 2008, to 601, left the Gallery Baithak short of space. As a result, the Birendra International Convention Centre at New Baneshwar was chosen. Both constituent assemblies and the two federal parliaments, following the promulgation of Nepal's 2015 Constitution, operated from the convention centre.

The property was leased by the government, which paid nearly Rs150 million in annual rent. The lease agreement has not been renewed following an arson incident that rendered the property uninhabitable.

The parliament building was the first target of the September Gen Z movement. It was completely destroyed on September 9. With each passing day, the Parliament Secretariat and the government are under intense pressure to secure an alternative venue before the new House is elected.

Officials believe the under-construction buildings on the Singha Durbar premises will be ready. “Amid uncertainties, we wrote to the government to make a place available on time for the newly elected House,” Eakram Giri, spokesperson for the secretariat, told the Post. “The Ministry of Urban Development has assured that the new space will be ready in a month and a half.”

After operating the legislature from the rented building for a decade, the government began construction of dedicated facilities in 2019. The foundation stone for the 12 structures was laid in September that year, with a target completion date of three years. The joint venture of the China-based Second Harbour Engineering Company and Tundi Construction, a Nepali firm, won the contract.

However, even after missing the fifth deadline extension in the past three years, the construction remains incomplete.

Officials overseeing the construction say work has been expedited to prepare the space to accommodate both chambers of parliament. “The entire structure will not immediately be ready, but the chambers for both houses and a lobby connecting them will be ready by mid-February at the latest,” Roshan Shrestha, the project chief, told the Post.

The under-construction area, spread over 150 ropani (7.63 hectares), has been designed to accommodate 700 individuals in the chamber designated for the lower house. It will have a seating capacity of 400 for lawmakers on the main floor and 300 in the balcony for the press, visitors, and guests. The hall designated for the 59-strong National Assembly will have seating arrangements for over 250.

A separate hall with 350 seats is also under construction for the joint meeting of the two houses. Shrestha said that while the civil works, which involve the erection of the structure, have been completed, the interiors and the installation of the dome at the top remain incomplete.

“We have mobilised 406 people daily to complete interiors and the roofing. The production of chairs is going on simultaneously,” he said. “All the items related to information technology have been imported, which await installation.”

There is a constitutional compulsion to call the session within 30 days of the final results of the election to the House of Representatives. The session was called 50 days after the elections in November 2022, as the Election Commission took more than two weeks to announce the final results.

If the commission’s plan works, counting will be completed in less than a week, as only HoR votes need to be counted, unlike in the previous elections when provincial assembly polls were held simultaneously. Preparations of the final results will take another few days, the commission says.

If the commission faces no obstacle in conducting the elections, the House session needs to be called by mid-March.

“We need the space ready at least three weeks before the first meeting to make sure everything is functional. As it is the new place, we also need to conduct mock drills in advance,” said Giri. “The secretariat believes the government and the construction companies understand the sensitivity.”
"""
# 3. Split text into chunks using LangChain splitter


# Use LangChain's splitter with custom separator '\n' for paragraph splitting
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=0,
    separators=['\n']
)

chunks = [c.strip() for c in splitter.split_text(raw_text) if c.strip()]

print(f"Text split into {len(chunks)} chunks:")
for idx, c in enumerate(chunks):
    print(f"Chunk {idx}: '{c}'\n")

# 4. Embed and add to DB using Ollama nomic-embed-text
for i, text_chunk in enumerate(chunks):
    response = ollama_client.embed(model="nomic-embed-text", input=f"search_document: {text_chunk}")
    collection.add(
        ids=[f"chunk_{i}"],
        embeddings=[response["embeddings"][0]],
        documents=[text_chunk]
    )

# 5. User query: vectorize and retrieve
user_query = "Who earns $600?"
query_embed = ollama_client.embed(model="nomic-embed-text", input=f"query: {user_query}")["embeddings"][0]
results = collection.query(query_embeddings=[query_embed], n_results=1)

print("Most relevant chunk:")
for doc in results["documents"][0]:
    print(doc)
