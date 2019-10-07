import os


use_proxy = os.environ["use_proxy"] == "True"
proxy_user = os.environ["proxy_user"]
proxy_pass = os.environ["proxy_pass"]
proxy_address = os.environ["proxy_address"]
proxy_port = int(os.environ["proxy_port"])
token = os.environ["token"]
