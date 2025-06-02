from urllib.parse import urlparse
from opensearchpy import OpenSearch, RequestsHttpConnection


def opensearch_get_client(self, REQUEST=None):
	# ${opensearch.url:https://localhost:9200, https://localhost:9201}
	# ${opensearch.url.timeout:3}
	# ${opensearch.username:admin}
	# ${opensearch.password:admin}
	# ${opensearch.ssl.verify:}
	url_string = self.getConfProperty('opensearch.url')
	urls = [url.strip().rstrip('/') for url in url_string.split(',')]
	hosts = []
	use_ssl = False
	# Process (multiple) url(s) (host, port, ssl)
	if not urls:
		return None
	else:
		for url in urls:
			hosts.append( { \
					'host':urlparse(url).hostname, \
					'port':urlparse(url).port } \
				)
			if urlparse(url).scheme=='https':
				use_ssl = True
	timeout = float(self.getConfProperty('opensearch.url.timeout', 3))
	verify = bool(self.getConfProperty('opensearch.ssl.verify', False))
	username = self.getConfProperty('opensearch.username', 'admin')
	password = self.getConfProperty('opensearch.password', 'admin')
	auth = (username,password)
	
	# CAVE: connection_class RequestsHttpConnection
	client = OpenSearch(
		urls,
		connection_class=RequestsHttpConnection,
		http_compress = False,
		http_auth = auth,
		use_ssl = use_ssl,
		verify_certs = verify,
		ssl_assert_hostname = verify,
		ssl_show_warn = False,
		timeout = timeout,
	)
	return client
