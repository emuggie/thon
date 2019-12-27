import pserver, pserver.handler

print("start server")
def onReq(req, res) :
    print("request", req.command,req.path)
    
pserver.handler.onRequest(onReq)
pserver.test(static="/home/emuggie/dev/workspace/VisualStudioCode/python/pworm/demo/routes")