.. image:: https://img.shields.io/pypi/v/licenseheaders.svg
    :target: https://pypi.python.org/pypi/licenseheaders/
    :alt: PyPi version

.. image:: https://img.shields.io/pypi/pyversions/licenseheaders.svg
    :target: https://pypi.python.org/pypi/licenseheaders/
    :alt: Python compatibility
 	
.. image:: https://img.shields.io/travis/elmotec/licenseheaders.svg
    :target: https://travis-ci.org/elmotec/licenseheaders
    :alt: Build Status

.. image:: https://img.shields.io/pypi/dm/licenseheaders.svg
    :alt: PyPi
    :target: https://pypi.python.org/pypi/licenseheaders

.. image:: https://coveralls.io/repos/elmotec/licenseheaders/badge.svg
    :target: https://coveralls.io/r/elmotec/licenseheaders
    :alt: Coverage
    
.. image:: https://img.shields.io/codacy/474b0af6853a4c5f8f9214d3220571f9.svg
    :target: https://www.codacy.com/app/elmotec/licenseheaders/dashboard
    :alt: Codacy


========
licenseheaders
========

A tool to update, change or add license headers to all files of any of 
the supported types in or below some directory.

Currently, the following file types are supported: .c, .c++, .cc, .config, .cpp, .cs, .csh,
.erl, .groovy, .h, .hpp, .jape, .java, .js, .jsx, .pl, .py, .rb,
.scala, .schema, .sh, .sql, .src, .ts, .vb, .xml 


Usage
-----

::

  usage: licenseheaders.py [-h] [-v] [-V] [-d directory] [-t template] [-y years] [-b] [-a]
                            [-c copyrightOwner] 

  License Header Updater

  positional arguments: none

  optional arguments:
    -h, --help            show this help message and exit
    -V, --version         show program's version number and exit
    -v, --verbose         increases log verbosity (can be specified multiple times)
    -d, --dir             directory to process, all subdirectories will be included
    -t, --tmpl            template name or file to use (if not specified, -y must be specified)
    -y, --years           if template is specified, the year to substitute, otherwise this year
                          or year range will replace any existing year in existing headers.
                          Replaces variable ${years} in a template
    -b, --backup          for each file that gets changed, create a backup of the original with
                          the additional filename extension .bak
    -c, --cr              copyright owner, replaces variable ${owner} in a template
    -a, --addonly         add a header to all supported file types, ignore any existing headers.

  Examples:
  # Add a new license header or replace any existing one based on
  # the lgpl-v3 template.
  # Process all files of supported type in or below the current directory.
  # Use "Eager Hacker" as the copyright owner.

  licenseheaders -t lgpl-v3 -c "Eager Hacker"


If licenseheaders is installed as a package (from pypi for instance), one can interact with it as a command line tool:

::

  python -m licenseheaders -t lgpl3 -c "Eager Hacker"

or directly:

::

  licenseheaders -t lgpl3 -c "Eager Hacker"  



Installation
------------

Download ``licenseheaders.py`` from ``http://github.com/johann-petrak/licenseheaders`` or :

::

  pip install licenseheaders


Template names and files
------------------------

This library comes with a number of predefined templates. If a template name is specified
which when matched against all predefined template names matches exactly one as a substring,
then that template is used. Otherwise the name is expected to be the path of file.

If a template does not contain any variables of the form `${varname}` it is used as is.
Otherwise the program will try to replace the variable from one of the following 
sources:

- an environment variable with the same name but the prefix `LICENSE_HEADERS_` added
- the command line option that can be used to set the variable (see usage)

Predefined templates:
- gpl-v3: GNU GPL v3.0
- gpl-v3-multipart: Variation for projects with several source files
- agpl-v3: GNU AGPL v3.0
- agpl-v3-multipart: Variation for projects with several source files
- lgpl-v2.1: GNU LGPL v2.1
- lgpl-v3: GNU LGPL v3.0
- lgpl-v3-multipart: Variation for projects with several source files
- apache-2: Apache v2.0
- bsd-3: BSD v3.0
- mit: MIT

Supported file types and how they are processed
-----------------------------------------------

C:
- assumed for all files with the extensions: .c, .cc, .cpp, .c++, .h, .hpp
- only headers that use C block comments (/*...*/) are reconized as existing headers
- the template text will be wrapped in block comments

Java:
- assumed for all files with the extensions: .java, .scala, .groovy
- only headers that use Java block comments are recognized as existing headers
- the template text will be wrapped in block comments

Python:
- assumed for all files with the extension: .py
- keep first line containing the shebang and (possibly) second line if it contains encoding definition
- the template text will be wrapped in line comments

The full list of supported file extensions can be viewed with

::

   licenseheaders -h


License
-------

Licensed under the term of `MIT License`_. See attached file LICENSE.txt.


.. _MIT License: http://en.wikipedia.org/wiki/MIT_License

