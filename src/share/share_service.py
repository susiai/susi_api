from flask import Blueprint, send_from_directory, Response, jsonify
import os
import time

share_blueprint = Blueprint('share_service', __name__)
base_dir = 'data'

@share_blueprint.route('/', defaults={'req_path': ''})
@share_blueprint.route('/<path:req_path>')
def file_sharing(req_path):
    abs_path = os.path.join(base_dir, req_path)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_from_directory(base_dir, req_path)

    # Check if an index.json file is requested
    if req_path.endswith("/index.json"):
        files = os.listdir(abs_path.rstrip("/index.json"))
        file_info = []
        for file in files:
            file_abs_path = os.path.join(abs_path.rstrip("/index.json"), file)
            stats = os.stat(file_abs_path)
            file_info.append({
                "filename": file,
                "filesize": stats.st_size,
                "last_modified": time.ctime(stats.st_mtime)
            })
        return jsonify(file_info)

    # Show directory contents
    files = os.listdir(abs_path)
    file_links = [f'<li><a href="{os.path.join(req_path, file)}">{file}</a></li>' for file in files]
    return Response(f'<ul>{"".join(file_links)}</ul>', mimetype='text/html')
