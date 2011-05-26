import dpkt
import yapc.interface as yapc
import yapc.log.output as output
import yapc.pyopenflow as pyof
import yapc.events.openflow as ofevents
import yapc.util.memcacheutil as mcutil
import yapc.util.parse as pu
import yapc.forwarding.flows as flows
import yapc.netstate.swhost as swhost
import openwifi.event as owevent
import openwifi.globals as owglobal

AUTH_DST_IP = pu.ip_string2val("171.67.74.237")
AUTH_DST_PORT1 = 80
AUTH_DST_PORT2 = 8080
HTTPS_PORT = 443

AUTH_TIMEOUT = 120
MAX_AUTH_TIMEOUT = 3600 #One hour

#BYPASS_IP = [pu.ip_string2val("140.211.166.152")]
BYPASS_IP = []

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
        return pu.array2hex_str(host)+"_authenticated"
    get_key = yapc.static_callable(get_key)

    def get_auth_key(host):
        """Get server for host authentication key
        """
        return pu.array2hex_str(host)+"_auth_server"
    get_auth_key = yapc.static_callable(get_auth_key)

    def processevent(self, event):
        """Process authentication event
        """
        if (event.host == None):
            return True

        if (isinstance(event, owevent.authenticated)):
            output.dbg(pu.array2hex_str(event.host)+" is authenticated",
                       self.__class__.__name__)
            mcutil.set(host_auth.get_key(event.host), event.openid, MAX_AUTH_TIMEOUT)
        elif (isinstance(event, owevent.unauthenticated)):
            output.dbg(pu.array2hex_str(event.host)+" is unauthenticated",
                       self.__class__.__name__)
            mcutil.delete(host_auth.get_key(event.host))
            mcutil.delete(host_auth.get_auth_key(event.host))
        elif (isinstance(event, owevent.going_to_auth)):
            output.dbg(pu.array2hex_str(event.host)+" is going to authenticate",
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
            ##Allow flow to authenticate even when yet authenticated
            if ((event.match.nw_dst == AUTH_DST_IP and
                 (event.match.tp_dst == AUTH_DST_PORT1 or event.match.tp_dst == AUTH_DST_PORT2)) or
                (event.match.nw_src == AUTH_DST_IP and
                 (event.match.tp_src == AUTH_DST_PORT1 or event.match.tp_src == AUTH_DST_PORT2))):
                if (event.match.nw_dst == AUTH_DST_IP and event.match.tp_dst == 8080):
                    owglobal.last_host_redirect = (self.conn.db[event.sock].dpid,
                                                   event.match.dl_src)
                output.dbg("Approving "+\
                               pu.ip_val2string(event.match.nw_src) + ":"+str(event.match.tp_src)+\
                               "=>"+\
                               pu.ip_val2string(event.match.nw_dst) + ":"+str(event.match.tp_dst),
                           self.__class__.__name__)
                return True

            #Authenticated host
            if (host_authenticated(event.match.dl_src) or 
                host_authenticated(event.match.dl_dst)):
                output.vdbg("Authenticated host flow "+\
                                pu.ip_val2string(event.match.nw_src) + ":"+str(event.match.tp_src)+\
                                "=>"+\
                                pu.ip_val2string(event.match.nw_dst) + ":"+str(event.match.tp_dst),
                            self.__class__.__name__)
                return True

            ##Allow special website access without authentication
            if (event.match.nw_dst in BYPASS_IP or
                event.match.nw_src in BYPASS_IP):
                output.dbg("Allow bypass for special server",
                           self.__class__.__name__)
                return True

            ##Allow 
            # (1) ARP
            # (2) ICMP
            # (3) DHCP
            # (4) DNS
            if ((event.match.dl_type == dpkt.ethernet.ETH_TYPE_ARP) or 
                (event.match.dl_type == dpkt.ethernet.ETH_TYPE_IP and
                 event.match.nw_proto == dpkt.ip.IP_PROTO_ICMP) or 
                (event.match.dl_type == dpkt.ethernet.ETH_TYPE_IP and 
                 event.match.nw_proto == dpkt.ip.IP_PROTO_UDP and
                 (event.match.tp_dst == 67 or 
                  event.match.tp_dst == 68)) or
                (event.match.dl_type == dpkt.ethernet.ETH_TYPE_IP and 
                 event.match.nw_proto == dpkt.ip.IP_PROTO_UDP and
                 (event.match.tp_dst == 53 or event.match.tp_src == 53))):
                return True

            ##Allow route to OpenID provider (should be in HTTPS)
            if (event.match.tp_dst == HTTPS_PORT or 
                event.match.tp_dst == 8080 or 
                event.match.tp_dst == 80 or
                event.match.tp_src == HTTPS_PORT or 
                event.match.tp_src == 8080 or 
                event.match.tp_src == 80):
                auth_s = None
                if (event.match.tp_dst == HTTPS_PORT or 
                    event.match.tp_dst == 8080 or 
                    event.match.tp_dst == 80):
                    auth_s = mcutil.get(host_auth.get_auth_key(event.match.dl_src))
                else:
                    auth_s = mcutil.get(host_auth.get_auth_key(event.match.dl_dst))

                if (auth_s != None):
                    output.dbg(pu.ip_val2string(event.match.nw_dst)+" associated with "+\
                                   " auth server "+str(auth_s)+" "+str(event.match.dl_src),
                               self.__class__.__name__)
                    return True
                
            ##Redirect unauthenticated host if HTTP
            if (event.match.dl_type == dpkt.ethernet.ETH_TYPE_IP and 
                event.match.nw_proto == dpkt.ip.IP_PROTO_TCP and
                (event.match.tp_dst == 80 or event.match.tp_dst == 8080)):
                output.dbg("Redirecting %x to authenticate" % pu.array2val(event.match.dl_src),
                           self.__class__.__name__)

                #Forward flow
                flow = flows.exact_entry(event.match)
                key = swhost.mac2sw_binding.get_key(event.sock,
                                                    event.match.dl_dst)
                port = mcutil.get(key)
                if (port != None):
                    flow.set_buffer(event.pktin.buffer_id)
                    flow.add_nw_rewrite(False, AUTH_DST_IP)
                    flow.add_output(port)
                    self.conn.send(event.sock,flow.get_flow_mod(pyof.OFPFC_MODIFY).pack())
                    
                    #Reverse flow
                    rflow = flow.reverse(port)
                    rflow.match.nw_src = AUTH_DST_IP
                    rflow.add_nw_rewrite(True, event.match.nw_dst)
                    rflow.add_output(event.pktin.in_port)
                    self.conn.send(event.sock,rflow.get_flow_mod(pyof.OFPFC_MODIFY).pack())
                
                return False
           
            #Drop remaining flows
            flow = flows.exact_entry(event.match)
            flow.set_buffer(event.pktin.buffer_id)
            self.conn.send(event.sock,flow.get_flow_mod(pyof.OFPFC_ADD).pack())
            output.dbg("Dropping "+\
                           pu.ip_val2string(event.match.nw_src) + ":"+str(event.match.tp_src)+\
                           "=>"+pu.ip_val2string(event.match.nw_dst) + ":"+str(event.match.tp_dst),
                       self.__class__.__name__)
            return False

        return True

        
