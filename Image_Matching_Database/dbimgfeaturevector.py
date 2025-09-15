# Importing Required Packages
import json
import os
from glob import glob
from main import get_feature_vector

# Define a function to calculate the fewature vectors of database images
def create_database_image_feature_vector(database_folder):
    # Define the path for the JSON cache file
    cache_file = os.path.join(database_folder, "db_feature_vector_51.json")

    # Check if the cache file already exists or not
    if os.path.exists(cache_file):
        print(f"---------------- Loading Feature Database from {cache_file} ----------------")
        with open(cache_file, 'r') as f:
            database = json.load(f)
        print(f"----------------- Loaded {len(database)} feature vectors from cache -----------------")
        return database

    # If cache file does not exist, proceed with feature extraction
    print(f"----------------- Creating Feature Database from {database_folder} -----------------------")
    database = []
    # Loop through all images in the database folder
    image_paths = glob(os.path.join(database_folder, "*.jpg")) + glob(os.path.join(database_folder, "*.jpeg")) + glob(os.path.join(database_folder, "*.png"))
    for path in image_paths:
        print(f"----------------- Processing {os.path.basename(path)} -----------------")
        feature_vector = get_feature_vector(path)
        if feature_vector is not None:
            # Convert numpy array to list for JSON serialization
            database.append({'path': path, 'features': feature_vector.tolist()})

    # After creating the database, save it to the JSON file
    print(f"----------------- Feature Database Created Successfully. {len(database)} images processed -----------------")
    with open(cache_file, 'w') as f:
        json.dump(database, f, indent = 2)
    print(f"----------------- Saved feature vectors to {cache_file} for future use -----------------")
    
    return database

# Inference on the Database folder
if __name__ == "__main__":
    database_folder = r"C:\Users\Webbies\Jupyter_Notebooks\Rehou_Image_Search\Database"
    create_database_image_feature_vector(database_folder)