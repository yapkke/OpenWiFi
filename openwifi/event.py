import yapc.interface as yapc

class going_to_auth(yapc.event):
    """Event thrown when host is going to url to authenticate

    @author ykk
    @date Apr 2011
    """
    def __init__(self, datapathid, host, url):
        """Initialize
        """
        self.datapathid = datapathid
        self.host = host
        self.url = url

    def server(self):
        """Return domain name
        """
        st = self.url.find('//')
        url = self.url[st+2:]
        en = url.find('/')
        server = url[:en]
        en = server.rfind('.')
        st = server.rfind('.', 0, en)
        return server[st+1:]

class unauthenticated(yapc.event):
    """Event thrown when host is unauthenticated
   
    @author ykk
    @date Apr 2011
    """
    name = "Host Unauthenticated Event"
    def __init__(self, datapathid, host):
        """Initialize
        """
        self.datapathid = datapathid
        self.host = host

class authenticated(unauthenticated):
    """Event thrown when host is authenticated
   
    @author ykk
    @date Apr 2011
    """
    name = "Host Authenticated Event"
    def __init__(self, datapathid, host, openid):
        """Initialize
        """
        unauthenticated.__init__(self, datapathid, host)
        self.openid = openid
