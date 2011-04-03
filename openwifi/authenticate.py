import yapc.interface as yapc
import yapc.output as output
import yapc.util.memcacheutil as mcutil
import openwifi.event as owevent

class host_auth(yapc.component):
    """Component that tracks if host is authenticated
    
    @author ykk
    @date Apr 2011
    """
    def __init__(self, server):
        """Initialize
        """
        mcutil.get_client()

        server.register_event_handler(owevent.authenticated.name, self)
        server.register_event_handler(owevent.unauthenticated.name, self)

    def get_key(host):
        """Get host authentication key
        """
        return "%x_authenticated" % host
    get_key = yapc.static_callable(get_key)

    def processevent(self, event):
        """Process authentication event
        """
        if (isinstance(event, owevent.authenticated)):
            output.dbg("%x is authenticated" % event.host,
                       self.__class__.__name__)
            mcutil.set(self.get_key(event.host), True)
        elif (isinstance(event, owevent.unauthenticated)):
            output.dbg("%x is unauthenticated" % event.host,
                       self.__class__.__name__)
            mcutil.set(self.get_key(event.host), False)
            
        return True
