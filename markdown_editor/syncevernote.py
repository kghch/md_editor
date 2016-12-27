from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types


class Note(object):
    def __init__(self):
        # consumer_key = 'wanghan0307171', consumer_secret = '7ce3360054d137a3'
        self.dev_token = "sandbox key"
        self.app_token = "production key"
        self.client = EvernoteClient(token=self.app_token, sandbox=False)
        self.noteStore = self.client.get_note_store()

    def createEvernote(self, title, html, notebook_guid='d7900482-362b-4424-a698-99c1833fb81c'):
        note = Types.Note()
        #note.notebookGUID = 'd7900482-362b-4424-a698-99c1833fb81c'
        note.notebookGuid = notebook_guid
        note.title = title
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += "<en-note>"
        note.content += html
        note.content += "</en-note>"
        note = self.noteStore.createNote(note)
        return note

    def updateNote(self, note_guid, title, html):
        note = self.noteStore.getNote(note_guid, False, False, False, False)
        note.title = title
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += "<en-note>"
        note.content += html
        note.content += "</en-note>"
        note = self.noteStore.updateNote(note)
        return note


def test():
    html = """This is evening.
    """
    #guid = "d7900482-362b-4424-a698-99c1833fb81c"
    note = Note().createEvernote("evening test", html)
    print note.guid
    html_new = """
    <blockquote style="border-left:4px solid #DDD;padding:0 15px;color:#777">
    <p>This is a quote.</p>
    </blockquote>
    """
    Note().updateNote(note.guid, 'Evening Update test', html_new)


if __name__ == "__main__":
    test()