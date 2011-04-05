import dpkt
import yapc.interface as yapc
import yapc.output as output
import yapc.events.openflow as ofevents
import yapc.util.memcacheutil as mcutil
import yapc.forwarding.flows as flows
import openwifi.event as owevent
import openwifi.globals as owglobal

AUTH_DST_IP = 0xab434aef
AUTH_DST_PORT = 8080
AUTH_DST = "openflow2.stanford.edu"
AUTH_TIMEOUT = 30

def host_auth_server(host):
    """Return server host is going to authenticate with
    """
    au = mcutil.get(host_auth.get_auth_key(host))
    if (au == None):
        return None
    else:
        return au

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
        server.register_event_handler(owevent.going_to_auth.name, self)

    def get_key(host):
        """Get host authentication key
        """
        return "%x_authenticated" % host
    get_key = yapc.static_callable(get_key)

    def get_auth_key(host):
        """Get server for host authentication key
        """
        return "%x_authenticated" % host
    get_auth_key = yapc.static_callable(get_auth_key)

    def processevent(self, event):
        """Process authentication event
        """
        if (isinstance(event, owevent.authenticated)):
            output.dbg("%x is authenticated" % event.host,
                       self.__class__.__name__)
            mcutil.set(host_auth.get_key(event.host), event.openid)
        elif (isinstance(event, owevent.unauthenticated)):
            output.dbg("%x is unauthenticated" % event.host,
                       self.__class__.__name__)
            mcutil.set(host_auth.get_key(event.host), None)
        elif (isinstance(event, owevent.going_to_auth)):
            output.dbg("%x is going to authenticate" % event.host,
                       self.__class__.__name__)
            mcutil.set(host_auth.get_auth_key(event.host), event.server(),
                       AUTH_TIMEOUT)

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
            # (4) DNS
            if (host_authenticated(event.match.dl_src) or 
                (event.match.dl_type == dpkt.ethernet.ETH_TYPE_ARP) or 
                (event.match.dl_type == dpkt.ethernet.ETH_TYPE_IP and 
                 event.match.nw_proto == dpkt.ip.IP_PROTO_UDP and
                 (event.match.tp_dst == 67 or 
                  event.match.tp_dst == 68)) or
                (event.match.dl_type == dpkt.ethernet.ETH_TYPE_IP and 
                 event.match.nw_proto == dpkt.ip.IP_PROTO_UDP and
                 event.match.tp_dst == 53)
                ):
                return True

            ##Allow flow to authenticate even when yet authenticated
            

            ##Redirect unauthenticated host if HTTP
            if (event.match.dl_type == dpkt.ethernet.ETH_TYPE_IP and 
                event.match.nw_proto == dpkt.ip.IP_PROTO_TCP and
                event.match.tp_dst == 80):
                if (event.match.nw_dst == AUTH_DST_IP and
                    event.match.tp_dst == AUTH_PORT):
                    return True
                else:
                    owglobal.last_host_redirect = (self.conn.db[event.sock].dpid,
                                                   event.match.dl_src)
                    ##Rewrite ip address to openflow2.stanford.edu
            
            return False

        return True

        
