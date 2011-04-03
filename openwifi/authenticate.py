import yapc.interface as yapc
import yapc.output as output
import yapc.events.openflow as ofevents
import yapc.util.memcacheutil as mcutil
import openwifi.event as owevent

def host_authenticated(host):
    """Return if host is authenticated
    """
    au = mcutil.get(host_auth.get_key(host))
    if (au == None):
        return False
    else:
        return True

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
            mcutil.set(self.get_key(event.host), event.openid)
        elif (isinstance(event, owevent.unauthenticated)):
            output.dbg("%x is unauthenticated" % event.host,
                       self.__class__.__name__)
            mcutil.set(self.get_key(event.host), None)
            
        return True

class redirect(yapc.component):
    """Class to redirect unauthenticate host for authentication
    
    @author ykk
    @date Apr 2011
    """
    def __init__(self, server, conn):
        """Initialize
        """
        server.register_event_handler(ofevents.pktin.name, self)
        self.conn = conn

    def processevent(self, event):
        """Process event
        """
        if (isinstance(event, ofevents.pktin)):
            ##Allow 
            # (1) authenticated host
            # (2) ARP
            # (3) DHCP
            if (host_authenticated(event.match.dl_src) or 
                (event.match.dl_type == 0x0806) or 
                (event.match.dl_type == 0x0800 and 
                 event.match.nw_proto == 17 and
                 (event.match.tp_dst == 67 or 
                  event.match.tp_dst == 68))
                ):
                return True
 
            ##Redirect unauthenticated host if HTTP
            return False

        return True
