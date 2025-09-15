# Importing the required function from the main.py
from main import find_closest_match
import matplotlib.pyplot as plt
import cv2

# Test on an image
query_image_path = r"C:\Users\Webbies\Jupyter_Notebooks\Rehou_Image_Search\Query\QueryImg1.jpg"
matches = find_closest_match(query_image_path)

# Printing the Results
if matches:
    for i, (closest_match_path, similarity) in enumerate(matches):
        print(f"Match #{i+1}: {closest_match_path}")
        print(f"Similarity: {similarity:.4f}")
    # Display the Matched Images
    fig, axes = plt.subplots(1, len(matches)+1, figsize=(15, 5))
    # Display the Query Image
    query_img = cv2.imread(query_image_path)
    query_img = cv2.cvtColor(query_img, cv2.COLOR_BGR2RGB)
    axes[0].imshow(query_img)
    axes[0].set_title('Query Image')
    axes[0].axis('off')
    # Display the Matched Images
    for i, (path, similarity) in enumerate(matches):
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        axes[i+1].imshow(img)
        axes[i+1].set_title(f'Match #{i+1}\nScore: {similarity:.4f}')
        axes[i+1].axis('off')
    
    plt.tight_layout()
    plt.show()
else:
    print("No valid matches found.")



# if closest_match_path and similarity is not None:
#     print(f"Closest Match: {closest_match_path}")
#     print(f"Similarity: {similarity:.4f}")
# else:
#     print("No valid match found.")

# # Show the Image from Code Script
# img = cv2.imread(closest_match_path)
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# plt.imshow(img)
# plt.axis('off')
# plt.show()