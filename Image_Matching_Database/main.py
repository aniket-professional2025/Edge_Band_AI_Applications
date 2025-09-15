# Description:
# Euclidean Distance: A score of 0 is a perfect match. The score increases as images become less similar. 
# Your previous code correctly found the smallest distance.

# Cosine Similarity: A score of 1.0 is a perfect match (identical images). 
# The score decreases as images become less similar. 
# A score of 0 indicates no similarity (the vectors are perpendicular).

# ----------------------------------------------------------------------------

# Importing Required Packages
import torch
import os
import numpy as np
from PIL import Image
import json
from transformers import ViTFeatureExtractor, ViTModel
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from glob import glob

# ---------------------------------------------------

# Loading the Model and the Feature Extractor
print("---------------- Loading the Pre-trained ViT model and Feature Extractor ------------------")
model_name = "google/vit-base-patch16-224"
feature_extractor = ViTFeatureExtractor.from_pretrained(model_name)
model = ViTModel.from_pretrained(model_name)
print("---------------- Model Loaded Successfully ----------------")

# ----------------------------------------------------

# Function to Extract Feature
def get_feature_vector(image_path):
    try:
        # Load the Image using pillow
        image = Image.open(image_path).convert("RGB")
        # Preprocess the image for the model
        inputs = feature_extractor(images=image, return_tensors="pt")
        # Get the model outputs
        with torch.no_grad():
            outputs = model(**inputs)
        # Extract the feature vector (the output of the last hidden state)
        last_hidden_states = outputs.last_hidden_state
        feature_vector = last_hidden_states[:, 0, :].squeeze().numpy()
        return feature_vector
    except Exception as e:
        print(f"------------------- Error occurred while processing {image_path}: {e} -----------------------")
        return None
    
# --------------------------------------------------------

def create_feature_database(database_folder):
    # Define the path for the JSON cache file
    cache_file = os.path.join(database_folder, 'db_feature_vector_51.json')

    # Check if the cache file already exists
    if os.path.exists(cache_file):
        print(f"----------------- Loading Feature Database from {cache_file} -----------------------")
        with open(cache_file, 'r') as f:
            database = json.load(f)
        print(f"----------------- Loaded {len(database)} feature vectors from cache -----------------")
        # Convert features back to numpy arrays
        for item in database:
            item['features'] = np.array(item['features'])
        return database
    else:
        print(f"----------------- Error: No feature cache file found at {cache_file} -----------------")
        return []

# --------------------------------------------------------------------

# Function to Search and Match the database
def search_database(query_feature_vector, database, num_results = 2):
    print("---------------- Searching the Database for Similar Images --------------------")
    # Extract feature vectors from the database for bulk processing
    db_feature_vectors = np.array([entry['features'] for entry in database])
    db_path = [entry['path'] for entry in database]
    # Calculate Euclidean distances
    similarity = cosine_similarity(query_feature_vector.reshape(1, -1), db_feature_vectors)[0]
    # Combine Paths and distances, then sort by distances
    results = sorted(zip(db_path, similarity), key=lambda x: x[1], reverse = True) # reverse = True means descending
    return results[:num_results]

# --------------------------------------------------------------------

# The main Execution block
def find_closest_match(query_image_path, num_results = 2):
    # Define the path to your existing database folder
    database_folder = r"C:\Users\Webbies\Jupyter_Notebooks\Rehou_Image_Search\Database"
    
    # Check if the query image exists
    if not os.path.exists(query_image_path):
        print(f"------------------- Error: Query image does not exist at {query_image_path} --------------------")
        return None
        
    # Create the feature database
    feature_database = create_feature_database(database_folder)
    
    if not feature_database:
        print("No valid images found in the database folder. Please check folder path or image formats.")
        return None
        
    print(f"--------------------- Processing the Query Image: {os.path.basename(query_image_path)} -----------------------")
    query_vector = get_feature_vector(query_image_path)
    
    if query_vector is not None:
        # Search the database for the single best match
        results = search_database(query_vector, feature_database, num_results = num_results)
        
        if results:
            print(f"---------------- Top {len(results)} matches found: ------------------------")
            for path, similarity in results:
                print(f"-------- Match Found: {os.path.basename(path)} with a similarity of {similarity:.4f}")
            return results
        else:
            print("------------- No matches found. -------------------")
            return None
    else:
        print("------------ The Query Vector is None -------------------")
        return None
    


    #         # The search_database function returns a list of tuples, so we take the first element
    #         closest_match_path, similarity = results[0]
    #         print(f"Match Found: {os.path.basename(closest_match_path)} with a similarity of {similarity:.4f}")
    #         return closest_match_path, similarity
    #     else:
    #         print("No matches found.")
    #         return None, None
    # else:
    #     print("------------------------ The query vector is None-------------------------")
    #     return None, None