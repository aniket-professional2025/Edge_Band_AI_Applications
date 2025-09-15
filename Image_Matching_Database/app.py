# Importing necessary libraries
import streamlit as st
from PIL import Image
import os
import tempfile
from main import find_closest_match # This imports the function from your main.py file

# Set up the Streamlit page configuration
st.set_page_config(layout="wide", page_title="Image Match Finder")

# Custom Header and description using Markdown for better styling
st.markdown("""
    <h1 style='text-align: center; color: #1f77b4;'>Image Match Finder</h1>
    <p style='text-align: center; font-size: 1.2em; color: #555;'>
        Upload an image and press 'Search' button to find the top two most similar images.
    </p>
    <hr style='border: 1px solid #ddd;'>
""", unsafe_allow_html=True)

# Create the file uploader widget
st.markdown("### Upload your image here...")
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

# Main logic to process the uploaded file
if uploaded_file is not None:
    # Add a search button below the uploader
    search_button = st.button("Search Images in the Database")

    # The search logic is now triggered by the button click
    if search_button:
        # Use a temporary file to save the uploaded image for processing
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            st.write("---") # Add a separator
            st.info("Searching for the top 2 matches...")

            # Create a **three-column layout** for all three images (uploaded + 2 results)
            col1, col2, col3 = st.columns(3)

            # Find the two closest matches
            matches = find_closest_match(tmp_file_path, num_results=2)

            with col1:
                st.markdown("<h3 style='text-align: center;'>Your Uploaded Image</h3>", unsafe_allow_html = True)
                user_image = Image.open(uploaded_file)
                st.image(user_image, caption = uploaded_file.name, use_container_width = True)

            # Check if matches were found and display them
            if matches and len(matches) > 0:
                # Display the first match in the second column
                if len(matches) > 0:
                    first_match_path, first_similarity = matches[0]
                    with col2:
                        st.markdown("<h3 style='text-align: center;'>🥇 Top Match</h3>", unsafe_allow_html=True)
                        first_match_image = Image.open(first_match_path)
                        st.image(first_match_image, caption=os.path.basename(first_match_path), use_container_width=True)
                        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Similarity Score: {first_similarity:.4f}</p>", unsafe_allow_html=True)
                
                # Display the second match in the third column
                if len(matches) > 1:
                    second_match_path, second_similarity = matches[1]
                    with col3:
                        st.markdown("<h3 style='text-align: center;'>🥈 Second Match</h3>", unsafe_allow_html=True)
                        second_match_image = Image.open(second_match_path)
                        st.image(second_match_image, caption=os.path.basename(second_match_path), use_container_width=True)
                        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Similarity Score: {second_similarity:.4f}</p>", unsafe_allow_html=True)
                else:
                    st.warning("Only one valid match was found.")
            else:
                st.error("Could not find any matches in the database. Please check your database folder or try another image.")
        finally:
            # Clean up the temporary file
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

else:
    st.info("Please upload an image to start the search process.")