from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

clients = []

# class WebsocketHandler(WebSocket):
#
#     def __init__(self, callback):
#         self.callback = callback
#
#     def handleMessage(self):
#         for client in clients:
#             if client != self:
#                 self.callback(self.data)
#                 print(self.data)
#
#     def handleConnected(self):
#         print(self.address, 'connected')
#         for client in clients:
#             print(self.address[0] + u' - connected')
#         clients.append(self)
#
#     def handleClose(self):
#         clients.remove(self)
#         print(self.address, 'closed')
#         for client in clients:
#             print(self.address[0] + u' - disconnected')