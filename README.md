# scheduling-heLP

## Synopsis

A Python script that assigns people to timeslots for you

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

1. Copy and fill in [`availability.csv`](sample/availability.csv) with each person's availability in each timeslot.

    Columns of this CSV file are the timeslots, and rows are the people being scheduled into the timeslots. For each `(person, timeslot)` pair, `person` should indicate their availability for `timeslot` (either `Preferred`, `Available`, or `Not available`).

2. Copy and fill in [`slot_info.csv`](sample/slot_info.csv) with information about each slot.

    Rows of this CSV file are slots, and columns are additional pieces of information that should be provided about each timeslot. The names of the timeslots must exactly match the column names in [`availability.csv`](sample/availability.csv). Additional slot information that should be provided is as follows:

    - `Role name - Capacity` - the number of people with role `Role name` that can be assigned to this timeslot. If there are _n_ possible roles for people, then there should be _n_ `Role name - Capacity` columns. These columns can appear in any order.

3. Copy and fill out [`people_info.csv`](sample/people_info.csv) with information about each person. 

    Rows of this CSV file are people, and columns are additional pieces of information that should be provided about each person. The names of the timeslots must exactly match the row names in [`availability.csv`](sample/availability.csv). Additional person information that should be provided is as follows:
    
    - `Role` - This person's role. If there is only one possible role, then a generic role like `Person` suffices. Possible roles might include `Teacher`, `Student`, or `Tutor`.
    - `Maximum assignments` - The maximum number of slots to which this person should be assigned. If each person should only be assigned to 1 slot, then `Maximum assignments` is `1`. If a person can be assigned to at most _n_ slots, then `Maximum assignments` is `n`.

**CSV files can also be copied from [here](https://docs.google.com/spreadsheets/d/1pGjQOtGLkkmwrhMt3qo9vKZll6U0eX4BNYSKmy_YM-s/edit#gid=176279976).**

## Running the script

    $ python main.py <availaibility.csv> <slot_info.csv> <people_info.csv>
    
## Important stipulations

This script is not magic 🎇. It is backed by a [linear program](https://en.wikipedia.org/wiki/Linear_programming). Here is additional information about how the script works "under the hood", included with the goal of clarifying what this script _can_ and _cannot_ do. 

- The CSV files that you provide are used to create the **constraints** for the linear program. These constraints are used to construct a region of feasible solutions (i.e., possible schedules). 
- If some slots are marked as `Preferred` by your participants, then the program **selects the feasible solution that is "most preferred"**. If no slots are marked as `Preferred` by any of your participants, then the program selects any feasible solution. 
- If your constraints produce a linear program with an **infeasible region**, then you must "relax" constaints until there is a feasible region. How might you relax constraints? Your first step should probably be to ask your participants to re-assess (and hopefully increase) their availability during your slots. If the region is still infeasible, then you might increase the number of participants in each role allowed in each slot.
    - Unfortunately, the answer to "_Why_ is my LP's region infeasible?" is often not as clear as we might want. Future versions of this project might make suggestions as to how to make the region feasible, but the current version does not.
- This script operates on the assumption that **all slots are temporally independent**. That is, Person 1 should be able to be scheduled into both Slot 1 and Slot 2 without consequence (i.e., Slot 1 and Slot 2 should not be at the same time in "real life".)
    - If you do want to accommodate real-life slots that are at the same time, combine the real-life slots into a single slot with a capacity that is the sum of the real-life slots' capacities.
- If you aspire to use this program to optimally select from a set of possible real-life slots, this script will not necessarily produce a set of slots that are "entirely full" or "entirely empty". For example, if you are scheduling 8 people (marked by `x`'s) into 5 2-person slots...

    |Slot 1|Slot 2|Slot 3|Slot 4|Slot 5|
    |------|------|------|------|------|
    |      |      |      |      |      |
    |      |      |      |      |      |
    
    ...then you may get a less-desirable assignment with some half-filled slots...
    
    |Slot 1|Slot 2|Slot 3|Slot 4|Slot 5|
    |------|------|------|------|------|
    |   x  |  x   |  x   |  x   |  x   |
    |   x  |      |      |  x   |  x   |
    
    ...instead of a more-desirable assignment where every slot is empty or full.
    
    |Slot 1|Slot 2|Slot 3|Slot 4|Slot 5|
    |------|------|------|------|------|
    |   x  |      |  x   |  x   |  x   |
    |   x  |      |  x   |  x   |  x   |

    If a less-desirable assignment occurs, then you should remove one of the not-full slots from the set of possible slots and re-run the script with the updated CSV files.

## Contact

If you find bugs or have suggestions, please open an Issue, and I will address it ASAP. Thanks!

