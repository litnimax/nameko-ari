import eventlet
import logging
import requests
import socket
from nameko.extensions import Entrypoint, ProviderCollector, SharedExtension

import ari

eventlet.monkey_patch()


logger = logging.getLogger(__name__)


class AriNotConnected(Exception):
    pass


def safe_hangup(channel):
    """Hangup a channel, ignoring 404 errors.
    :param channel: Channel to hangup.
    """
    try:
        channel.hangup()
    except requests.exceptions.HTTPError as e:
        # Ignore 404's, since channels can go away before we get to them        
        if e.response.status_code == requests.codes.not_found:
            logger.debug('Channel %s not found for hangup!', channel)
        else:
            raise


class AriClient(SharedExtension, ProviderCollector):
    client = None
    app_name = None

    def __init__(self, app_name=None, **kwargs):
        if app_name:
            self.app_name = app_name
        super(AriClient, self).__init__(**kwargs)

    def setup(self):
        self.ari_url = self.container.config['ASTERISK_ARI_URL']
        self.ari_user = self.container.config['ASTERISK_ARI_USER']
        self.ari_pass = self.container.config['ASTERISK_ARI_PASS']        
        self.app_name = self.container.config['ASTERISK_ARI_APP']

    def start(self):
        self.container.spawn_managed_thread(self.run)

    def stop(self):
        if self.client:
            self.client.close()
            super(AriClient, self).stop()

    def run(self):
        while True:
            try:
                self.client = ari.connect(self.ari_url, self.ari_user,
                                          self.ari_pass)
                self.client.on_channel_event('StasisStart', self.stasis_start)
                self.client.run(apps=self.app_name)
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

    def stasis_start(self, channel, event):
        logger.debug('StasisStart: %s', event)
        for provider in self._providers:
            provider.handle_event(channel, event)


class AriEventHandler(Entrypoint):
    ari_client = AriClient()

    def setup(self):
        self.ari_client.register_provider(self)

    def stop(self):
        self.ari_client.unregister_provider(self)

    def handle_event(self, channel, event):
        logger.debug('StasisStart: %s', event)
        self.container.spawn_worker(self, [channel, event], {},
                                    context_data={},
                                    handle_result=self.handle_result)


    def handle_result(self, message, worker_ctx, result=None, exc_info=None):
        return result, exc_info


stasis = AriEventHandler.decorator