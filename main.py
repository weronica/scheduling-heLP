import csv

from pulp import *


PERSON_NAME_COLUMN_NUM = 1
AVAILABILITY_START_NUM = 2
AVAILABILITY_END_NUM = 17


def main():
    people_names = []  # People names.
    slot_names = []  # OH assignment names.
    slot_info = {}
    coefficients = []
    variables = []

    # Extract row names, column names, and coefficients from CSV file.
    with open('data/oh_preferences.csv', 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        header_column = next(csv_reader)
        start = AVAILABILITY_START_NUM
        end = AVAILABILITY_END_NUM + 1
        for i, column_name in enumerate(header_column[start:end]):
            splice_start = column_name.index('[') + 1
            splice_end = column_name.index(']')
            slot_name = column_name[splice_start:splice_end]
            slot_names.append(slot_name)

        for i, row in enumerate(csv_reader):
            person_name = row[PERSON_NAME_COLUMN_NUM]
            people_names.append(person_name)

            start = AVAILABILITY_START_NUM
            end = AVAILABILITY_END_NUM + 1
            coefficients_row = []
            for availability in row[start:end]:
                coefficient = 0
                if availability == 'Available':
                    coefficient = 1
                elif availability == 'Preferred':
                    coefficient = 2
                coefficients_row.append(coefficient)
            coefficients.append(coefficients_row)

    # Extract slot info.
    with open('data/slot_info.csv', 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)
        next(csv_reader)

        for i, row in enumerate(csv_reader):
            slot_name = row[0]
            slot_info[slot_name] = {}
            slot_info[slot_name]['index'] = slot_names.index(slot_name)
            slot_info[slot_name]['priority'] = float(row[1])
            slot_info[slot_name]['capacity'] = int(row[2])
            if int(row[3]) == 1:
                slot_info[slot_name]['must_be_filled'] = True
            else:
                slot_info[slot_name]['must_be_filled'] = False

    # Normalize priorities.

    # Constrct LP problem.
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

        capacity = slot_info[slot_names[j]]['capacity']
        sense = LpConstraintLE
        if slot_info[slot_names[j]]['must_be_filled']:
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
    problem.writeLP("data/oh_assignments.lp")

    # Try to solve LP.
    problem.solve()

    print 'Status: %s\n' % LpStatus[problem.status]

    if LpStatus[problem.status] == 'Optimal':

        print '** TA ASSIGNMENTS:'
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