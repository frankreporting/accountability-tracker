accountability_tracker
======================

[SCPR](http://www.scpr.org/) repository to house an iterative Django project that will store and provide data for a series of projects dealing with accountability in the political process.

Documentation
=============

* Bootstrapping the project for local development

    * Clone the project repository

            git clone git@github.com:SCPR/accountability-tracker.git

    * Change into the directory

            cd accountability-tracker

    * Assuming you're running Python 2.x and have [virtualenv](https://virtualenv.pypa.io/en/latest/) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/) installed...

        * Create a new virtualenv and activate it

                mkvirtualenv accountability-tracker
                workon accountability-tracker

        * Install the project requirements

                pip install -r requirements.txt

        * Create a copy of ```config.yml.template``` and rename it as ```development.yml```. ```development.yml``` is ignored by default and should not be committed to the repository.

                cp config.yml.template development.yml

        * Open ```development.yml``` and fill out the necessary parameters

        * Create your database and sync

        * Start the project's development server

* Applications

    * ~~**ballot_initiatives**~~
        * ~~[Application](/ballot_initiatives)~~
        * ~~[Documentation]()~~

    * ~~**cali_water**~~
        * [Application](/cali_water)
        * ~~[Documentation]()~~

    * **election_profiles**
        * [Application](/election_profiles)
        * ~~[Documentation]()~~

    * **maplight_finance**
        * [Application](/maplight_finance)
        * [Documentation](https://github.com/SCPR/accountability-tracker/wiki/Maplight-Finance)

* Project Development & Scoping
    * [Code: Scraping Reference](https://github.com/SCPR/accountability-tracker/wiki/Code:-Scraping-Reference)
    * [Design: Card Data Points](https://github.com/SCPR/accountability-tracker/wiki/Design:-Card-Data-Points)
    * [Editorial: Questions Data Queries](https://github.com/SCPR/accountability-tracker/wiki/Editorial:-Questions-Data-Queries)
    * [Scoping: Ballot Initiative Tracker](https://github.com/SCPR/accountability-tracker/wiki/Scoping:-Ballot-Initiative-Tracker)
    * [Usage: Embedding campaign contribution cards](https://github.com/SCPR/accountability-tracker/wiki/Usage:-Embedding-campaign-contribution-cards)