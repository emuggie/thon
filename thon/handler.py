import cgi, os
from logging import getLogger
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPStatus

logger = getLogger(__name__)

_handleFunction = lambda req, res  : logger.error("handleFunction not initialized :%s", req.path)

def onRequest(on) :
    global _handleFunction
    _handleFunction = on or _handleFunction

class ResourcedHandler(SimpleHTTPRequestHandler) :
    """
    """
    def __init__(self, request, client_address, server, directory):
        self.directory = directory
        self.responseInfo = self.requestInfo = None
        super().__init__(request, client_address, server)

    def translate_path(self, path):
        return os.path.join(self.directory, super().translate_path(path).replace(os.getcwd(),"",1).lstrip("/"))
        
    def list_directory(self, path):
        self.send_error(HTTPStatus.NOT_FOUND,"Listing static resources is restricted.")

    def __getattribute__(self, attr):
        """
        if file exists : do_GET, do_POST
        if file not exists or is directory : do_handle
        """
        if attr.startswith("do_") : 
            path = self.translate_path(self.path)
            if not os.path.exists(path) or os.path.isdir(path) :
                if os.path.exists(path.rstrip("/")+"/index.htm") or os.path.exists(path.rstrip("/")+"/index.html"):
                    return object.__getattribute__(self, attr)
                return object.__getattribute__(self, 'do_handle')

            # default resource response
            return object.__getattribute__(self, "do_handle")
        return object.__getattribute__(self, attr)

    def do_handle(self) :
        self.requestInfo = self.requestInfo if self.requestInfo else RequestInfo(self)
        self.responseInfo = self.responseInfo if self.responseInfo else ResponseInfo(self)
        global _handleFunction
        logger.info("do_handle")
        
        _handleFunction(self.requestInfo, self.responseInfo)
        if not self.responseInfo.isFinished() or not self.wfile.closed() :
            self.responseInfo.finish()
                        
        return None
    
    def finish(self) :
        super().finish()
        # self.response.finish()

class RequestInfo(BaseHTTPRequestHandler) :
    """
    Request data class
    """
    def __init__(self,parent:BaseHTTPRequestHandler) :
        self.command = parent.command
        self.path = parent.path
        self.raw_requestline = parent.raw_requestline
        self.rfile = parent.rfile
        # self.parse_request()
        self.parse_body()
    
    def parse_body(self) :
        if self.command != 'POST' and self.command != 'UPDATE' :
            return
        
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            self.form = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            self.form = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        elif ctype == 'application/json':
            self.json = json.loads(self.rfile.read(length))
    
class ResponseInfo(BaseHTTPRequestHandler) :
    """
    Helper class for easier response
    """
    def __init__(self, parent):
        self.parent = parent
        self.closed = False
        self.headers = {}
        self.status = HTTPStatus.OK

    def isFinished(self)->bool:
        return self.closed

    def finish(self) :
        if self.closed or self.parent.wfile.closed:
            raise
        
        self.parent.send_response_only(self.status)
        for key in self.headers :
            self.parent.send_header(key, self.headers[key])
        self.parent.end_headers()
        # self.wfile.write(self.response.content if type(self.response.content) == bytes else str(self.response.content).encode('utf-8'))
        self.closed = True
        # self.parent.finish()