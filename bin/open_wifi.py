#!/usr/bin/python
import web
import yapc.core as yapc
import yapc.output as output
import yapc.comm.openflow as ofcomm
import openwifi.webpage as owweb
import sys
import time

output.set_mode("VVDBG")

server = yapc.core()
ofconn = ofcomm.ofserver(server)
webapp = web.application(owweb.urls, globals())
webcleanup = owweb.cleanup(server)

if __name__ == "__main__": 
    server.run(runbg=True)
    webapp.run()
