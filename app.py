from flask import Flask, request, jsonify, send_file
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import os
import io
import zipfile

app = Flask(__name__)

# Load the BLIP2-FLAN-T5-XL model and processor (once for efficiency)
processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-flan-t5-xl")

@app.route('/generate-caption', methods=['POST'])
def generate_caption():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    prompt = request.form.get('prompt', '')

    try:
        # Open the image
        image = Image.open(io.BytesIO(image_file.read())).convert("RGB")
    except Exception as e:
        return jsonify({'error': f'Error opening image: {e}'}), 500

    try:
        # Process the image and prompt
        inputs = processor(images=image, text=prompt, return_tensors="pt")
        outputs = model.generate(**inputs)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        return jsonify({'error': f'Error generating caption: {e}'}), 500

    # Save the captioned image
    captioned_image_path = "captioned_image.jpg"
    try:
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()  # Use default font
        text_width, text_height = draw.textsize(caption, font=font)
        image_width, image_height = image.size
        x = (image_width - text_width) / 2
        y = image_height - text_height - 10  # Padding from bottom
        draw.text((x, y), caption, fill="white", font=font)
        image.save(captioned_image_path)
    except Exception as e:
        return jsonify({'error': f'Error saving captioned image: {e}'}), 500

    # Save caption as an audio file
    audio_path = "caption_audio.mp3"
    try:
        tts = gTTS(caption)
        tts.save(audio_path)
    except Exception as e:
        return jsonify({'error': f'Error converting caption to audio: {e}'}), 500

    # Create a ZIP file containing the image and audio
    zip_path = "captioned_output.zip"
    try:
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(captioned_image_path)
            zipf.write(audio_path)
    except Exception as e:
        return jsonify({'error': f'Error creating ZIP file: {e}'}), 500

    # Return the download URL for the ZIP file
    return jsonify({'zip_url': f'/download-zip?file={zip_path}'})

@app.route('/download-zip', methods=['GET'])
def download_zip():
    file_path = request.args.get('file')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'ZIP file not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)