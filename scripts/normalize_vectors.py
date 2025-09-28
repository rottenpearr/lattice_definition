import numpy as np

# vec1 = [
#     [2,2,1],
#     [4,4,2]
# ]
# vec2 = [
#     [1,1,0.5],
#     [2,2,1]
# ]

def normalize(vectors):
    vec_length = np.linalg.norm(vectors, axis=1)
    avg_length = np.mean(vec_length)
    normalized_vector = vectors/avg_length
    return normalized_vector

# print(normalize(vec1))
# print(normalize(vec2))
