from app.services.chat_service import ask_question

question = input("Question: ")

result = ask_question(question)

print("\nAnswer:\n")
print(result["answer"])

print("\nRetrieved Chunks:\n")

for i, chunk in enumerate(result["sources"], start=1):
    print(f"------ Chunk {i} ------")
    print(chunk[:300])
    print()