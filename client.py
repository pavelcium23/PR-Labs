#!/usr/bin/env python3
"""
Simple HTTP Client
Downloads files from the HTTP server or displays HTML content.
Usage: python client.py server_host server_port url_path directory
"""

import socket
import sys
import os
from pathlib import Path

def send_request(host, port, path):
    """Send HTTP GET request and return response."""
    # Create socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server
        client_socket.connect((host, port))
        
        # Create HTTP request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}:{port}\r\n"
        request += "Connection: close\r\n"
        request += "\r\n"
        
        # Send request
        client_socket.sendall(request.encode('utf-8'))
        
        # Receive response
        response_data = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            response_data += chunk
        
        return response_data
    
    finally:
        client_socket.close()

def parse_response(response_data):
    """Parse HTTP response into headers and body."""
    # Split headers and body
    try:
        header_end = response_data.index(b'\r\n\r\n')
        headers_data = response_data[:header_end].decode('utf-8')
        body_data = response_data[header_end + 4:]
    except ValueError:
        return None, None, None, None
    
    # Parse status line
    lines = headers_data.split('\r\n')
    status_line = lines[0]
    parts = status_line.split(' ', 2)
    
    if len(parts) < 3:
        return None, None, None, None
    
    status_code = int(parts[1])
    status_text = parts[2]
    
    # Parse headers
    headers = {}
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    
    return status_code, status_text, headers, body_data

def get_filename_from_path(url_path):
    """Extract filename from URL path."""
    path_parts = url_path.rstrip('/').split('/')
    if path_parts:
        filename = path_parts[-1]
        if filename:
            return filename
    return "downloaded_file"

def handle_response(status_code, headers, body_data, url_path, save_directory):
    """Handle response based on content type."""
    if status_code != 200:
        print(f"Error: HTTP {status_code}")
        if body_data:
            try:
                print(body_data.decode('utf-8'))
            except:
                print("Could not decode response body")
        return
    
    content_type = headers.get('content-type', '')
    
    if 'text/html' in content_type:
        # Print HTML content
        try:
            html_content = body_data.decode('utf-8')
            print(html_content)
        except UnicodeDecodeError:
            print("Error: Could not decode HTML content")
    
    elif 'image/png' in content_type or 'application/pdf' in content_type:
        # Save binary file
        if not save_directory:
            print("Error: No directory specified for saving file")
            return
        
        # Create directory if it doesn't exist
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        
        # Determine filename
        filename = get_filename_from_path(url_path)
        
        # Ensure proper extension
        if 'image/png' in content_type and not filename.endswith('.png'):
            filename += '.png'
        elif 'application/pdf' in content_type and not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # Save file
        filepath = os.path.join(save_directory, filename)
        
        with open(filepath, 'wb') as f:
            f.write(body_data)
        
        print(f"File saved: {filepath}")
        print(f"Size: {len(body_data)} bytes")
    
    else:
        print(f"Unknown content type: {content_type}")
        print("Response body (first 500 bytes):")
        try:
            print(body_data[:500].decode('utf-8', errors='replace'))
        except:
            print(body_data[:500])

def main():
    """Main function."""
    if len(sys.argv) < 4:
        print("Usage: python client.py server_host server_port url_path [directory]")
        print("Example: python client.py localhost 8080 /index.html")
        print("Example: python client.py localhost 8080 /document.pdf ./downloads")
        sys.exit(1)
    
    host = sys.argv[1]
    
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be a number")
        sys.exit(1)
    
    url_path = sys.argv[3]
    
    # Ensure path starts with /
    if not url_path.startswith('/'):
        url_path = '/' + url_path
    
    save_directory = sys.argv[4] if len(sys.argv) > 4 else None
    
    print(f"Connecting to {host}:{port}")
    print(f"Requesting: {url_path}")
    print()
    
    try:
        # Send request
        response_data = send_request(host, port, url_path)
        
        # Parse response
        status_code, status_text, headers, body_data = parse_response(response_data)
        
        if status_code is None:
            print("Error: Could not parse server response")
            return
        
        print(f"Status: {status_code} {status_text}")
        print()
        
        # Handle response based on type
        handle_response(status_code, headers, body_data, url_path, save_directory)
    
    except ConnectionRefusedError:
        print(f"Error: Could not connect to {host}:{port}")
        print("Make sure the server is running.")
    except socket.gaierror:
        print(f"Error: Could not resolve host '{host}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()