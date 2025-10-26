
from websockets.asyncio.server import ServerConnection
from random import randint
from typing import Tuple

def resolve_ip_address(websocket: ServerConnection) -> Tuple[str, int]:
    headers = websocket.request.headers
    pseudo_port = randint(1024, 65535)

    if 'CF-Connecting-IP' in headers:
        return headers['CF-Connecting-IP'].strip(), pseudo_port

    if 'X-Real-IP' in headers:
        return headers['X-Real-IP'].strip(), pseudo_port

    if 'X-Forwarded-For' in headers:
        return headers['X-Forwarded-For'].split(',')[0].strip(), pseudo_port

    address = websocket.remote_address

    if not address:
        return '', pseudo_port

    return address[0] or '', address[1] or pseudo_port
