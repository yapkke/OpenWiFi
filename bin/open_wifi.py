#!/usr/bin/python
import web
import yapc.core as yapc
import yapc.output as output
import yapc.comm.openflow as ofcomm
import openwifi.webpage as owweb
import openwifi.globals as owglobal
import sys
import time

output.set_mode("DBG")
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

if __name__ == "__main__": 
    server.run(runbg=True)
    webapp.run()
