# saved as greeting-server.py
import Pyro4

"""
!! start the naming server first with:
python -m Pyro4.naming
   or
pyro4-ns

!! it is possible to query the naming server with:
$ python -m Pyro4.nsc list

!! once the naming server is running, start this process in the background with:
$ python greeting-server.py
"""

@Pyro4.expose
class GreetingMaker(object):
  def get_fortune(self, name):
    return "Hello, {0}. Here is your fortune message:\n" \
      "Behold the warranty -- the bold print giveth and the fine print taketh away.".format(name)

daemon = Pyro4.Daemon()                # make a Pyro daemon
ns = Pyro4.locateNS()                  # find the name server
uri = daemon.register(GreetingMaker)   # register the greeting maker as a Pyro object
ns.register("example.greeting",uri)    # register the object with a name in the name server

print("Ready.")                        # print the uri so we can use it in the client later
daemon.requestLoop()                   # start the event loop of the server to wait for calls

