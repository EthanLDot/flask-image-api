from flask import Flask, request, jsonify, send_file, send_from_directory
from PIL import Image, ImageOps
import os
from io import BytesIO
from flasgger import Swagger, swag_from
from flask import Flask
import zipfile
import time

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
    
    start_time = time.time()
    for file in files:
        if file.filename == '':
            continue
        file_start_time = time.time()
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        print(str(time.time() - file_start_time) + 's')
    time_elapsed = time.time() - start_time
    print("Request complete")
    print(str(time_elapsed) + 's')
    return jsonify({'message': 'Upload successful', 'time_elapsed': time_elapsed}), 200


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

    start_time = time.time()
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_start_time = time.time()
            img = Image.open(file)
            img = ImageOps.invert(img.convert("RGB"))
            
            img_io = BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)
            zipf.writestr(f"inverted_{file.filename}", img_io.read())
            print(str(time.time() - file_start_time) + 's')
    zip_io.seek(0)
    time_elapsed = time.time() - start_time
    print("Request complete")
    print(str(time_elapsed) + 's')
    response = send_file(
        zip_io,
        mimetype='application/zip',
        as_attachment=True,
        download_name="inverted_images.zip"
    )
    response.headers["X-Time-Elapsed"] = str(time_elapsed)
    return response

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

@app.route("/upscale", methods=["POST"])
def upscale_uploaded_images():
    """
    Upscales multiple uploaded images from request data by a factor of 2
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: images
        in: formData
        type: file
        required: true
        description: Image files to upscale
    responses:
      200:
        description: Upscaled images
      400:
        description: No image files provided
    """
    if "images" not in request.files:
        return jsonify({"error": "No image files provided"}), 400

    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "No images uploaded"}), 400
    start_time = time.time()
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_start_time = time.time()
            img = Image.open(file)
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
            
            img_io = BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)
            zipf.writestr(f"upscaled_{file.filename}", img_io.read())
            print(str(time.time() - file_start_time) + 's')
    
    zip_io.seek(0)
    time_elapsed = time.time() - start_time
    print("Request complete")
    print(str(time_elapsed) + 's')
    response = send_file(
        zip_io,
        mimetype='application/zip',
        as_attachment=True,
        download_name="upscaled_images.zip"
    )
    response.headers["X-Time-Elapsed"] = str(time_elapsed)
    return response

@app.route("/downscale", methods=["POST"])
def downscale_uploaded_images():
    """
    Downscales multiple uploaded images from request data by a factor of 2
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: images
        in: formData
        type: file
        required: true
        description: Image files to downscale
    responses:
      200:
        description: Downscaled images
      400:
        description: No image files provided
    """
    if "images" not in request.files:
        return jsonify({"error": "No image files provided"}), 400

    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "No images uploaded"}), 400
    start_time = time.time()
    zip_io = BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_start_time = time.time()
            img = Image.open(file)
            img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
            
            img_io = BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)
            zipf.writestr(f"upscaled_{file.filename}", img_io.read())
            print(str(time.time() - file_start_time) + 's')
    
    zip_io.seek(0)
    time_elapsed = time.time() - start_time
    print("Request complete")
    print(str(time_elapsed) + 's')
    response = send_file(
        zip_io,
        mimetype='application/zip',
        as_attachment=True,
        download_name="downscaled_images.zip"
    )
    response.headers["X-Time-Elapsed"] = str(time_elapsed)
    return response


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