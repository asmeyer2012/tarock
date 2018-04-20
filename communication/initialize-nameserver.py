import Pyro4
import Pyro4.naming

import socket

## this way requires the naming server to be called from bash
## can I do this completely within python?

#daemon = Pyro4.Daemon() ## make a Pyro daemon to listen for function calls
#ns = Pyro4.locateNS()   ## find the name server
#uri = daemon.register(function) ## register function with a name in name server
#ns.register("object.name",uri)  ## register object with a name in name server

Pyro4.config.SERVERTYPE='multiplex'

## supposedly starts the name server, but locateNS hangs
print "get hostname"
#hostname = socket.gethostname()
hostname = 'localhost'
print "start name server"
nsUri,nsDaemon,bcServer = Pyro4.naming.startNS(host=hostname)
print "nsUri   : ",nsUri
print "nsDaemon: ",nsDaemon
assert bcServer is not None, "expect a broadcast server to be created"
print "bcServer: ",bcServer
print "locate name server"
#ns = Pyro4.locateNS()   ## find the name server
print "ready"

#daemon.requestLoop()

