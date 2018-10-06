teams = {
    'Test': '127.0.0.0',
}

services = {
    'HTTP2': {'proto': 'http', 'offset': 1, 'port': 8000, 'method': 'GET', 'url': '/', 'regex': '.*'},
    'FTP': {'proto': 'ftp', 'offset': 5, 'port': 21, 'file': 'DONOTDELETE', 'contents': 'asdf', 'dne': 'DOESNOTEXIST'},
    'SSH': {'proto': 'ssh', 'offset': 6, 'port': 22, 'username': 'asdf', 'password': 'asdf'},
    'HTTP': {'proto': 'http', 'offset': 7, 'port': 80, 'method': 'GET', 'url': '/', 'regex': 'asdf'},
    'MySQL': {'proto': 'mysql', 'offset': 8, 'port': 3306, 'username': 'asdf', 'password': 'asdf', 'db': 'asdf'},
}

interval = 60
