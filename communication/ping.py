import Pyro4

proxy = Pyro4.Proxy("PYRONAME:GameServer")
proxy.GetPlayers()
proxy.Ping()

