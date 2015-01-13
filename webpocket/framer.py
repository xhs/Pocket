# -*- coding: utf-8 -*-

from struct import pack
from frame import *
from exc import *

class Framer(object):
  def __init__(self, actors, payload_limit=0):
    self._actors = actors
    self._buffer = b''
    self._payload_limit = payload_limit

  def send_text(self, text):
    self._send_data(OPCODE_TEXT, text)

  def send_binary(self, binary):
    self._send_data(OPCODE_BINARY, binary)

  def _send_data(self, opcode, data):
    limit = self._payload_limit
    if limit > 0 and limit < len(data):
      data = self._send_fragment(0, opcode, data, limit)
      while limit < len(data):
        data = self._send_fragment(0, OPCODE_CONTINUE, data, limit)
      self._send_fragment(1, OPCODE_CONTINUE, data, limit)
    else:
      data = Frame(opcode=opcode, payload=data).encode()
      self._actors['streamer'].send(data)

  def _send_fragment(self, fin, opcode, payload, limit):
    data = Frame(fin=fin, opcode=opcode, payload=payload[:limit]).encode()
    self._actors['streamer'].send(data)
    return payload[limit:]

  def feed(self, data):
    self._buffer += data
    while len(self._buffer) > 0:
      try:
        frame, left_data = Frame().decode(self._buffer)
        self._buffer = left_data
        self._actors['messager'].feed(frame)
      except InsufficientBytesException:
        break

  def send_pong(self):
    data = Frame(opcode=OPCODE_PONG).encode()
    self._actors['streamer'].send(data)

  def send_close(self, code, reason):
    payload = pack('!H', code) + reason
    data = Frame(opcode=OPCODE_CLOSE, payload=payload).encode()
    self._actors['streamer'].send(data)

if __name__ == '__main__':
  class DummyMessager(object):
    def feed(self, frame):
      frame.inspect()

  messager = DummyMessager()
  framer = Framer({'messager': messager})

  data = Frame(payload='foobar').encode()
  framer.feed(data[:3])
  framer.feed(data[3:])
