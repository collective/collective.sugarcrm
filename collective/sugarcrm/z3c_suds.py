from suds.client import Client

try:
    from zope.site.hooks import getSite
    _get_default_context = getSite
except ImportError:
    try:
        from zope.app.component.hooks import getSite
        _get_default_context = getSite
    except ImportError:
        _get_default_context = lambda: None

def get_suds_client(wsdl_uri, **kwargs):

    context = kwargs.pop('context', None)
    if context is None or type(context) == dict:
        context = _get_default_context()

    if context is None:
        # no cache
        client = Client(wsdl_uri, **kwargs)
    else:
        jar = getattr(context, '_p_jar', None)
        oid = getattr(context, '_p_oid', None)
        if jar is None or oid is None:
            # object is not persistent or is not yet associated with a
            # connection
            cache = context._v_suds_client_cache = {}
        else:
            cache = getattr(jar, 'foreign_connections', None)
            if cache is None:
                cache = jar.foreign_connections = {}
        
        cache_key = 'suds_%s' % wsdl_uri
        client = cache.get(cache_key)
        if client is None:
            client = cache[cache_key] = Client(wsdl_uri, **kwargs)
    
    return client

__all__ = ('get_suds_client',)
