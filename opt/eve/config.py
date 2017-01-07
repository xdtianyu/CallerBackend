schema = {
    'uid': {
        'type': 'string',
        'minlength': 8,
        'maxlength': 30,
    },
    'number': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 20,
    },
    'name': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 30,
    },
    'city': {
        'type': 'string',
        'minlength': 0,
        'maxlength': 20,
    },
    'provider': {
        'type': 'string',
        'minlength': 0,
        'maxlength': 20,
    },
    'province': {
        'type': 'string',
        'minlength': 0,
        'maxlength': 20,
    },
    'type': {
        'type': 'integer',
    },
    'from': {
        'type': 'integer',
    },
    'count': {
        'type': 'integer',
    },
}


caller = {
    'allow_unknown': False,
    'resource_methods': ['GET', 'POST'],
    'schema': schema
}


config = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'caller',
    'URL_PREFIX': 'api',
    'API_VERSION': 'v1',
    'DEBUG': True,
    'DOMAIN': {'caller': caller}
}