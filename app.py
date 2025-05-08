from flask import Flask, request, jsonify
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image
import io
import os

# Initialize Flask app
app = Flask(__name__)

# Load the ViT-GPT2 model and processor globally
model_name = "nlpconnect/vit-gpt2-image-captioning"
model = VisionEncoderDecoderModel.from_pretrained(model_name)
processor = ViTImageProcessor.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

@app.route('/generate-caption', methods=['POST'])
def generate_caption():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    prompt = request.form.get('prompt', '')  # Optional prompt

    try:
        # Open the image
        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
    except Exception as e:
        return jsonify({'error': f'Error opening image: {str(e)}'}), 500

    try:
        # Preprocess the image
        pixel_values = processor(images=image, return_tensors="pt").pixel_values

        # If a prompt is provided, include it as the initial input for the model
        if prompt:
            input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        else:
            input_ids = None  # No prompt, start generating from scratch

        # Generate the caption
        output_ids = model.generate(pixel_values, input_ids=input_ids, max_length=16, num_beams=4)
        caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    except Exception as e:
        return jsonify({'error': f'Error generating caption: {str(e)}'}), 500

    return jsonify({'caption': caption})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use dynamic port binding for Render
    app.run(host='0.0.0.0', port=port)
