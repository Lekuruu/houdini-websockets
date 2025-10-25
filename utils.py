
from websockets.asyncio.server import ServerConnection

def resolve_ip_address(websocket: ServerConnection) -> str:
    headers = websocket.request.headers

    if 'CF-Connecting-IP' in headers:
        return headers['CF-Connecting-IP'].strip()

    if 'X-Real-IP' in headers:
        return headers['X-Real-IP'].strip()
    
    if 'X-Forwarded-For' in headers:
        return headers['X-Forwarded-For'].split(',')[0].strip()

    address = websocket.remote_address

    if not address:
        return ''

    return address[0] or ''
