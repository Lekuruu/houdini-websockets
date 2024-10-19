
from websockets import WebSocketServerProtocol

def resolve_ip_address(websocket: WebSocketServerProtocol) -> str:
    headers = websocket.request_headers

    if 'CF-Connecting-IP' in headers:
        return headers['CF-Connecting-IP']

    if 'X-Real-IP' in headers:
        return headers['X-Real-IP'].strip()
    
    if 'X-Forwarded-For' in headers:
        return headers['X-Forwarded-For'].split(',')[0]

    address = websocket.remote_address

    if address is None:
        return ''
    
    return address[0]
