import http.server, time, threading, asyncio, cgi, os,urllib.parse,posixpath,json
from urllib.parse import urlparse
from  concurrent.futures import ThreadPoolExecutor
from functools import partial
import multiprocessing as mp

from sys import platform
from logging import getLogger
from .handler import ResourcedHandler

logger = getLogger(__name__)

executor = ThreadPoolExecutor()
mp.set_start_method('fork')

class ExtendedHttpServer(http.server.HTTPServer) :
    async def process_request_async(self, request, client_address) :
        logger.debug("Begin Handle Request : ", client_address, request)
        try:
            super().process_request(request, client_address)
        except:
            super().handle_error(request, client_address)
            super().shutdown_request(request)
        logger.debug("End Handle Request : ", client_address, request)

    # Override process_request to delegate execution to threads
    def process_request(self, request, client_address):
        loop = getattr(asyncio,'get_running_loop', asyncio.get_event_loop)()
        loop.run_until_complete(self.process_request_async(request, client_address))
        # loop.run_in_executor(executor, self.process_request_async, request, client_address)
        # executor.submit(self.process_request_thread, request, client_address)

def run(host = "127.0.0.1", port = 5000, static = os.getcwd(), handler = ResourcedHandler, interval = 0.5) :
    httpd = ExtendedHttpServer((host,port),partial(handler, directory = static))
    logger.info("Server :",host, ":", port, "interval : ", interval, ', pid ', os.getpid())

    # Multiprocess using fork.
    if platform.startswith("linux") :
        mp.Process(target=httpd.serve_forever,args=(interval,)).start()
    # mp.Process(target=httpd.serve_forever,args=interval).start()
    # mp.Process(target=httpd.serve_forever,args=interval).start()
    httpd.serve_forever(interval)

def test(host = "127.0.0.1", port = 5000, static = os.getcwd(), handler = ResourcedHandler, interval = 0.5) :
    """
    Test function for development stage.
    """
    logger.info("Server :",host, ":", port, "interval : ", interval, ', pid ', os.getpid())
    http.server.HTTPServer((host,port), partial(handler, directory = static)).serve_forever(interval)