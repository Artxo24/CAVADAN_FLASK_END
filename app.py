from flask import Flask, request, jsonify, send_file
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import os
import io
import zipfile

# Initialize Flask app
app = Flask(__name__)

# Load the BLIP2 model and processor globally (only once during app startup)
processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-flan-t5-xl")

# Ensure the static folder exists
STATIC_FOLDER = "static"
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route('/generate-caption', methods=['POST'])
def generate_caption():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    prompt = request.form.get('prompt', '')

    try:
        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
    except Exception as e:
        return jsonify({'error': f'Error opening image: {str(e)}'}), 500

    try:
        # Use the globally loaded model and processor
        inputs = processor(images=image, text=prompt, return_tensors="pt")
        outputs = model.generate(**inputs)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        return jsonify({'error': f'Error generating caption: {str(e)}'}), 500

    captioned_image_path = os.path.join(STATIC_FOLDER, "captioned_image.jpg")
    try:
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        text_width, text_height = draw.textsize(caption, font=font)
        image_width, image_height = image.size
        x = (image_width - text_width) / 2
        y = image_height - text_height - 10
        draw.text((x, y), caption, fill="white", font=font)
        image.save(captioned_image_path)
    except Exception as e:
        return jsonify({'error': f'Error saving captioned image: {str(e)}'}), 500

    audio_path = os.path.join(STATIC_FOLDER, "caption_audio.mp3")
    try:
        tts = gTTS(caption)
        tts.save(audio_path)
    except Exception as e:
        return jsonify({'error': f'Error converting caption to audio: {str(e)}'}), 500

    zip_path = os.path.join(STATIC_FOLDER, "captioned_output.zip")
    try:
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(captioned_image_path, arcname="captioned_image.jpg")
            zipf.write(audio_path, arcname="caption_audio.mp3")
    except Exception as e:
        return jsonify({'error': f'Error creating ZIP file: {str(e)}'}), 500

    return jsonify({'caption': caption, 'zip_url': f'/download-zip?file={zip_path}'})

@app.route('/download-zip', methods=['GET'])
def download_zip():
    file_path = request.args.get('file')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'ZIP file not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use dynamic port binding for Render
    app.run(host='0.0.0.0', port=port)
