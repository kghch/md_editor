import json
import requests

CLIENT_ID = 'f0e82131f29cf4177970'
CLIENT_SECRET = ''
URL_ACCESS_TOKEN = 'https://github.com/login/oauth/access_token'
URL_GET_USER = 'https://api.github.com/user'


class LoginError(Exception):
    def __init__(self, message):
        super(LoginError, self).__init__()
        self.message = message


class OauthGithub(object):

    @staticmethod
    def get_access_token(code):
        payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code
        }
        res = requests.post(URL_ACCESS_TOKEN, data=payload)
        if res.status_code != 200:
            raise LoginError('Login Error with Github.')

        return res.content

    @staticmethod
    def get_user(access_token):
        rep = requests.get('%s?%s' % (URL_GET_USER, access_token))
        user = json.loads(rep.content)
        return user

