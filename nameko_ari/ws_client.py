import eventlet
eventlet.monkey_patch() 
import json
import logging
import socket
from urllib.parse import urljoin
from nameko.extensions import Entrypoint, ProviderCollector, SharedExtension
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.client import SwaggerClient


logger = logging.getLogger(__name__)


class WsClient(SharedExtension, ProviderCollector):
    client = None
    app_name = None

    def __init__(self, app_name=None, **kwargs):
        if app_name:
            self.app_name = app_name
        super(WsClient, self).__init__(**kwargs)

    def setup(self):
        if not self.app_name:
            self.app_name = self.container.config['ASTERISK_ARI_APP']
        http_uri = self.container.config['ASTERISK_HTTP_URI']
        self.ari_url = urljoin(http_uri, 'ari/api-docs/resources.json')
        self.ari_user = self.container.config['ASTERISK_ARI_USER']
        self.ari_pass = self.container.config['ASTERISK_ARI_PASS']                    
        self.setup_client()

    def setup_client(self):
        http_client = SynchronousHttpClient()
        http_client.set_basic_auth('asterisk', self.ari_user, self.ari_pass)
        self.client = SwaggerClient(self.ari_url, http_client=http_client)
        logger.info('ARI client setup done.')

    def start(self):
        self.container.spawn_managed_thread(self.run)

    def stop(self):
        if self.client:
            self.client.close()
            super(WsClient, self).stop()

    def run(self):
        while True:
            try:                
                ws = self.client.events.eventWebsocket(app=self.app_name)
                for msg_str in iter(lambda: ws.recv(), None):
                    msg_json = json.loads(msg_str)
                    self.handle_event(msg_json)
            except socket.error as e:
                if e.errno == 32: # Broken pipe as we close the client.
                    pass
            except ValueError as e:
                if e.message == 'No JSON object could be decoded': # client.close()
                    pass
            except Exception as e:
                self.client = None
                error = e.message if hasattr(e, 'message') else str(e)
                logger.error('ARI connection error (%s), reconnect...', error)
                eventlet.sleep(1)
                continue

    def handle_event(self, msg):
        for provider in self._providers:
            provider.handle_event(msg)


class WsEventHandler(Entrypoint):
    ws_client = WsClient()

    def setup(self):
        self.ws_client.register_provider(self)

    def stop(self):
        self.ws_client.unregister_provider(self)

    def handle_event(self, event):
        self.container.spawn_worker(self, (event,), {},
                                    context_data={},
                                    handle_result=self.handle_result)

    def handle_result(self, message, worker_ctx, result=None, exc_info=None):
        return result, exc_info


stasis = WsEventHandler.decorator