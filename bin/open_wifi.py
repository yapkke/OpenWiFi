#!/usr/bin/python
import web
import yapc.core as yapc
import yapc.output as output
import yapc.comm.openflow as ofcomm
import yapc.util.memcacheutil as mcutil
import openwifi.webpage as owweb
import openwifi.globals as owglobal
import openwifi.authenticate as owauth
import sys
import time

output.set_mode("VVDBG")
mcutil.memcache_mode = mcutil.MEMCACHE_MODE["LOCAL"]
web.config.debug=True

server = yapc.core()
owglobal.server = server
ofconn = ofcomm.ofserver(server)
webapp = web.application(owweb.urls, globals())
webcleanup = owweb.cleanup(server)
session = web.session.Session(webapp, 
                              web.session.DiskStore('sessions'), 
                              initializer={'datapath': None, 
                                           'host': None})
owglobal.session = session
hauth = owauth.host_auth(server)

if __name__ == "__main__": 
    server.run(runbg=True)
    webapp.run()
