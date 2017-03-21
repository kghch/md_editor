
## online markdown editor

[Try Demo here.](http://59.110.139.171)

### Features

- Github OAuth2.0 login
- Notes archive and preview
- Export to PDF
- ~~Synchronize with Evernote~~

### Preview

![Show My Docs](https://ooo.0o0.ooo/2017/03/21/58d0e04940d22.png)

### Requirements

- tornado
- markdown
- requests
- peewee

### Attention

The sidebar style is inspired by [maxiang.io](http://maxiang.io), the markdown css style copies from [ncornette](https://github.com/ncornette/Python-Markdown-Editor.git )

### Usage

1. MySQL database and tables prepared
2. Apply for a github OAuth application [here](https://github.com/settings/developers) and configure `CLIENT_ID` and `CLIENT_SECRET` in `OAUTH_GITHUG.PY`
3. Run `python md_editor.py`


### Todo:
- [ ] Input box's highlighting
- [x] Pictures syntax in markdown
- [x] Todo lists syntax in markdown
- [x] Export to PDF
- [ ] Multiple color themes 
- [ ] Scrollbar synchronization