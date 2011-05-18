import web
import web.webopenid
import openid.consumer.consumer
import openwifi.globals as owglobal
import openwifi.event as owevent
import yapc.interface as yapc
import yapc.log.output as output

urls = (
    r'/openid', 'openwifi.webpage.host',
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

class host(web.webopenid.host):
    def POST(self):
        # unlike the usual scheme of things, the POST is actually called
        # first here
        i = web.input(return_to='/')
        if i.get('action') == 'logout':
            web.webopenid.logout()
            return web.redirect(i.return_to)

        i = web.input('openid', return_to='/')
        going = owevent.going_to_auth(owglobal.session.datapath,
                                      owglobal.session.host,
                                      i['openid'])
        owglobal.server.post_event(going)
        output.dbg(str(owglobal.session.host)+\
                       " is going to "+going.server()+" to authenticate",
                   self.__class__.__name__)

        n = web.webopenid._random_session()
        web.webopenid.sessions[n] = {'webpy_return_to': i.return_to}
        
        c = openid.consumer.consumer.Consumer(web.webopenid.sessions[n], 
                                              web.webopenid.store)
        a = c.begin(i.openid)
        f = a.redirectURL(web.ctx.home, web.ctx.home + web.ctx.fullpath)

        web.setcookie('openid_session_id', n)
        return web.redirect(f)

def form(openid_loc):
    oid = web.webopenid.status()
    if oid:
        return '''
        <form method="post" action="%s">
          <img src="http://openflow2.stanford.edu:8080/static/login-bg.gif" alt="OpenID" />
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
         style="background: url(http://openflow2.stanford.edu:8080/static/login-bg.gif) no-repeat; 
         padding-left: 18px; background-position: 0 50%%;" />
        <input type="hidden" name="return_to" value="%s" />
        <button type="submit">log in</button>
        </form>''' % (openid_loc, web.ctx.fullpath)

class index:
    """Index page
    
    @author ykk
    @date Mar 2011
    """
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
            a = owevent.authenticated(owglobal.session.datapath,
                                      owglobal.session.host,
                                      oid)
            owglobal.server.post_event(a)
            output.dbg(str(owglobal.session.host)+\
                           " is authenticated with %s" % oid, 
                       self.__class__.__name__)
        else:
            if (owglobal.session.datapath == None or
                (not isinstance(owglobal.session.datapath, list))):
                owglobal.session.datapath = owglobal.last_host_redirect[0]
                owglobal.session.host = owglobal.last_host_redirect[1]
            body += self.get_login()
            u = owevent.unauthenticated(owglobal.session.datapath,
                                        owglobal.session.host)
            owglobal.server.post_event(u)            

        body += '''
        <br>
        </td></tr>
        <tr><td>
        Empowered by 
        <img height=24px src="http://openflow2.stanford.edu:8080/static/newlogo5.png">
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
OpenWiFi is a research project that helps others provide free WiFi access. The researchers involved would act in good faith to protect your identity and privacy.
</td></tr><tr><td>
By using this network, you agree 
<ul>
<li>for your network information to be used for research purposes, and </li>
<li>be responsible for your actions while using this network.</li>
</ul>
</td></tr><tr><td>
If you have arrived here while logging into a wireless network, you can use this network by simply logging in using your OpenID here:
</td></tr>
        '''

        body += '''<tr><td>
        %s
        </td></tr>
        <tr><td>
        e.g., for user <i>IUseOpenWiFi</i>,<br>
        
        ''' % (form('/openid'))

        body += '''
        Google OpenID url is 
        <b><a href="http://google.com">http://www.google.com/</a>profiles/<i>IUseOpenWiFi</i></b><br>
        '''

        body += '''
        Yahoo OpenID url is 
        <b><a href="http://www.yahoo.com">https://me.yahoo.com/</a><i>IUseOpenWiFi</i></b><br>
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
