# Nameko Asterisk REST Interface client extension
This Nameko extension has both a HTTP client and websocket event listener.

Example service:

```python
from nameko_ari import AriClient, stasis


class AriBroker:
    name = 'asterisk_ari'
    ari_client = AriClient()


@stasis('my_app')
def on_stasis_event(self, event):
    print(event)
```

Configuration parameters:

* **ASTERISK_ARI_ENABLED** (default - yes): if set to no, ARI client will not setup.
* **ASTERISK_HTTP_URI** - Asterisk ARI connection string, e.g. `http://127.0.0.1:8088`.
  The rest part `ari/api-docs/resources.json` will be appended to this URI.
* **ASTERISK_ARI_USER** - ARI login from ``ari.conf``.
* **ASTERISK_ARI_PASS** - ARI password from ``ari.conf``.
* **ASTERISK_ARI_APP** - for WS client you can specify application name as ``@stasis`` entrypoint
  parameter e.g. ``@stasis('my_app')``. For HTTP client set application name in config.
