from ai.semantic_search import find_best_response

npc_name = "blacksmith"

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        break
    response = find_best_response(user_input, npc_name)
    print(f"{npc_name}: {response}")
