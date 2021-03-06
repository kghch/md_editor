# -*- coding: utf-8 -*-

import os
import re
import time
import threading

import tornado
import tornado.web
import tornado.httpserver
import peewee
import markdown

from OAUTH_GITHUB import *


MARKDOWN_EXT = ('codehilite', 'extra')

checked_pattern1 = re.compile(r'<li>\[(?P<checked>[xX ])\]')
checked_pattern2 = re.compile(r'<li>\n<p>\[(?P<checked>[xX ])\]')
src_pattern = re.compile(r'src="&quot;(?P<src>[^&]*)&quot;"')
xss_pattern1 = re.compile(r'<script>')
xss_pattern2 = re.compile(r'</script>')

DB = peewee.MySQLDatabase('docs', host='127.0.0.1', port=3306, user='root', password='123456')


global_vars = threading.local()
global_vars.login = False
global_vars.user = False


class BaseModel(peewee.Model):
    class Meta:
        database = DB


class Doc(BaseModel):
    id = peewee.IntegerField()
    fid = peewee.IntegerField()
    title = peewee.CharField()
    raw = peewee.TextField()
    html = peewee.TextField()
    created = peewee.DateTimeField()
    updated = peewee.DateTimeField()
    author = peewee.CharField()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', LoginHandler),
            (r'/home', HomeHandler),
            (r'/callback', CallbackHandler),
            (r'/preview', PreviewHandler),
            (r'/create', CreateHandler),
            (r'/save', SaveHandler),
            (r'/delete', DeleteHandler),
            (r'/showpreview/(\d+)', ShowPreviewHandler),
            (r'/mydocs', MydocsHandler),
            (r'/show/(\d+)', ShowByFidHandler)
        ]

        settings = dict(
            editor_title="KGHCH markdown",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            default_handler_class=NotFoundHandler
        )
        super(Application, self).__init__(handlers, **settings)


class PeeweeRequestHandler(tornado.web.RequestHandler):
    def prepare(self):
        DB.connect()
        return super(PeeweeRequestHandler, self).prepare()

    def on_finish(self):
        if not DB.is_closed():
            DB.close()
        return super(PeeweeRequestHandler, self).on_finish()


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        user = self.get_cookie('user')
        if user:
            self.redirect('/home')
        else:
            self.render('login.html')


class HomeHandler(PeeweeRequestHandler):
    def get(self):
        user = self.get_cookie('user', None)
        if user:  
            latest = Doc.select().where(Doc.author == user).order_by(Doc.updated.desc()).limit(1)
            if latest:
                latest = latest[0]
                self.render('home.html', fid=latest.fid, title=latest.title, raw=latest.raw, html=latest.html,
                            created=latest.created, github_name=user)
            else:
                self.render('home.html', fid='0', title='untitled', raw='', html='', created='',github_name=user)
        else:
            self.redirect('/')


class CallbackHandler(PeeweeRequestHandler):
    def get(self):
        code = self.get_argument('code', None)
        try:
            access_token = OauthGithub.get_access_token(code)
        except LoginError, e:
            self.render('error.html', error=e.message)
        else:
            global_vars.login = access_token
            user = OauthGithub.get_user(access_token)
            global_vars.user = user
            self.set_cookie('user', user['login'], expires_days=None)
            self.redirect('/home')


class PreviewHandler(PeeweeRequestHandler):
    def post(self):
        raw_text = self.request.body
        unicode_raw_text = unicode(raw_text, "utf-8")
        md = markdown.Markdown(extensions=MARKDOWN_EXT)
        html_text = md.reset().convert(unicode_raw_text)

        # 支持任务列表
        def convert_checkbox1(match):
            return '<li><input type="checkbox" disabled>' if match.group('checked') == ' ' \
                else '<li><input type="checkbox" disabled checked>'

        def convert_checkbox2(match):
            return '<li>\n<p><input type="checkbox" disabled>' if match.group('checked') == ' ' \
                else '<li>\n<p><input type="checkbox" disabled checked>'

        # 支持img out link
        def convert_src(match):
            return 'src="' + match.group('src') + '"'

        def filter_xss(match):
            return ' '

        pattern_actions = {xss_pattern1: filter_xss,
                        xss_pattern2: filter_xss,
                        checked_pattern1: convert_checkbox1,
                        checked_pattern2: convert_checkbox2,
                        src_pattern: convert_src}
        for pattern, action in pattern_actions.items():
            html_text = re.sub(pattern, action, html_text)

        self.write(html_text)


class CreateHandler(PeeweeRequestHandler):
    def get(self):
        user = self.get_cookie('user', None)
        if user:
            doc = Doc.select().where(Doc.author == user).order_by(Doc.fid.desc()).limit(1)
            if doc:
                doc = doc[0]
                doc_id = doc.fid + 1
            else:
                doc_id = 1
            self.write({'fid': str(doc_id), 'title': 'untitled'})
        else:
            self.redirect('/')


class SaveHandler(PeeweeRequestHandler):
    def post(self):
        user = self.get_cookie('user', None)
        if not user:
            self.redirect('/')
        else:
            data = json.loads(self.request.body)
            origin_title = re.search(r"<h[1-6]>[^<]+</h[1-6]>", data['html'])
            title = origin_title.group(0)[4:-5] if origin_title else "untitled"
            created = ''
            try:
                doc = Doc.get(Doc.fid == int(data['fid']), Doc.author == user)
            except:
                fid = int(data['fid'])
                created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                Doc.create(fid=fid, title=title, raw=data['raw'], html=data['html'], created=created, updated=created, author=user)
            else:
                fid = doc.fid
                updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                doc = Doc.get(Doc.fid == int(fid), Doc.author == user)
                doc.raw = data['raw']
                doc.html = data['html']
                doc.title = title
                doc.updated = updated
                doc.save()

            self.write({"fid": str(fid), "title": title, "created": created})


class DeleteHandler(PeeweeRequestHandler):
    def post(self):
        user = self.get_cookie('user', None)
        if user:
            data = json.loads(self.request.body)
            del_fid = data['delfid']
            cur_fid = data['curfid']
            Doc.delete().where(Doc.fid == int(del_fid), Doc.author == user).execute()
            refresh = 0
            if del_fid == cur_fid:
                refresh = 1
            self.write({'refresh': refresh})

class ShowPreviewHandler(PeeweeRequestHandler):
    def get(self, fid):
        user = self.get_cookie('user', None)
        if user:
            doc = Doc.get(Doc.fid == fid, Doc.author == user)
            if doc:
                self.render('preview.html', fid=fid, html=doc.html, title=doc.title)
            else:
                self.render("error.html", error="The page hasn't been developed yet.")
        else:
            self.redirect('/')


class MydocsHandler(PeeweeRequestHandler):
    def get(self):
        user = self.get_cookie('user', None)
        if not user:
            self.redirect('/')
        else:
            docs = Doc.select().where(Doc.author == user).order_by(Doc.created.desc())
            table_html = self.render_string("docs.html", docs=docs)
            self.write(table_html)


class ShowByFidHandler(PeeweeRequestHandler):
    def get(self, fid):
        user = self.get_cookie('user', None)

        if not user:
            self.redirect('/')
        else:
            try:
                doc = Doc.get(Doc.fid == fid, Doc.author == user)
            except:
                self.render('error.html', error='This page has not been developed yet.')
            else:
                self.render('home.html', fid=fid, title=doc.title, raw=doc.raw, html=doc.html,
                            created=doc.created, github_name=user)

class NotFoundHandler(PeeweeRequestHandler):
    def get(self):
        self.render("error.html", error="The page hasn't been developed yet.")


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(9876)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
