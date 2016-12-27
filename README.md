[Demo](http://59.110.139.171:9876/)

markdown编辑器web端。 raw部分的js基本都是模仿[ncornette](https://github.com/ncornette/Python-Markdown-Editor.git )，样式（包括sidebar）仿照马克飞象。

功能:

1. md语法的文档编辑，存档，删除，预览；
2. 与印象笔记同步（沙箱环境）功能完成了，但是拿不到产品环境的API KEY，目前隐藏了这个功能；`markdown_editor.py`中很多看起来复杂的代码都是为了处理这部分逻辑，印象笔记的样式插入只支持inline css，所以需要把以`<link ref=>`方式引用的css转换成inline形式。

requirements:
- tornado
- torndb
- markdown
- Evernote Python SDK（optional）
