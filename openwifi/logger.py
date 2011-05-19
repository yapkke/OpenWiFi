import yapc.interface as yapc
import yapc.log.sqlite as sqlite
import yapc.util.parse as pu
import yapc.log.output as output
import openwifi.event as owevent
import time

class authlogger(sqlite.SqliteLogger, yapc.component):
    """Class to log authentication and unauthentication

    @author ykk
    @date May 2011
    """
    def __init__(self, server, db, name="Auth"):
        """Initialize
        """
        sqlite.SqliteLogger.__init__(self, db, name)
        server.register_event_handler(owevent.authenticated.name, self)
        server.register_event_handler(owevent.unauthenticated.name, self)

    def get_col_names(self):
        """Get column names
        """
        return ["time_received","event",
                "datapathid","ethernet_addr",  "openid"]

    def processevent(self, event):
        """Process event
        """
        if (isinstance(event, owevent.authenticated)):
            h = None
            if (event.host != None):
                h = pu.array2hex_str(event.host)
            i = [time.time(),
                 "auth",
                 event.datapathid,
                 h,
                 event.openid]
            output.dbg("Authentication of "+str(h)+" recorded"+\
                           " with OpenID "+event.openid,
                       self.__class__.__name__)
            self.table.add_row(tuple(i))
        elif (isinstance(event, owevent.unauthenticated)):
            h = None
            if (event.host != None):
                h = pu.array2hex_str(event.host)
            i = [time.time(),
                 "unauth",
                 event.datapathid,
                 h,
                 None]
            output.dbg("Unauthentication of "+str(h)+" recorded",
                       self.__class__.__name__)
            self.table.add_row(tuple(i))
                 
        return True
