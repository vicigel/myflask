from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
from app import create_app


class MainHanlder(RequestHandler):
    def get(self):
        self.write("This message comes from Tornado ^_^ ")


tr = WSGIContainer(create_app('default'))


application = Application([
    (r"/tornado", MainHanlder),
    (r".*", FallbackHandler, dict(fallback=tr))
])


if __name__ == "__main__":
    application.listen(8080, address='0.0.0.0')
    IOLoop.instance().start()