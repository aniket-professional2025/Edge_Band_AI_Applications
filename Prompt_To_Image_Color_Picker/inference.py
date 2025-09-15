# Importing Required Packages
from main import generate_image

# Inference on the Prompt
prompt = "A futuristic city skyline at sunset, in cyberpunk style"
img = generate_image(prompt)
img.show()
img.save("generated_image.png")