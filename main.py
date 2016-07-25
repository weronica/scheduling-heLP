import csv

from pulp import *

DEFAULT_PRIORITY = 1
DEFAULT_CAPACITY = 2
DEFAULT_MUST_BE_FILLED = False
PRIORITY_KEY = 'priority'
CAPACITY_KEY = 'capacity'
MUST_BE_FILLED_KEY = 'must be filled'
AVAILABLE_STRING = 'available'
PREFERRED_STRING = 'preferred'


def main():
    availability_csv_filename = sys.argv[1]
    if len(sys.argv) == 3:
        slot_info_csv_filename = sys.argv[2]
    else:
        slot_info_csv_filename = None

    people_names = []  # People names.
    slot_names = []  # OH assignment names.
    slot_info = {}
    coefficients = []
    variables = []

    # Extract row names, column names, and coefficients from CSV file.
    with open(availability_csv_filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        header_row = next(csv_reader)
        for i, slot_name in enumerate(header_row[1:]):
            slot_names.append(slot_name)

        for i, row in enumerate(csv_reader):
            person_name = row[0]
            people_names.append(person_name)

            # Convert to lowercase.
            row = [x.lower() for x in row]

            coefficients_row = []
            for availability in row[1:]:
                coefficient = 0
                if availability == AVAILABLE_STRING:
                    coefficient = 1
                elif availability == PREFERRED_STRING:
                    coefficient = 2
                coefficients_row.append(coefficient)
            coefficients.append(coefficients_row)

    # Insert default slot info.
    for slot_name in slot_names:
        slot_info[slot_name] = {}
        slot_info[slot_name][PRIORITY_KEY] = DEFAULT_PRIORITY
        slot_info[slot_name][CAPACITY_KEY] = DEFAULT_CAPACITY
        slot_info[slot_name][MUST_BE_FILLED_KEY] = DEFAULT_MUST_BE_FILLED

    # Extract slot info.
    if slot_info_csv_filename is not None:
        with open(slot_info_csv_filename, 'rb') as csv_infile:
            csv_reader = csv.reader(csv_infile)

            header_row = [x.lower() for x in next(csv_reader)]
            priority_index = header_row.index(PRIORITY_KEY)
            capacity_index = header_row.index(CAPACITY_KEY)
            must_be_filled_index = header_row.index(MUST_BE_FILLED_KEY)

            for i, row in enumerate(csv_reader):
                slot_name = row[0]

                # Convert to lowercase.
                row = [x.lower() for x in row]
                if priority_index != -1:
                    slot_info[slot_name][PRIORITY_KEY] = \
                        float(row[priority_index])
                if capacity_index != -1:
                    slot_info[slot_name][CAPACITY_KEY] = \
                        int(row[capacity_index])
                if must_be_filled_index != -1:
                    if row[must_be_filled_index] == 'x':
                        slot_info[slot_name][MUST_BE_FILLED_KEY] = True
                    else:
                        slot_info[slot_name][MUST_BE_FILLED_KEY] = False

    # Construct LP problem.
    problem = LpProblem('16fa OH Assignments', LpMaximize)
    num_rows = len(people_names)
    num_columns = len(slot_names)

    # Construct LP variables.
    for i, row in enumerate(coefficients):
        variables.append([0] * len(row))
        for j, cell in enumerate(row):
            variables[i][j] = LpVariable(
                ('x_(%d,%d)' % (i, j)),
                0,
                1,
                LpInteger
            )

    # Construct objective function.
    d = {}
    for i in range(0, num_rows):
        for j in range(0, num_columns):
            d[variables[i][j]] = coefficients[i][j]
    exp = LpAffineExpression(d)
    problem.objective = exp

    # Construct constraints.

    # At most 2 people can be assigned to each OH slot.
    for j in range(0, num_columns):
        d = {}
        for i in range(0, num_rows):
            d[variables[i][j]] = 1

        capacity = slot_info[slot_names[j]][CAPACITY_KEY]
        sense = LpConstraintLE
        if slot_info[slot_names[j]][MUST_BE_FILLED_KEY]:
            sense = LpConstraintEQ

        exp = LpAffineExpression(d)
        constraint = LpConstraint(
            e=exp,
            sense=sense,
            name='At most 2 people in slot %d' % j,
            rhs=capacity
        )
        problem += constraint

    # Everyone must be assigned to at most 1 slot.
    for i in range(0, num_rows):
        d = {}
        for j in range(0, num_columns):
            d[variables[i][j]] = 1
        exp = LpAffineExpression(d)
        constraint = LpConstraint(
            e=exp,
            sense=LpConstraintEQ,
            name='Person %i is assigned to exactly 1 slot' % i,
            rhs=1
        )
        problem += constraint

    # Everyone must be assigned to a slot in which they are available.
    for i in range(0, num_rows):
        d = {}
        for j in range(0, num_columns):
            d[variables[i][j]] = coefficients[i][j]
        exp = LpAffineExpression(d)
        constraint = LpConstraint(
            e=exp,
            sense=LpConstraintGE,
            name='Person %i is assigned to a slot when they are available' % i,
            rhs=1
        )
        problem += constraint

    # Save LP to file.
    problem.writeLP('assignments.lp')

    # Try to solve LP.
    problem.solve()

    print 'Status: %s\n' % LpStatus[problem.status]

    if LpStatus[problem.status] == 'Optimal':

        print '** PEOPLE ASSIGNMENTS:'
        for i in range(0, num_rows):
            for j in range(0, num_columns):
                if int(value(variables[i][j])) == 1:
                    print '%s: %s' % (people_names[i].ljust(20), slot_names[j])
        print '\n'

        print '** SLOT ASSIGNMENTS:'
        for j in range(0, num_columns):
            print '%s:' % slot_names[j]
            for i in range(0, num_rows):
                if int(value(variables[i][j])) == 1:
                    print '- %s' % people_names[i]
            print '\n'


if __name__ == "__main__":
    main()