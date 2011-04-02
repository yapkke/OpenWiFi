import web
import web.webopenid
import yapc.interface as yapc
import yapc.output as output

urls = (
    r'/openid', 'web.webopenid.host',
    r'/', 'openwifi.webpage.index'
    )

class cleanup(yapc.cleanup):
    """Component to terminate webpy
    
    @author ykk
    @date Apr 2011
    """
    def __init__(self, server):
        """Register cleanup
        """
        server.register_cleanup(self)

    def cleanup(self):
        """Stop webpy through keyboard interrupt
        """
        output.dbg("Cleanup webpy", self.__class__.__name__)
        raise KeyboardInterrupt

def form(openid_loc):
    oid = web.webopenid.status()
    if oid:
        return '''
        <form method="post" action="%s">
          <img src="http://openid.net/login-bg.gif" alt="OpenID" />
          <strong>%s</strong>
          <input type="hidden" name="action" value="logout" />
          <input type="hidden" name="return_to" value="%s" />
          <button type="submit">log out</button>
        </form>''' % (openid_loc, oid, web.ctx.fullpath)
    else:
        return '''
        <form method="post" action="%s">
        <input type="text" size=80 name="openid" 
         value="http://www.google.com/profiles/" 
         style="background: url(http://openid.net/login-bg.gif) no-repeat; 
         padding-left: 18px; background-position: 0 50%%;" />
        <input type="hidden" name="return_to" value="%s" />
        <button type="submit">log in</button>
        </form>''' % (openid_loc, web.ctx.fullpath)

class index:
    """Index page
    
    @author ykk
    @date Mar 2011
    """
    def __init__(self):
        output.dbg("Created", self.__class__.__name__)
    
    def GET(self):
        """Response to get
        """
        oid = web.webopenid.status()
        body = '''
        <html><head><title>Open WiFi: Towards Access Everywhere...</title></head>
        <body>
        '''

        if oid:
            body += self.get_logout()
        else:
            body += self.get_login()

        body += '''
        <br>
        </td></tr>
        <tr><td>
        Empowered by 
        <img height=24px src="http://www.openflow.org/img/newlogo5.png">
        </td></tr>
    
        </table>
        </body>
        </html>
        '''
        
        return body

    def get_login(self):
        """Get page to login
        """
        body = ""

        body += '''
        <table width=600 border=0><tr><td>
OpenWiFi aims to facilitate widesread availability of free and open wireless access.  If you have arrived here while logging into a wireless network, you can use this network by simply logging in using your <a target=_new_ href="http://openid.net/">OpenID</a> here.  This access is provided as part of a research experiment.  By using this network, you agree for your session information to be used for research purposes.  The researchers involved would act in good faith to protect your identity when publishing results.  You will, of course, also responsible for any of your actions while using this network.
        <br><br></td></tr>
        '''

        body += '''<tr><td>
        If you agree to the above terms and condition, 
        you can login with your OpenID here:<br>
        %s
        </td></tr>
        <tr><td>
        e.g., for user <i>IUseOpenWiFi</i>,<br>
        
        ''' % (form('/openid'))

        body += '''
        Google OpenID url is 
        <b>http://www.google.com/profiles/<i>IUseOpenWiFi</i></b><br>
        '''

        body += '''
        Yahoo OpenID url is 
        <b>https://me.yahoo.com/<i>IUseOpenWiFi</i></b><br>
        '''

        return body

    def get_logout(self):
        """Get page to logout
        """
        body = ""

        body += '''<tr><td>
        You are logged in as<br>
        %s
        </td></tr>
        <tr><td>  
        ''' % (form('/openid'))

        return body
