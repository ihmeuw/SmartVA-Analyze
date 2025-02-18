.. image:: https://travis-ci.com/ihmeuw/SmartVA-Analyze.svg?branch=master
    :target: https://travis-ci.com/ihmeuw/SmartVA-Analyze
    
SmartVA-Analyze is an application that implements the `Tariff 2.0 Method <http://www.healthdata.org/research-article/improving-performance-tariff-method-assigning-causes-death-verbal-autopsies/>`_ for computer certification of verbal autopsies.

More information and the SmartVA-Analyze application can be found here:
http://www.healthdata.org/verbal-autopsy/tools

The latest development version of the SmartVA-Analyze application can be found in `releases. <https://github.com/ihmeuw/SmartVA-Analyze/releases>`_
The application is available as a Windows graphical user interface (GUI), Windows command-line interface (CLI), and Linux binary.

The latest stable version of the SmartVA-Analyze application can be found here:
http://www.healthdata.org/verbal-autopsy/tools

The SmartVA-Analyze application requires an input csv in the format of the `PHMRC Full Questionnaire <http://www.healthdata.org/verbal-autopsy/tools/>`_,
`PHMRC Shortened (SmartVA) Questionnaire <http://www.healthdata.org/verbal-autopsy/tools/>`_,
`WHO 2016 Questionnaire <https://www.who.int/healthinfo/statistics/verbalautopsystandards/en/>`_
or
`WHO 2022 Questionnaire <https://www.who.int/healthinfo/statistics/verbalautopsystandards/en/>`_..
The simplest workflow is to collect verbal autopsy data with `ODK Collect <https://docs.opendatakit.org/collect-intro/>`_ and export the questionaire data
via `ODK Aggregate <https://docs.opendatakit.org/aggregate-intro/>`_ or `ODK Briefcase <https://docs.opendatakit.org/briefcase-intro/>`_.

Requirements
~~~~~~~~~~~~
To compile the source code of SmartVA-Analyze, the following applications must be installed:

* `Anaconda <https://www.anaconda.com/download/>`_

* `Docker <https://www.docker.com/get-started>`_


Build Instructions
~~~~~~~~~~~~~~~~~~
To build the SmartVA-Analyze application as seen in `releases <https://github.com/ihmeuw/SmartVA-Analyze/releases>`_, run one of the following commands:

Windows: ``build_script.bat``

macOS, Linux: ``$ sh build_script.sh``

Environment Instructions
~~~~~~~~~~~~~~~~~~~~~~~~
To create your python environment, either create a conda environment or use the Docker image.

::

    $ conda env create --file=smartva.yaml
    $ conda activate smartva3


Run Instructions
~~~~~~~~~~~~~~~~
To test your python environment, run the following command to show the available options.

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

    $ mkdir ./test/example/output
    $ python app.py "./test/example/input/PHMRC_short_example.csv" "./test/example/output" --hiv=False
    $ python app.py "./test/example/input/WHO_2016_1_5_1_example.csv" "./test/example/output" --language=chinese --country=CHN

Test Instructions
~~~~~~~~~~~~~~~~~
All tests are run using pytest:

``$ python -m pytest``

Build Instructions
~~~~~~~~~~~~~~~~~~
::
    $ cp pkg/smartva-win.spec .
    $ pyinstaller smartva-win.spec --clean
