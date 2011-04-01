import web
import web.webopenid
import yapc.interface as yapc
import yapc.output as output

urls = (
    r'/openid', 'web.webopenid.host',
    r'/', 'openwifi.webpage.index'
    )

class cleanup(yapc.cleanup):
    def __init__(self, server):
        server.register_cleanup(self)

    def cleanup(self):
        output.dbg("Cleanup webpy", self.__class__.__name__)
        raise KeyboardInterrupt

class index:
    def GET(self):
        body = '''
        <html><head><title>Open WiFi: Towards Access Everywhere...</title></head>
        <body>
        %s
        ''' % (web.webopenid.form('/openid'))

        body += '''
        </body>
        </html>
        '''
        
        return body
