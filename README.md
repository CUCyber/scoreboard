scoreboard
==========

A scoreboard for verifying and scoring services in a red vs. blue competition.


## Dependencies

* python3
* fooster-web
* dnspython
* python-ldap
* python-mysqlclient
* paramiko


### Debian/Ubuntu/Kali

```sh
$ sudo apt install build-essential python3 python3-setuptools python3-cffi libldap2-dev libmariadb-dev
$ sudo ./setup.py install
```


### RedHat/CentOS

```sh
$ sudo yum groupinstall "Development Tools"
$ sudo yum install epel-release
$ sudo yum install python34 python34-devel python34-setuptools python34-cffi openldap-devel mariadb-devel
$ sudo ./setup.py install
```


### Fedora

```sh
$ sudo dnf groupinstall "Development Tools"
$ sudo dnf install python3-devel python3-cffi openldap-devel mariadb-devel
$ sudo ./setup.py install
```


### Arch

```sh
$ sudo pacman -S base-devel python-cffi libldap libmariadbclient
$ sudo ./setup.py install
```


### Gentoo

```sh
$ sudo emerge dev-python/cffi net-nds/openldap dev-db/mariadb-connector-c
$ sudo ./setup.py install
```


### macOS

Requires [Homebrew](https://brew.sh/).

```sh
$ brew install python3 mysql-connector-c
$ ./setup.py install
```


## Configuring

### Options

...

```python
score = True

interval = 60
timeout = 3
poll = 1
workers = 4
show = True
```


### Teams

Each team is identified by a name that maps to a base IP address from which the offset for each service will be added. Generally this will be the base address in the CIDR notation for each team's network (without the mask). This assumes that each service is at the same offset for each team.


#### Example

```python
teams = collections.OrderedDict()
teams['Team1'] = '10.0.130.0'
teams['Team2'] = '10.0.131.0'
teams['Team3'] = '10.0.132.0'
teams['Team4'] = '10.0.133.0'
```


### Services

Services are identified by a name that maps to a configuration for how the scoreboard should score the service. This includes at a minimum the protocol to score with and the IP address offset of the service relative to each team's base IP address. Any protocol option can be a list that when found will generate a random index each poll interval and use the same index for all lists in the service for all teams.


### Example

```python
services = collections.OrderedDict()
services['FTP'] = {'proto': 'ftp', 'offset': 5, 'port': 21, 'file': 'DONOTDELETE', 'contents': 'asdf', 'dne': 'DOESNOTEXIST'}
services['SSH'] = {'proto': 'ssh', 'offset': 6, 'port': 22, 'username': 'asdf', 'password': 'asdf'}
services['HTTP'] = {'proto': 'http', 'offset': 7, 'port': 80, 'method': 'GET', 'url': ['/', '/test1', '/test2'], 'regex': [r'asdf', r'asdf1', r'asdf2']}
services['MySQL'] = {'proto': 'mysql', 'offset': 8, 'port': 3306, 'username': 'asdf', 'password': 'asdf', 'db': ''}
```


### Ping

#### Options

None


### TCP

#### Options

* `port`


### DNS

#### Options

* `port`
* `hostname`


### FTP

#### Options

* `port`
* `cert` (optional; uses FTPS; boolean or string path of CA certificate)
* `username` (optional; uses login information)
* `password` (optional; uses login information)
* `file` (optional; checks for contents of file)
* `contents` (optional; checks for contents of file)
* `dne` (optional; checks for lack of file)


### HTTP

#### Options

* `port`
* `cert` (optional; uses HTTPS; boolean or string path of CA certificate)
* `method` (optional; sends HTTP request)
* `headers` (optional; sends HTTP headers)
* `host` (optional; sends HTTP Host header)
* `url` (optional; sends HTTP request)
* `body` (optional; sends HTTP request body)
* `regex` (optional; regular expression to check for in the HTTP response)


### IMAP

#### Options

* `port`
* `cert` (optional; uses STARTTLS; boolean or string path of CA certificate)
* `username` (optional; uses login information)
* `password` (optional; uses login information)
* `list` (optional; checks for email list)


### LDAP

#### Options

* `port`
* `cert` (optional; uses STARTTLS; boolean or string path of CA certificate)
* `dn` (optional; uses simple bind)
* `password` (optional; uses simple bind)
* `base` (optional; searches for common name under base name)
* `cn` (optional; searches for common name under base name)


### MySQL

#### Options

* `port`
* `username`
* `password`
* `db` (optional; uses database)
* `query` (optional; executes and checks query)
* `result` (optional; executes and checks query)


### POP3

#### Options

* `port`
* `cert` (optional; uses STARTTLS; boolean or string path of CA certificate)
* `username` (optional; uses login information)
* `password` (optional; uses login information)
* `list` (optional; checks for email list)


### SMTP

#### Options

* `port`
* `cert` (optional; uses STARTTLS; boolean or string path of CA certificate)
* `username` (optional; uses login information)
* `password` (optional; uses login information)
* `from_` (optional; attempts to send an email)
* `to` (optional; attempts to send an email)


### SSH

#### Options

* `port`
* `username`
* `password`


## Running

```sh
$ scoreboard config.py
```
