import http.server
import socketserver

# Define the port
PORT = 8001

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS header to allow all origins
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    # Use the custom handler
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"Serving at port {PORT} with CORS enabled")
        httpd.serve_forever()
