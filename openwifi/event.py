import yapc.interface as yapc

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
