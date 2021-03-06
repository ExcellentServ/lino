====================
Use a MySQL database
====================

If you decided to use MySQL as database frontend, 
then here is a cheat sheet for quickly doing so.
No warranty.

Installation
============

To install mysql on your site::

    $ sudo aptitude install mysql-server python-mysqldb
    
Or if your site is to run within a virtualenv::
    
    $ sudo aptitude install mysql-server libmysqlclient-dev python-dev
    $ pip install MySQL-python

Users
=====
    
For your first project create a user ``django`` which you can reuse
for all projects::
    
    $ mysql -u root -p 
    mysql> create user 'django'@'localhost' identified by 'my cool password';

To see all users defined on the site::

    mysql> select host, user, password from mysql.user;
    +-----------+------------------+------------------------------+
    | host      | user             | password                     |
    +-----------+------------------+------------------------------+
    | localhost | root             | 6FD6D9512034462391B7154E5ADF |
    | 127.0.0.1 | root             | 6FD6D9512034462391B7154E5ADF |
    | localhost |                  |                              |
    | localhost | debian-sys-maint | A14910957D8F261196A210B4C82F |
    | localhost | django           | 42214E1C5E6EF5119DD86A2A2F8C |
    | %         | django           | 42214E1C5E6EF5119DD86A2A2F8C |
    +-----------+------------------+------------------------------+
    6 rows in set (0.00 sec)


Here is how to change the password of an existing user::

    mysql> set password for 'django'@'localhost' = password('my cool password');


Databases
=========

For each new project you must create a database and grant permissions
to ``django``::
    
    $ mysql -u root -p 
    mysql> create database mysite charset 'utf8';
    mysql> grant all on mysite.* to django with grant option;
    mysql> grant all on test_mysite.* to django with grant option;
    mysql> quit;


See which databases are installed on this server::

    mysql> show databases;


And then of course you set DATABASES in your :xfile:`settings.py` 
file::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', 
            'NAME': 'mysite',                     
            # The following settings are not used with sqlite3:
            'USER': 'django',
            'PASSWORD': 'my cool password',
            'HOST': '',                      
            'PORT': '',                      
        }
    }



Notes about certain MySQL configuration settings
================================================

See the following chapters of the MySQL documentation

-  Lino is tested only with databases using the 'utf8' charset.
   See `Database Character Set and Collation
   <http://dev.mysql.com/doc/refman/5.0/en/charset-database.html>`_

.. _innodb:

Lino and the InnoDB engine
==========================

Lino versions before :blogref:`20141220` wer more easy to use with
the MyISAM database storage because :manage:`initdb` can fail to
drop tables due to InnoDB's more severe integrity contraints.  Using
InnoDB can cause the following error message when trying to run
:manage:`initdb` a *second* time::

    IntegrityError: (1217, 'Cannot delete or update a parent row: 
    a foreign key constraint fails')

One method to set the default database storage on a Debian server is
to create a file :file:`/etc/mysql/conf.d/set_myisam_engine.cnf`
with this content::

    [mysqld]
    default-storage-engine=myisam

If you insist on InnoDB, you can work around this problem by doing
yourself a `DROP DATABASE` followed by a new `CREATE DATABASE`
before running :manage:`initdb`.

See also `Setting the Storage Engine
<http://dev.mysql.com/doc/refman/5.1/en/storage-engine-setting.html>`_




