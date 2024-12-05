from flask import Flask, request, render_template, send_from_directory
import os
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'books'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # List folders in the library
    books = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, f))]
    return render_template('index.html', books=books)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and file.filename.endswith('.zip'):
        folder_name = file.filename.rsplit('.', 1)[0]
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        
        # Save and extract the zip file
        os.makedirs(folder_path, exist_ok=True)
        zip_path = os.path.join(folder_path, file.filename)
        file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(folder_path)
        os.remove(zip_path)  # Clean up zip file after extraction
    return 'Upload successful! <a href="/">Go back</a>'

@app.route('/read/<book_name>')
def read(book_name):
    # Path to the folder containing the book HTML file
    nested_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], book_name, book_name)
    html_file_path = os.path.join(nested_folder_path, f"{book_name}")
    
    # Check if the HTML file exists and serve it
    if os.path.exists(html_file_path):
        return send_from_directory(nested_folder_path, f"{book_name}.html")
    else:
        return f"Error: The book '{book_name}' does not have a corresponding HTML file."


@app.route('/books/<book_name>/<path:filename>')
def book_file(book_name, filename):
    # Serve additional files (images, CSS, etc.)
    book_path = os.path.join(app.config['UPLOAD_FOLDER'], book_name)
    return send_from_directory(book_path, filename)

if __name__ == '__main__':
    app.run(debug=True)
