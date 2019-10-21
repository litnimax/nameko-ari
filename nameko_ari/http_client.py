import eventlet
eventlet.monkey_patch() 
import logging
from urllib.parse import urljoin, urlparse
from nameko.extensions import DependencyProvider
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.client import SwaggerClient


logger = logging.getLogger(__name__)


class AriClient(DependencyProvider):
    ari = None

    def setup(self):
        self.http_uri = self.container.config['ASTERISK_HTTP_URI']
        self.ari_url = urljoin(self.http_uri, 'ari/api-docs/resources.json')
        self.ari_user = self.container.config['ASTERISK_ARI_USER']
        self.ari_pass = self.container.config['ASTERISK_ARI_PASS']        
        self.app_name = self.container.config['ASTERISK_ARI_APP']
        while True:
            try:
                self.setup_client()
                break
            except Exception as e:
                logger.error('ARI HTTP setup error: %s', e)
                eventlet.sleep(1)


    def setup_client(self):
        http_client = SynchronousHttpClient()
        http_client.set_basic_auth(
                                urlparse(self.http_uri).netloc.split(':')[0],
                                self.ari_user, self.ari_pass)
        self.ari = SwaggerClient(self.ari_url, http_client=http_client)
        logger.info('ARI client setup done.')


    def get_dependency(self, worker_ctx):
        return self.ari