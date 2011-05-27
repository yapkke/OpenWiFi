import web
import webfb.facebook as fb
import openwifi.webpage as owpage
import openwifi.globals as owglobal
import openwifi.event as owevent
import yapc.log.output as output

urls = (
    r'/about', 'openwifi.webpage.about',
    r'/tos', 'openwifi.webpage.tos',
    r'/', 'openwifi.facebookwebpage.index',
    r'/fb', 'openwifi.facebookwebpage.login',
    r'/welcome', 'openwifi.facebookwebpage.welcome'
    )

class welcome:
    def POST(self):
        uname = str(web.input()['userName'])
        a = owevent.authenticated(owglobal.session.datapath,
                                  owglobal.session.host,
                                  "Facebook:"+uname)
        owglobal.server.post_event(a)
        output.dbg(str(owglobal.session.host)+\
                       " is authenticated with %s" % uname, 
                   self.__class__.__name__)
       
        return '''
        <html><head><title>Open WiFi: Towards Access Everywhere...</title></head>
        <body>
        <center>
        <h2>Welcome to OpenWiFi<sup>&alpha</sup>!</h2>
        <h4>A Stanford Research Project</h4>
        <table align=centerwidth=600 border=0>        
        <td><tr>Hi %s, hope you will enjoy OpenWiFi!
        </td></tr>
        <tr><td>&nbsp</td></tr>
        <tr><td>&nbsp</td></tr>
        <tr><td>
        <a href="about">About OpenWiFi</a>&nbsp&nbsp
        <a href="tos">Terms of Service</a>.
        </td></tr>
        </table>   
        </center>
        </body>
        </html>
''' % uname

class login(fb.login):
    def GET(self):
        going = owevent.going_to_auth(owglobal.session.datapath,
                                      owglobal.session.host,
                                      "facebook")
        owglobal.server.post_event(going)
        output.dbg(str(owglobal.session.host)+\
                       " is going to "+going.server()+" to authenticate",
                   self.__class__.__name__)
        return fb.login.GET(self)

class index(owpage.index):
    def get_login(self):
        """Get page to login
        """
        body = ""

        body += '''
        <table align=centerwidth=600 border=0>
        <tr><td align=center>%s</td></tr>
        <tr><td>&nbsp</td></tr>
        <tr><td>&nbsp</td></tr>
        ''' % fb.login_form()

        return body
