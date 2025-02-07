from flask import Flask, request, jsonify, send_file, send_from_directory
from PIL import Image, ImageOps
import os
from io import BytesIO
from flasgger import Swagger, swag_from
from flask import Flask
import zipfile

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3
}
swagger = Swagger(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No images part in request'}), 400
    
    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'No images uploaded'}), 400
    
    for file in files:
        if file.filename == '':
            continue
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    
    return jsonify({'message': 'Upload successful'}), 200


# @app.route("/upload", methods=["POST"])
# def upload_image():
#     """
#     Upload an image
#     ---
#     consumes:
#       - multipart/form-data
#     parameters:
#       - name: image
#         in: formData
#         type: file
#         required: true
#         description: Image file to upload
#     responses:
#       200:
#         description: Upload successful
#       400:
#         description: No image file provided or invalid file
#     """
#     if "image" not in request.files:
#         return jsonify({"error": "No image file provided"}), 400

#     image = request.files["image"]
#     if image.filename == "":
#         return jsonify({"error": "No selected file"}), 400

#     image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
#     image.save(image_path)

#     return jsonify({"message": "Upload successful", "path": image_path}), 200


@app.route("/image/<filename>", methods=["GET"])
def get_image(filename):
    """
    Retrieve an uploaded image
    ---
    parameters:
      - name: filename
        in: path
        required: true
        type: string
        description: Name of the image file
    responses:
      200:
        description: Image file
      404:
        description: File not found
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/upscale/<filename>", methods=["GET"])
def upscale_image(filename):
    """
    Upscale an existing image
    ---
    parameters:
      - name: filename
        in: path
        required: true
        type: string
        description: Name of the image file to upscale
    responses:
      200:
        description: Upscaled image
      404:
        description: File not found
    """
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(image_path):
        return jsonify({"error": "File not found"}), 404

    img = Image.open(image_path)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    
    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")


@app.route("/downscale/<filename>", methods=["GET"])
def downscale_image(filename):
    """
    Downscale an existing image
    ---
    parameters:
      - name: filename
        in: path
        required: true
        type: string
        description: Name of the image file to downscale
    responses:
      200:
        description: Downscale image
      404:
        description: File not found
    """
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(image_path):
        return jsonify({"error": "File not found"}), 404

    img = Image.open(image_path)
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    
    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

@app.route("/invert/<filename>", methods=["GET"])
def invert_image(filename):
    """
    Invert an existing image
    ---
    parameters:
      - name: filename
        in: path
        required: true
        type: string
        description: Name of the image file to invert
    responses:
      200:
        description: Inverted image
      404:
        description: File not found
    """
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(image_path):
        return jsonify({"error": "File not found"}), 404

    img = Image.open(image_path)
    img = ImageOps.invert(img.convert("RGB"))
    
    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")


# @app.route("/invert", methods=["POST"])
# def invert_uploaded_image():
#     """
#     Inverts an uploaded image from request data
#     ---
#     consumes:
#       - multipart/form-data
#     parameters:
#       - name: image
#         in: formData
#         type: file
#         required: true
#         description: Image file to invert
#     responses:
#       200:
#         description: Inverted image
#       400:
#         description: No image file provided
#     """
#     if "image" not in request.files:
#         return jsonify({"error": "No image file provided"}), 400

#     image = request.files["image"]
#     img = Image.open(image)
#     img = ImageOps.invert(img.convert("RGB"))
    
#     img_io = BytesIO()
#     img.save(img_io, format="PNG")
#     img_io.seek(0)

#     return send_file(img_io, mimetype="image/png")

@app.route("/invert", methods=["POST"])
def invert_uploaded_images():
    """
    Inverts multiple uploaded images from request data
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: images
        in: formData
        type: file
        required: true
        description: Image files to invert
    responses:
      200:
        description: Inverted images
      400:
        description: No image files provided
    """
    if "images" not in request.files:
        return jsonify({"error": "No image files provided"}), 400

    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "No images uploaded"}), 400

    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            img = Image.open(file)
            img = ImageOps.invert(img.convert("RGB"))
            
            img_io = BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)
            zipf.writestr(f"inverted_{file.filename}", img_io.read())
    
    zip_io.seek(0)
    return send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name="inverted_images.zip")

@app.route('/')
def index():
    """
    API home
    ---
    responses:
      200:
        description: Welcome message
    """
    return 'Welcome to the Image Processing API!'

    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    img = load_image(file)
    if img is None:
        return 'Invalid image file', 400

    format = request.form.get('format', 'PNG').upper()
    if format not in ['PNG', 'JPEG', 'GIF']:
        return 'Unsupported format', 400

    img_io = io.BytesIO()
    img.save(img_io, format)
    img_io.seek(0)

    return send_file(img_io, mimetype=f'image/{format.lower()}')

@app.route("/upscale", methods=["POST"])
def upscale_uploaded_image():
    """
    Upscales an uploaded image from request data
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Image file to upscale
    responses:
      200:
        description: Upscaled image
      400:
        description: No image file provided
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]
    img = Image.open(image)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)

    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

@app.route("/downscale", methods=["POST"])
def downscale_uploaded_image():
    """
    Downscale an uploaded image from request data
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Image file to downscale
    responses:
      200:
        description: Downscaled image
      400:
        description: No image file provided
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files["image"]
    img = Image.open(image)
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)

    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")


@app.route("/images", methods=["GET"])
def list_images():
    """
    Get all available images
    ---
    responses:
      200:
        description: List of images
    """
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return jsonify({"images": files})

if __name__ == '__main__':
    app.run(debug=True)