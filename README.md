[Demo](http://59.110.139.171:9876/)

markdown编辑器web端。
样式（包括sidebar）仿照马克飞象；markdown语法的渲染格式抄袭[ncornette](https://github.com/ncornette/Python-Markdown-Editor.git )

功能:

1. md语法的文档编辑，存档，删除，预览；
2. 与印象笔记（沙箱环境）同步，这部分功能放在`markdown_editor.py`和`inlinecss.py`和`syncevernote.py`中；

requirements:
- tornado
- torndb
- markdown
- Evernote Python SDK（optional，不打算做和印象笔记的同步了，没有去申请产品环境的KEY）

运行方式:

`python md_editor.py`

todo:
- []输入框文字装饰
- []图片支持
- [x]任务列表
- [x]导出pdf
- []主题切换
