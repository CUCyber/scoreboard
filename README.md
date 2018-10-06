snakeboi
========

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
$ sudo apt install python3 python3-setuptools build-essential libmariadb-dev
$ sudo ./setup.py install
```


### RedHat/CentOS

```sh
$ sudo yum groupinstall "Development Tools"
$ sudo yum install epel-release
$ sudo yum install python34 python34-setuptools mariadb-devel
$ sudo ./setup.py install
```


### Fedora

```sh
$ sudo dnf groupinstall "Development Tools"
$ sudo dnf install mariadb-devel
$ sudo ./setup.py install
```


### Arch

```sh
$ sudo pacman -S base-devel mariadb-clients
$ sudo ./setup.py install
```


### Gentoo

```sh
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
$ snakeboi config.py
```
