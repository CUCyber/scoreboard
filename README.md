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


## Running

```sh
$ scoreboard config.py
```
