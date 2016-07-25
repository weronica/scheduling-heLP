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

1. Copy and fill in [`availability.csv`](data/availability.csv) with each person's availability in each timeslot.

The columns of the CSV file are the timeslots, and the rows are the people being scheduled into the timeslots. For each `(person, timeslot)` pair, `person` should indicate their availability for `timeslot` (either "Preferred", "Available", or "Not available").

2. (Optional) Copy and fill in [`slot_info.csv`](data/csv_info.csv) with information about each timeslots.

The rows of the CSV file are the timeslots, and the columns are additional pieces of information that can be provided about each timeslot. The names of the timeslots must exactly match the column names in `availability.csv`. Additional timeslot information that can be provided includes:

- `Priority` - how important it is that this timeslot be filled to capacity. A lower number indicates a lower priority and vice versa.
- `Capacity` - the number of people that can be assigned to this timeslot.
- `Must be filled` - whether the timeslot should be filled to capacity. If so, mark with an `X`; otherwise, leave this column blank.

All of these columns are optional. Any subset can appear in any order in `slot_info.csv`.

##### Run the program

    $ python main.py <availaibility.csv> [slot_info.csv]

If the given constraints produce a linear program with an infeasible region, then you must relax constaints until there is a feasible region.
