# -*- coding: utf-8 -*-

import os
import json
import re

import tornado
import tornado.web
import tornado.httpserver
import torndb
import markdown

# todo: 使用ORM(peewee)

MARKDOWN_EXT = ('codehilite', 'extra')

checked_pattern = re.compile(r'<li>\[(?P<checked>[xX ])\]')
img_pattern = re.compile(r'(?P<alttext><img alt="[^"]*")')
src_pattern = re.compile(r'src="&quot;(?P<src>[^&]*)&quot;"')

db = torndb.Connection(host='127.0.0.1:3306', database='docs', user='root', password='123456')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
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
            debug=True,
            default_handler_class=NotFoundHandler
        )
        super(Application, self).__init__(handlers, **settings)


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        latest = db.get("SELECT * FROM doc ORDER BY updated DESC LIMIT 1")
        if latest:
            self.render('home.html', fid=latest['fid'], title=latest['title'], raw=latest['raw'], html=latest['html'],
                        created=latest['created'])
        else:
            self.render('home.html', fid='0', title='untitled', raw='', html='')


class PreviewHandler(tornado.web.RequestHandler):
    def post(self):
        raw_text = self.request.body
        unicode_raw_text = unicode(raw_text, "utf-8")
        md = markdown.Markdown(extensions=MARKDOWN_EXT)
        html_text = md.reset().convert(unicode_raw_text)

        # 支持任务列表
        def convert_checkbox(match):
            return '<li><input type="checkbox" disabled>' if match.group('checked') == ' ' \
                else '<li><input type="checkbox" disabled checked>'

        # 限制插入图片长宽
        def convert_img(match):
            return match.group('alttext') + ' width=200, height=200'

        # 支持img out link
        def convert_src(match):
            return 'src="' + match.group('src') + '"'

        html_text = re.sub(checked_pattern, convert_checkbox, html_text)
        html_text = re.sub(img_pattern, convert_img, html_text)
        html_text = re.sub(src_pattern, convert_src, html_text)

        self.write(html_text)


class CreateHandler(tornado.web.RequestHandler):
    def get(self):
        doc = db.get("SELECT * FROM doc ORDER BY fid DESC LIMIT 1")
        if doc:
            doc_id = doc['fid'] + 1
        else:
            doc_id = 1
        self.write({'fid': str(doc_id), 'title': 'untitled'})


class SaveHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        doc = db.get("SELECT * FROM doc WHERE fid=%s", int(data['fid']))
        origin_title = re.search(r"<h[1-6]>[^<]+</h[1-6]>", data['html'])
        title = origin_title.group(0)[4:-5] if origin_title else "untitled"

        if doc:
            fid = doc['fid']
            db.execute("UPDATE doc set raw=%s, html=%s, title=%s, updated=UTC_TIMESTAMP() WHERE fid=%s", \
                       data['raw'], data['html'], title, int(fid))
        else:
            fid = int(data['fid'])
            db.execute("""INSERT INTO doc(fid, title, raw, html, created, updated)
            VALUES(%s, %s, %s, %s, UTC_TIMESTAMP(), UTC_TIMESTAMP())""", fid, title, data['raw'], data['html'])

        self.write({"fid": str(fid), "title": title})


class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        del_fid = data['delfid']
        cur_fid = data['curfid']
        db.execute("DELETE FROM doc WHERE fid=%s", int(del_fid))
        refresh = 0
        if del_fid == cur_fid:
            refresh = 1
        self.write({'refresh': refresh})


class ShowPreviewHandler(tornado.web.RequestHandler):
    def get(self, fid):
        doc = db.get("SELECT * FROM doc WHERE fid=%s", fid)
        if doc:
            self.render('preview.html', fid=fid, html=doc['html'], title=doc['title'])
        else:
            self.render("error.html", error="The page hasn't been developed yet.")


class MydocsHandler(tornado.web.RequestHandler):
    def get(self):
        docs = db.query("SELECT * FROM doc ORDER BY created DESC")
        for doc in docs:
            doc['updated'] = doc['updated'].strftime("%Y-%m-%d %H:%M:%S")
            doc['created'] = doc['created'].strftime("%Y-%m-%d %H:%M:%S")
        table_html = self.render_string("docs.html", docs=docs)
        self.write(table_html)


class ShowByFidHandler(tornado.web.RequestHandler):
    def get(self, fid):
        doc = db.get("SELECT * FROM doc WHERE fid=%s", fid)
        if doc:
            self.render('home.html', fid=fid, title=doc['title'], raw=doc['raw'], html=doc['html'],
                        created=doc['created'])
        else:
            self.render("error.html", error="The page hasn't been developed yet.")


class NotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("error.html", error="The page hasn't been developed yet.")


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(9876)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
