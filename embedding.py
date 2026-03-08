import numpy as np
import os
from getpass import getpass
from openai import OpenAI

#https://colab.research.google.com/drive/16oeaa8j9F6BHZdB-diJ_ATQZs9xpJynJ?usp=sharing#scrollTo=nK3iA651IHsK


# ---------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

client = OpenAI(
    # Recommended: use environment variable for production
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# First, let's create embeddings for a set of words
words = [
    "king", "queen", "man", "woman",
    "apple", "banana", "orange", "pear",
    "castle", "throne"
]

# Get embeddings for all words
response = client.embeddings.create(
    model="text-embedding-3-large",
    input=words,
    encoding_format="float"
)

# Extract the embeddings
embeddings = [data.embedding for data in response.data]

print(f"Embedding dimension: {len(embeddings[0])}")
print(f"Number of embeddings: {len(embeddings)}")

# Function to compute dot product between two vectors
def dot_product(vec1, vec2):
    return np.dot(vec1, vec2)

# Compute similarity matrix (dot products between all pairs)
similarity_matrix = np.zeros((len(words), len(words)))
for i in range(len(words)):
    for j in range(len(words)):
        similarity_matrix[i][j] = dot_product(embeddings[i], embeddings[j])

# Print similarity matrix with labels
print("\nSimilarity Matrix (Dot Products):")
print("          " + " ".join(f"{word:<8}" for word in words))
for i, word in enumerate(words):
    row_values = " ".join(f"{similarity_matrix[i][j]:.4f}  " for j in range(len(words)))
    print(f"{word:<10} {row_values}")

# Check specific relationships
king_queen_similarity = dot_product(embeddings[0], embeddings[1])
apple_banana_similarity = dot_product(embeddings[4], embeddings[5])

print("\nSpecific relationships:")
print(f"Similarity between 'king' and 'queen': {king_queen_similarity:.4f}")
print(f"Similarity between 'apple' and 'banana': {apple_banana_similarity:.4f}")
print(f"Similarity between 'king' and 'apple': {dot_product(embeddings[0], embeddings[4]):.4f}")

# We expect king/queen to be closer to each other than king/apple
# And apple/banana to be closer to each other than queen/banana
#-ve means less co-related, string simalirity and weak relationship

# Embedding dimension: 3072
# Number of embeddings: 10

# Similarity Matrix (Dot Products):
#           king     queen    man      woman    apple    banana   orange   pear     castle   throne  
# king       1.0000   0.5552   0.4183   0.2938   0.3243   0.3305   0.2879   0.2802   0.3615   0.4027  
# queen      0.5552   1.0000   0.3072   0.4132   0.3145   0.3191   0.2983   0.2996   0.2969   0.3354  
# man        0.4183   0.3072   1.0000   0.5713   0.3098   0.3495   0.2972   0.2695   0.2998   0.2650  
# woman      0.2938   0.4132   0.5713   1.0000   0.3199   0.2937   0.2784   0.2533   0.2449   0.2491  
# apple      0.3243   0.3145   0.3098   0.3199   1.0000   0.4619   0.4588   0.4391   0.3002   0.2340  
# banana     0.3305   0.3191   0.3495   0.2937   0.4619   1.0000   0.4579   0.3636   0.2777   0.2075  
# orange     0.2879   0.2983   0.2972   0.2784   0.4588   0.4579   1.0000   0.3822   0.2848   0.2174  
# pear       0.2802   0.2996   0.2695   0.2533   0.4391   0.3636   0.3822   1.0000   0.2788   0.1929  
# castle     0.3615   0.2969   0.2998   0.2449   0.3002   0.2777   0.2848   0.2788   1.0000   0.3888  
# throne     0.4027   0.3354   0.2650   0.2491   0.2340   0.2075   0.2174   0.1929   0.3888   1.0000  

# Specific relationships:
# Similarity between 'king' and 'queen': 0.5552
# Similarity between 'apple' and 'banana': 0.4619
# Similarity between 'king' and 'apple': 0.3243