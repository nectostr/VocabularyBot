import os


use_proxy = os.environ.get("use_proxy", False) == "True"
proxy_user = os.environ.get("proxy_user", None)
proxy_pass = os.environ.get("proxy_pass", None)
proxy_address = os.environ.get("proxy_address", None)
proxy_port = int(os.environ.get("proxy_port", 0))
token = os.environ.get("token", "awahahamybeautifultokenyoucantsteal888")
