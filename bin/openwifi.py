#!/usr/bin/python

import web
import web.webopenid

urls = (
        r'/openid', 'web.webopenid.host',
        r'/', 'Index'
    )

app = web.application(urls, globals())

class Index:
    def GET(self):
        body = '''
        <html><head><title>Web.py OpenID Test</title></head>
        <body>
        %s
        </body>
        </html>
        ''' % (web.webopenid.form('/openid'))
        
        return body

if __name__ == "__main__": app.run()
