import numpy as np

def normalize(vectors):
    vec_length = np.linalg.norm(vectors, axis=1)
    avg_length = np.mean(vec_length)
    normalized_vector = vectors/avg_length
    return normalized_vector