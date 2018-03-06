# saved as greeting-client.py
import Pyro4

"""
Hold up, need to start the greeting server first.
Directions are in greeting-server.py

Once that's done, this process can communicate with it.
"""

name = input("What is your name? ").strip()

# use name server object lookup uri shortcut
greeting_maker = Pyro4.Proxy("PYRONAME:example.greeting")
print(greeting_maker.get_fortune(name))   # call method normally

