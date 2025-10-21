#!/usr/bin/env python3
"""
Simple HTTP File Server
Serves HTML, PNG, and PDF files from a specified directory.
Handles nested directories with directory listing support.
"""

import socket
import sys
import os
from pathlib import Path
from urllib.parse import unquote
import mimetypes

# Initialize mimetypes
mimetypes.init()

def parse_request(request_data):
    """Parse HTTP request and return method, path, and headers."""
    lines = request_data.split('\r\n')
    request_line = lines[0]
    parts = request_line.split()
    
    if len(parts) < 2:
        return None, None, {}
    
    method = parts[0]
    path = parts[1]
    
    # Parse headers
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    
    return method, path, headers

def get_content_type(file_path):
    """Determine content type based on file extension."""
    extension = file_path.suffix.lower()
    content_types = {
        '.html': 'text/html',
        '.htm': 'text/html',
        '.pdf': 'application/pdf',
        '.png': 'image/png',
    }
    return content_types.get(extension, 'application/octet-stream')

def generate_directory_listing(dir_path, url_path):
    """Generate an HTML page showing directory contents."""
    try:
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        return None
    
    # Start HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Directory listing for {url_path}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            padding: 8px;
            border-bottom: 1px solid #eee;
        }}
        li:hover {{
            background-color: #f5f5f5;
        }}
        a {{
            text-decoration: none;
            color: #2196F3;
            display: block;
        }}
        a:hover {{
            color: #0b7dda;
        }}
        .dir {{
            font-weight: bold;
        }}
        .dir::before {{
            content: "📁 ";
        }}
        .file::before {{
            content: "📄 ";
        }}
    </style>
</head>
<body>
    <h1>Directory listing for {url_path}</h1>
"""
    
    # Add parent directory link if not root
    if url_path != '/':
        parent_path = '/'.join(url_path.rstrip('/').split('/')[:-1]) or '/'
        html += f'    <ul>\n        <li><a href="{parent_path}" class="dir">.. (Parent Directory)</a></li>\n'
    else:
        html += '    <ul>\n'
    
    # List directories first, then files
    dirs = []
    files = []
    
    for item in items:
        item_path = os.path.join(dir_path, item)
        if os.path.isdir(item_path):
            dirs.append(item)
        else:
            files.append(item)
    
    # Add directories
    for item in dirs:
        link_path = url_path.rstrip('/') + '/' + item
        html += f'        <li><a href="{link_path}" class="dir">{item}/</a></li>\n'
    
    # Add files
    for item in files:
        link_path = url_path.rstrip('/') + '/' + item
        html += f'        <li><a href="{link_path}" class="file">{item}</a></li>\n'
    
    html += """    </ul>
</body>
</html>"""
    
    return html

def create_response(status_code, status_text, content_type, body, is_binary=False):
    """Create an HTTP response."""
    response = f"HTTP/1.1 {status_code} {status_text}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {len(body)}\r\n"
    response += "Connection: close\r\n"
    response += "\r\n"
    
    if is_binary:
        return response.encode('utf-8') + body
    else:
        return (response + body).encode('utf-8')

def handle_request(request_data, base_dir):
    """Process HTTP request and return response."""
    method, url_path, headers = parse_request(request_data)
    
    if method is None:
        return create_response(400, "Bad Request", "text/html", 
                             "<html><body><h1>400 Bad Request</h1></body></html>")
    
    if method != "GET":
        return create_response(405, "Method Not Allowed", "text/html",
                             "<html><body><h1>405 Method Not Allowed</h1></body></html>")
    
    # Decode and sanitize path
    url_path = unquote(url_path)
    
    # Remove leading slash and prevent directory traversal
    if url_path.startswith('/'):
        url_path = url_path[1:]
    
    # Prevent directory traversal attacks
    url_path = url_path.replace('..', '')
    
    # Construct full file path
    file_path = Path(base_dir) / url_path
    
    try:
        # Resolve to absolute path and ensure it's within base_dir
        file_path = file_path.resolve()
        base_dir_resolved = Path(base_dir).resolve()
        
        if not str(file_path).startswith(str(base_dir_resolved)):
            return create_response(403, "Forbidden", "text/html",
                                 "<html><body><h1>403 Forbidden</h1></body></html>")
        
        # Check if path exists
        if not file_path.exists():
            return create_response(404, "Not Found", "text/html",
                                 "<html><body><h1>404 Not Found</h1></body></html>")
        
        # Handle directory
        if file_path.is_dir():
            # Check for index.html
            index_path = file_path / "index.html"
            if index_path.exists():
                file_path = index_path
            else:
                # Generate directory listing
                listing_html = generate_directory_listing(file_path, '/' + url_path)
                if listing_html is None:
                    return create_response(403, "Forbidden", "text/html",
                                         "<html><body><h1>403 Forbidden</h1></body></html>")
                return create_response(200, "OK", "text/html", listing_html)
        
        # Read and serve file
        content_type = get_content_type(file_path)
        
        # Check if file type is supported
        if content_type == 'application/octet-stream':
            return create_response(415, "Unsupported Media Type", "text/html",
                                 "<html><body><h1>415 Unsupported Media Type</h1></body></html>")
        
        # Read file based on type
        if content_type in ['image/png', 'application/pdf']:
            with open(file_path, 'rb') as f:
                body = f.read()
            return create_response(200, "OK", content_type, body, is_binary=True)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                body = f.read()
            return create_response(200, "OK", content_type, body)
    
    except PermissionError:
        return create_response(403, "Forbidden", "text/html",
                             "<html><body><h1>403 Forbidden</h1></body></html>")
    except Exception as e:
        print(f"Error: {e}")
        return create_response(500, "Internal Server Error", "text/html",
                             "<html><body><h1>500 Internal Server Error</h1></body></html>")

def start_server(directory, host='0.0.0.0', port=8080):
    """Start the HTTP server."""
    # Verify directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.", flush=True)
        sys.exit(1)
    
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server started on http://{host}:{port}/", flush=True)
        print(f"Serving files from: {os.path.abspath(directory)}", flush=True)
        print("Press Ctrl+C to stop the server.", flush=True)
        print("Waiting for connections...", flush=True)
        
        while True:
            # Accept connection
            client_socket, client_address = server_socket.accept()
            print(f"\nConnection from {client_address}")
            
            try:
                # Receive request
                request_data = client_socket.recv(4096).decode('utf-8')
                
                if request_data:
                    # Parse and log request
                    lines = request_data.split('\r\n')
                    print(f"Request: {lines[0]}")
                    
                    # Handle request
                    response = handle_request(request_data, directory)
                    
                    # Send response
                    client_socket.sendall(response)
            
            except Exception as e:
                print(f"Error handling request: {e}")
            
            finally:
                client_socket.close()
    
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <directory> [port]")
        print("Example: python server.py ./content 8080")
        sys.exit(1)
    
    directory = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    start_server(directory, port=port)