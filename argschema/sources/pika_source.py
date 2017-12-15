from .source import InputSource
import pika
import json

class PikaJsonSource(InputSource):

    def __init__(self,channel,queue):
        """Pika client source for dictionary

        Parameters
        ----------
        channel: pika.channel.Channel
            pika client channel to connect to
        queue: str
            queue name to get message from
        """
        assert(type(channel)==pika.channel.Channel)
        self.channel = channel
        self.queue = queue

    def get_dict(self):
        method_frame, header_frame, body = self.channel.basic_get(self.queue)
        if method_frame:
            d = json.loads(body)
            self.channel.basic_ack(method_frame.delivery_tag)
        return d

    def put_dict(self,d):
        