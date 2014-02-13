# -*- coding: utf-8 -*-

import os
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.process
import tornado.options
import tornado.log
import tornado.escape
import tornado.httputil

import momoko

import psycopg2
import psycopg2.extras

from tornado.options import options
from tornado.options import define

## ┏━┓┏━┓╺┳╸╻┏━┓┏┓╻┏━┓
## ┃ ┃┣━┛ ┃ ┃┃ ┃┃┗┫┗━┓
## ┗━┛╹   ╹ ╹┗━┛╹ ╹┗━┛

def config_callback(path):
    options.parse_config_file(path, final=False)

define('config', type=str, help='Path to config file', callback=config_callback, group='Config file')

define('debug', default=False, help='Debug', type=bool, group='Application')

define('cookie_secret', type=str, group='Cookies')
define('cookie_domain', type=str, group='Cookies')

define('listen_port', default=8000, help='Listen Port', type=int, group='HTTP Server')
define('listen_host', default='localhost', help='Listen Host', type=str, group='HTTP Server')

define('postgresql_dsn', default='dbname=pglet', type=str, group='PostgreSQL')

## ┏┓ ┏━┓┏━┓┏━╸╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┣┻┓┣━┫┗━┓┣╸ ┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛╹ ╹┗━┛┗━╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, **kwargs):

        super(BaseHandler, self).initialize(**kwargs)

        self.kwargs = kwargs

    @property
    def db(self):
        return self.application.db

    @tornado.gen.coroutine
    def prepare(self):
        pass

    def get_template_namespace(self):
        namespace = super(BaseHandler, self).get_template_namespace()

        #namespace.update({
        #    'page_copyright': self.settings.get('page_copyright'),
        #    'page_title_prefix': self.settings.get('page_title_prefix'),
        #    'page_title': '',
        #})

        return namespace

## ┏━┓┏━┓┏━╸┏━╸┏━╸┏━┓┏━┓┏━┓┏━┓╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┣━┛┣━┫┃╺┓┣╸ ┣╸ ┣┳┛┣┳┛┃ ┃┣┳┛┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ╹  ╹ ╹┗━┛┗━╸┗━╸╹┗╸╹┗╸┗━┛╹┗╸╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class PageErrorHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.send_error(self.kwargs['error'])

    def post(self, *args, **kwargs):
        self.send_error(self.kwargs['error'])

## ┏━┓╺┳╸╻ ╻┏┓ ╻ ╻┏━┓┏┓╻╺┳┓╻  ┏━╸┏━┓
## ┗━┓ ┃ ┃ ┃┣┻┓┣━┫┣━┫┃┗┫ ┃┃┃  ┣╸ ┣┳┛
## ┗━┛ ╹ ┗━┛┗━┛╹ ╹╹ ╹╹ ╹╺┻┛┗━╸┗━╸╹┗╸

class StubHandler(BaseHandler):
    def check_xsrf_cookie(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        self.write(dict(self.request.headers))

    def head(self, *args, **kwargs):
        self.write('')

    def post(self, *args, **kwargs):
        self.write(self.request.body)

    def patch(self, *args, **kwargs):
        self.write('')

    def delete(self, *args, **kwargs):
        self.write('')

    def options(self, *args, **kwargs):
        self.write('')

## ┏┳┓┏━┓╻┏┓╻
## ┃┃┃┣━┫┃┃┗┫
## ╹ ╹╹ ╹╹╹ ╹

def main():
    tornado.options.parse_command_line()

    ## ┏━┓┏━╸╺┳╸╺┳╸╻┏┓╻┏━╸┏━┓
    ## ┗━┓┣╸  ┃  ┃ ┃┃┗┫┃╺┓┗━┓
    ## ┗━┛┗━╸ ╹  ╹ ╹╹ ╹┗━┛┗━┛

    code_path = os.path.dirname(__file__)
    static_path = os.path.join(code_path, 'static')
    template_path = os.path.join(code_path, 'templates')
    support_path = os.path.join(code_path, 'support')

    settings = dict(
        gzip = True,
        static_path = static_path,
        template_path = template_path,
        support_path = support_path,
        xsrf_cookies = True,
        **options.as_dict()
    )

    tornado.log.gen_log.debug(settings)

    ## ┏━┓┏━┓┏━┓╻  ╻┏━╸┏━┓╺┳╸╻┏━┓┏┓╻
    ## ┣━┫┣━┛┣━┛┃  ┃┃  ┣━┫ ┃ ┃┃ ┃┃┗┫
    ## ╹ ╹╹  ╹  ┗━╸╹┗━╸╹ ╹ ╹ ╹┗━┛╹ ╹

    handlers = [
        tornado.web.url(r'/static/(css/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        tornado.web.url(r'/static/(ico/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        tornado.web.url(r'/static/(img/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        tornado.web.url(r'/static/(js/.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        tornado.web.url(r'/__stub__$', StubHandler),
        tornado.web.url(r'/(.*)', PageErrorHandler, kwargs=dict(error=404)),
    ]

    application = tornado.web.Application(handlers=handlers, **settings)

    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)

    if options.debug:
        http_server.listen(options.listen_port, address=options.listen_host)
    else:
        http_server.bind(options.listen_port, address=options.listen_host)
        http_server.start(0)

    application.dsn = options.postgresql_dsn

    application.db = momoko.Pool(
        dsn=options.postgresql_dsn,
    )

    loop = tornado.ioloop.IOLoop.instance()

    try:
        loop_status = loop.start()
    except KeyboardInterrupt:
        loop_status = loop.stop()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass

