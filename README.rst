SmartVA-Analyze is an application that implements the `Tariff 2.0 Method <http://www.healthdata.org/research-article/improving-performance-tariff-method-assigning-causes-death-verbal-autopsies/>`_ for computer certification of verbal autopsies.

More information and the SmartVA-Analyze Application can be found here:
http://www.healthdata.org/verbal-autopsy/tools

Requirements
~~~~~~~~~~~~

* `Anaconda <https://www.anaconda.com/download/>`_

* `Docker <https://www.docker.com/get-started>`_


Build Instructions
~~~~~~~~~~~~~~~~~~

WINDOWS: ``build_script.bat``

macOS, LINUX: ``sh build_script.sh``

Environment Instructions
~~~~~~~~~~~~~~~~~~~~~~~~

WINDOWS::

    $ conda create -n smartva python=2.7.13 wxpython=3.*
    $ activate smartva
    $ pip install -r requirements.txt -r requirements-dev.txt - r requirements-win.txt

macOS,LINUX::

    $ conda create -n smartva python=2.7.13 wxpython=3.*
    $ source activate smartva
    $ pip install -r requirements.txt -r requirements-dev.txt

    or

    $ docker build -t smartva-build-linux -f ./pkg/docker/linux-build/Dockerfile ./pkg/docker
    $ docker build -t smartva-dev -f pkg/docker/dev/Dockerfile .
    $ docker run -it --rm -v `pwd`:/home/smartva/smartva smartva-dev

Development Instructions
~~~~~~~~~~~~~~~~~~~~~~~~
``$ python app.py --help``

::

    Usage: app.py [OPTIONS] INPUT OUTPUT

    Options:
      --country TEXT                  Data origin country abbreviation. "LIST"
                                      displays all. Default is "Unknown".
      --hiv BOOLEAN                   Data is from an HIV region. Default is True.
      --malaria BOOLEAN               Data is from a Malaria region. Default is
                                      True.
      --hce BOOLEAN                   Use Health Care Experience (HCE) variables.
                                      Default is True.
      --freetext BOOLEAN              Use "free text" variables. Default is True.
      --figures BOOLEAN               Generate charts and figures output. Default
                                      is True.
      --language [english|chinese|spanish]
                                      Language used for output files.
      --version                       Show the version and exit.
      --legacy-format                 Output files in a format that matches
                                      SmartVA v1.2
      --help                          Show this message and exit.

Example
~~~~~~~
::

    $ mkdir output-folder
    $ python app.py "./test/end_to_end_notebooks/data/example_1.csv" "./output-folder" --hiv=False --country=RWA

Test Instructions
~~~~~~~~~~~~~~~~~
``$ python -m pytest``
