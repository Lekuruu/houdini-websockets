# Houdini Websockets Extension

This repository contains a plugin for houdini, which allows you to host native websocket servers.

## Setup

To set this up go into your `houdini/plugins` folder and clone the repository inside there:

```shell
git clone https://github.com/Lekuruu/houdini-websockets.git
```

**Be sure to have the `websockets` package installed!**
If you haven't done so yet, install it by doing

```shell
pip install websockets
```

> [!NOTE]
> If you are using wand, you will have to add `websockets` to the end of your `requirements.txt` file, as well as
> rebuilding your containers by doing `docker compose build` and `docker compose up`.

By default the websocket server will be listening on the port of the game server + 1000. For example:

```
Port for blizzard: 9876
Port for blizzard (websocket): 10876
```

You are able to change this behaviour that inside the `__init__.py` if you want to.

> [!NOTE]
> If you are using wand, be sure to expose the websocket ports inside the `docker-compose.yml` file!

After restarting the server, you should be seeing a log message similar to `Websocket server listening on 0.0.0.0:<port>`.

### Using an ssl certificate (optional)

This part is optional, but required if your server runs under https/ssl. It will *require* you to have a valid domain/subdomain *and* ssl certificate.  

1. Move your ssl certificate file to somewhere inside the houdini folder.
2. Set the path to your ssl files in `__init__.py` (line 36 and 41)
3. Restart the server

Here is an example:

```python
@property
def certificate_path(self) -> Optional[str]:
    """The path to the certificate file (optional)"""
    return "./path/to/your/cert.pem"

@property
def key_path(self) -> Optional[str]:
    """The path to the key file (optional)"""
    return "./path/to/your/key.pem"
```
