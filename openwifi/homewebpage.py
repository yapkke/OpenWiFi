import web
import web.webopenid
import openid
import openid.consumer.consumer
import openwifi.webpage as owpage
import openwifi.globals as owglobal
import openwifi.event as owevent
import yapc.log.output as output

urls = (
    r'/openid', 'openwifi.homewebpage.host',
    r'/about', 'openwifi.webpage.about',
    r'/tos', 'openwifi.webpage.tos',
    r'/', 'openwifi.homewebpage.index'
    )


class host(web.webopenid.host):
    def POST(self):
        # unlike the usual scheme of things, the POST is actually called
        # first here
        i = web.input(return_to='/')
        if i.get('action') == 'logout':
            web.webopenid.logout()
            return web.redirect(i.return_to)

        i = web.input('openid', return_to='/')
        i['openid'] = "http://www.google.com/profiles/"+i['openid']
        print i['openid']
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
        <img height=20 src=http://openflow2.stanford.edu:8080/static/google.png />
        <form method="post" action="%s">
        <input type="text" size=30 name="openid" 
         style="background: url(http://openflow2.stanford.edu:8080/static/login-bg.gif) no-repeat; 
         padding-left: 18px; background-position: 0 50%%;" />
        <input type="hidden" name="return_to" value="%s" />
        <button type="submit">log in</button>
        </form>''' % (openid_loc, web.ctx.fullpath)

class index(owpage.index):
    def get_login(self):
        """Get page to login
        """
        body = ""

        body += '''
        <table width=600 border=0>
        <tr><td>%s</td></tr>
        <tr><td>&nbsp</td></tr>
        <tr><td>&nbsp</td></tr>
        ''' % (form('/openid'))

        return body
