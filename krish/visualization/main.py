from http.server import HTTPServer, SimpleHTTPRequestHandler

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = 'index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    PORT = 8000
    server = HTTPServer(('', PORT), Handler)
    print('Server running on port %s' % PORT)
    server.serve_forever()
