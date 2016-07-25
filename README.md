# scheduling-heLP

## Synopsis

A Python script that assigns busy people into limited timeslots for you.

## Setting up

##### Clone the repo

    $ git clone git@github.com:weronica/scheduling-heLP.git
    $ cd scheduling-heLP

##### Initialize a virtualenv

    $ pip install virtualenv
    $ virtualenv env
    $ source env/bin/activate

##### Install the dependencies

    $ pip install -r requirements.txt

##### Create CSV files

Copy and fill in [availability.csv](data/availability.csv) with information about each person's availability.

(Option) Copy and fill out [slot_info.csv](data/csv_info.csv) with information about the timeslots.

##### Run the program

    # python main.py <availaibility.csv> [slot_info.csv]
