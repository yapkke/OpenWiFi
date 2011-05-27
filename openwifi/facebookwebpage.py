import web

urls = (
    r'/about', 'openwifi.webpage.about',
    r'/tos', 'openwifi.webpage.tos',
    r'/', 'openwifi.facebookwebpage.index'
    )

render = web.template.render('templates/')

class index:
    """Index page
    
    @author ykk
    @date Mar 2011
    """
    def GET(self):
        """Response to get
        """
        return render.facebook()
