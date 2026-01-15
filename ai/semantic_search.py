import numpy as np

from ai.embeddings import embed
from db.mongo import dialogue_collection


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def normalize(text):
    return text.lower().strip()


def find_best_response(user_input: str, npc_name: str, threshold=0.6):
    """
    Find the most semantically similar NPC response.
    Returns a default message if similarity is below threshold.
    """
    query_vec = embed(normalize(user_input))

    candidates = dialogue_collection.find({"npc": npc_name})

    best_score = -1
    best_response = "I don't understand what you mean."

    for c in candidates:
        score = cosine_similarity(query_vec, c["embedding"])
        if score > best_score:
            best_score = score
            best_response = c["response"]

    if best_score < threshold:
        return "I don't understand what you mean."

    return best_response
