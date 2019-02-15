teams = {
    'Team1': '10.0.130.0',
    'Team2': '10.0.131.0',
    'Team3': '10.0.132.0',
    'Team4': '10.0.133.0',
}

services = {
    'FTP': {'proto': 'ftp', 'offset': 5, 'port': 21, 'file': 'DONOTDELETE', 'contents': 'asdf', 'dne': 'DOESNOTEXIST'},
    'SSH': {'proto': 'ssh', 'offset': 6, 'port': 22, 'username': 'asdf', 'password': 'asdf'},
    'HTTP': {'proto': 'http', 'offset': 7, 'port': 80, 'method': 'GET', 'url': '/', 'regex': 'asdf'},
    'MySQL': {'proto': 'mysql', 'offset': 8, 'port': 3306, 'username': 'asdf', 'password': 'asdf', 'db': ''},
}

interval = 60
timeout = 1
