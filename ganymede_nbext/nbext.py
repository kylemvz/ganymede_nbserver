from notebook.services.kernels.handlers import ZMQChannelsHandler
import json

class GanymedeHandler(ZMQChannelsHandler):
    def initialize(self, log=None):
        super(GanymedeHandler, self).initialize()
        self.logger = log
        self.logger.info("Loading Ganymede logging extension.")

    def log_msg(self, msg):
        json_msg = json.loads(msg)
        msg_type = json_msg['msg_type']
        if msg_type in ["execute_input", "execute_result", "stream", "error"]:
            self.log.info("%s" % json.dumps(json_msg, indent=4))

    # Log a message sent from Jupyter client
    #def on_message(self, msg):
    #    #self.logger.info("Sending message: %s" % msg)
    #    super(GanymedeHandler, self).on_message(msg)

    # Log a message sent from the kernel (see https://jupyter-client.readthedocs.org/en/latest/#
    # Note: This is an exact copy of _on_zmq_reply from ZMQStreamHandler in base/zmqhandlers.py in v4.1.0 of notebook.
    #   This code is brittle and probably should be updated on the next release
    #   Ideally, we would log either immediately before or after calling the superclass method.
    #   Unfortunately, _on_zmq_reply doesn't provide any hooks at the actual message.
    def _on_zmq_reply(self, stream, msg_list):
        if self.stream.closed() or stream.closed():
            self.log.warn("zmq message arrived on closed channel")
            self.close()
            return
        channel = getattr(stream, 'channel', None)
        try:
            msg = self._reserialize_reply(msg_list, channel=channel)
        except Exception:
            self.log.critical("Malformed message: %r" % msg_list, exc_info=True)
        else:
            self.write_message(msg, binary=isinstance(msg, bytes))
        # Call Ganymede custom logging function.
        self.log_msg(msg)

def load_jupyter_server_extension(nb_server_app):
    web_app = nb_server_app.web_app
    base_url = web_app.settings['base_url']

    # Construct a mapping of all URL patterns -> URLSpecs
    handlers = {}
    for handler in web_app.handlers:
        urlspecs = handler[1]
        for urlspec in urlspecs:
            handlers[str(urlspec.regex.pattern)] = urlspec

    # Inject GanymedeRequestHandler into the /api/kernels/<kernel_id>/channels URLSpec mapping
    api_kernel_channels_pattern = "%s/api/kernels/(?P<kernel_id>\w+-\w+-\w+-\w+-\w+)/channels$" % base_url.rstrip("/")
    channelspec = handlers[api_kernel_channels_pattern]
    channelspec.kwargs = {'log': nb_server_app.log}
    channelspec.handler_class = GanymedeHandler

