from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data (replace with your actual data)
image_data = {
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Fireball_imaged_by_the_Perenjori_DFN_station.jpg/330px-Fireball_imaged_by_the_Perenjori_DFN_station.jpg",
    "metadata": {
        "description": "Sample image",
        "author": "John Doe"
    }
}

@app.route('/image_data', methods=['GET'])
def get_image_data():
    return jsonify(image_data)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    # Get JSON data from the request
    data = request.get_json()

    # Process the data (you can save the image or metadata)
    # For example, you can print the received data
    print("Received image data:", data)

    # Return a response (you can customize this as needed)
    return jsonify({"message": "Image received successfully"})

if __name__ == '__main__':
    app.run(debug=True)
