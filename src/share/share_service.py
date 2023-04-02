from flask import Blueprint, request, send_from_directory, Response, jsonify, current_app
from flask_httpauth import HTTPTokenAuth
from werkzeug.utils import secure_filename
import os, time, logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
share_blueprint = Blueprint('share_service', __name__)
auth = HTTPTokenAuth(scheme='Bearer')

def secure_path(path):
    parts = path.split('/')
    return '/'.join(secure_filename(part) for part in parts)

@auth.verify_token
def verify_token(token):
    susi_api_key = current_app.config['SUSI_API_KEY']
    if susi_api_key and token == susi_api_key:
        return "valid-user"
    elif not susi_api_key:
        return "valid-user"

@share_blueprint.route('/', methods=['GET'], defaults={'req_path': ''})
@share_blueprint.route('/<path:req_path>', methods=['GET'])
def file_sharing(req_path):
    data_path = current_app.config['DATA_PATH']
    req_path = secure_path(req_path)
    abs_path = os.path.join(data_path, req_path)
    #logger.debug("data_path:    %s", data_path)
    #logger.debug("req_path:     %s", req_path)
    #logger.debug("abs_path:     %s", abs_path)

    # Check for directory traversal attempts
    if not os.path.abspath(abs_path).startswith(data_path):
        return "Invalid path request", 403

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_from_directory(data_path, req_path)

    # Check if an index.json file is requested
    if req_path.endswith("index.json"):
        parent_path = os.path.dirname(abs_path.rstrip("index.json"))
        files = [] if not os.path.exists(parent_path) else os.listdir(parent_path)
        file_info = []
        for file in files:
            file_abs_path = os.path.join(abs_path.rstrip("index.json"), file)
            stats = os.stat(file_abs_path)
            file_info.append({
                "name": file, # file name
                "size": stats.st_size, # file size in bytes
                "atime": int(stats.st_atime * 1000), # access time in millisonde since epoch
                "mtime": int(stats.st_mtime * 1000), # modified time in millisonde since epoch
                "last_accessed": time.ctime(stats.st_atime),
                "last_modified": time.ctime(stats.st_mtime)
            })
        return jsonify({'path': req_path, 'dir': file_info})

    # Check if path is a directory
    if not os.path.exists(abs_path) or not os.path.isdir(abs_path):
        return f"Directory {abs_path} does not exist.", 404
    
    # Show directory contents
    files = os.listdir(os.path.dirname(abs_path)) if req_path.endswith("index.html") else os.listdir(abs_path)
    file_links = [f'<li><a href="{os.path.join(req_path, file)}">{file}</a></li>' for file in files]
    return Response(f'<ul>{"".join(file_links)}</ul>', mimetype='text/html')

# authorized access to upload a file to the data path
# this can be called i.e. with:
# curl -X POST -H 'Authorization: Bearer your-application-key' -F 'file=@/path/to/myfile.txt' http://localhost:8080/subdir/myfile.txt
@share_blueprint.route('/<path:req_path>', methods=['POST'])
@auth.login_required
def upload_file(req_path):
    if 'file' not in request.files:
        return 'No file part in the request', 400
    file = request.files['file']

    if file.filename == '':
        return 'No file selected for uploading', 400

    data_path = current_app.config['DATA_PATH']
    req_path = secure_path(req_path)
    full_path = os.path.join(data_path, req_path)

    # Prevent directory traversal
    if not os.path.abspath(full_path).startswith(data_path):
        return "Invalid path request", 403

    os.makedirs(os.path.dirname(full_path), exist_ok=True)  # create directory if it does not exist
    file.save(full_path)
    logger.debug("stored file to :     %s", req_path)

    return f'File {full_path} uploaded successfully', 201

# authorized access to delete a file from the data path
# this can be called i.e. with:
# curl -X DELETE -H 'Authorization: Bearer your-application-key' http://localhost:8080/subdir/myfile.txt
@share_blueprint.route('/<path:req_path>', methods=['DELETE'])
@auth.login_required
def delete_file(req_path):
    data_path = current_app.config['DATA_PATH']
    req_path = secure_path(req_path)
    abs_path = os.path.join(data_path, req_path)
    
    # Prevent directory traversal
    if not os.path.abspath(abs_path).startswith(data_path):
        return "Invalid path request", 403
    
    # Check if path is a file
    if not os.path.isfile(abs_path):
        return f'File {req_path} does not exist.', 404
    
    os.remove(abs_path)
    logger.debug("deleted file from :  %s", req_path)
    
    # Remove any empty directories
    directory = os.path.dirname(abs_path)
    while directory != data_path:
        if not os.listdir(directory):  # if directory is empty
            os.rmdir(directory)
        directory = os.path.dirname(directory)
    
    return f'File {req_path} deleted successfully', 200