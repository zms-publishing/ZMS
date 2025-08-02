from urllib.parse import urlparse
from opensearchpy import OpenSearch, RequestsHttpConnection


def opensearch_get_client(self, REQUEST=None):
	# ${opensearch.url:https://localhost:9200, https://localhost:9201}
	# ${opensearch.url.timeout:3}
	# ${opensearch.username:admin}
	# ${opensearch.password:admin}
	# ${opensearch.ssl.verify:}

	zmscontext = self
	# Check if the method is called from a ZMS context
	try:
		url_string = zmscontext.getConfProperty('opensearch.url')
	except:
		# Fallback if the method is not called from ZMS context
		zmscontext = self.content
		url_string = zmscontext.getConfProperty('opensearch.url', 'https://localhost:9200')


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
	timeout = float(zmscontext.getConfProperty('opensearch.url.timeout', 3))
	verify = bool(zmscontext.getConfProperty('opensearch.ssl.verify', False))
	username = zmscontext.getConfProperty('opensearch.username', 'admin')
	password = zmscontext.getConfProperty('opensearch.password', 'admin')
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