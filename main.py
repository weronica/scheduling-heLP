import csv
import re

from pulp import *

DEFAULT_PRIORITY = 1
DEFAULT_CAPACITY = 2
DEFAULT_MUST_BE_FILLED = False
NAME_KEY = 'name'
INDEX_KEY = 'index'
ROLE_KEY = 'role'
CAPACITY_KEY = 'capacity'
AVAILABLE_STRING = 'available'
PREFERRED_STRING = 'preferred'
NOT_AVAILABLE_STRING = 'not available'


def main():
    availability_csv_filename = sys.argv[1]
    if len(sys.argv) == 3:
        slot_info_csv_filename = sys.argv[2]
    else:
        slot_info_csv_filename = None

    people_names = set()
    people_info = {}
    slot_names = set()
    slot_info = {}
    role_names = set()
    coefficients = []
    variables = []

    # Extract row names, column names, and coefficients from CSV file.
    with open(availability_csv_filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        header_row = next(csv_reader)
        for i, pretty_slot_name in enumerate(header_row[2:]):
            ugly_slot_name = uglify_name(pretty_slot_name)
            slot_names.add(ugly_slot_name)
            slot_info[ugly_slot_name] = {}
            slot_info[ugly_slot_name][NAME_KEY] = pretty_slot_name
            slot_info[ugly_slot_name][CAPACITY_KEY] = {}

        for i, row in enumerate(csv_reader):
            pretty_person_name = row[0]
            person_role = row[1]
            ugly_person_name = uglify_name(pretty_person_name)

            people_names.add(ugly_person_name)
            people_info[ugly_person_name] = {}
            people_info[ugly_person_name][NAME_KEY] = pretty_person_name
            people_info[ugly_person_name][ROLE_KEY] = person_role
            people_info[ugly_person_name][INDEX_KEY] = i
            role_names.add(person_role)

            # Convert to lowercase.
            row = [x.lower() for x in row]

            coefficients_row = []
            for availability in row[2:]:
                coefficient = 0
                if availability == AVAILABLE_STRING:
                    coefficient = 1
                elif availability == PREFERRED_STRING:
                    coefficient = 2
                coefficients_row.append(coefficient)
            coefficients.append(coefficients_row)

    # Insert default slot capacity info.
    for ugly_slot_name in slot_names:
        for role in role_names:
            slot_info[ugly_slot_name][CAPACITY_KEY][role] = DEFAULT_CAPACITY

    # Extract slot info.
    if slot_info_csv_filename is not None:
        with open(slot_info_csv_filename, 'rb') as csv_infile:
            csv_reader = csv.reader(csv_infile)

            header_row = [x.lower() for x in next(csv_reader)]
            capacity_indices = {}
            for i, column_name in enumerate(header_row):
                if column_name.split()[-1].lower() == CAPACITY_KEY:
                    role_name = uglify_name(column_name.split('-')[0].strip())
                    capacity_indices[role_name] = i

            for i, row in enumerate(csv_reader):
                pretty_slot_name = row[0]
                ugly_slot_name = uglify_name(pretty_slot_name)

                # Convert to lowercase.
                row = [x.lower() for x in row]
                for role_name, capacity_index in capacity_indices.iteritems():
                    slot_info[ugly_slot_name][CAPACITY_KEY][role_name] = row[capacity_index]

    # # Construct LP problem.
    # problem = LpProblem('Schedule', LpMaximize)
    # num_rows = len(people_names)
    # num_columns = len(slot_names)
    #
    # # Construct LP variables.
    # for i, row in enumerate(coefficients):
    #     variables.append([0] * len(row))
    #     for j, cell in enumerate(row):
    #         variables[i][j] = LpVariable(
    #             ('x_(%d,%d)' % (i, j)),
    #             0,
    #             1,
    #             LpInteger
    #         )
    #
    # # Construct objective function.
    # d = {}
    # for i in range(0, num_rows):
    #     for j in range(0, num_columns):
    #         d[variables[i][j]] = coefficients[i][j]
    # exp = LpAffineExpression(d)
    # problem.objective = exp
    #
    # # Construct constraints.
    #
    # # At most 2 people can be assigned to each OH slot.
    # for j in range(0, num_columns):
    #     d = {}
    #     for i in range(0, num_rows):
    #         d[variables[i][j]] = 1
    #
    #     capacity = slot_info[slot_names[j]][CAPACITY_KEY]
    #     sense = LpConstraintLE
    #     if slot_info[slot_names[j]][MUST_BE_FILLED_KEY]:
    #         sense = LpConstraintEQ
    #
    #     exp = LpAffineExpression(d)
    #     constraint = LpConstraint(
    #         e=exp,
    #         sense=sense,
    #         name='At most 2 people in slot %d' % j,
    #         rhs=capacity
    #     )
    #     problem += constraint
    #
    # # Everyone must be assigned to at most 1 slot.
    # for i in range(0, num_rows):
    #     d = {}
    #     for j in range(0, num_columns):
    #         d[variables[i][j]] = 1
    #     exp = LpAffineExpression(d)
    #     constraint = LpConstraint(
    #         e=exp,
    #         sense=LpConstraintLE,
    #         name='Person %i is assigned to exactly 1 slot' % i,
    #         rhs=1
    #     )
    #     problem += constraint
    #
    # # Everyone must be assigned to a slot in which they are available.
    # for i in range(0, num_rows):
    #     d = {}
    #     for j in range(0, num_columns):
    #         d[variables[i][j]] = coefficients[i][j]
    #     exp = LpAffineExpression(d)
    #     constraint = LpConstraint(
    #         e=exp,
    #         sense=LpConstraintGE,
    #         name='Person %i is assigned to a slot when they are available' % i,
    #         rhs=1
    #     )
    #     problem += constraint
    #
    # # Save LP to file.
    # problem.writeLP('assignments.lp')
    #
    # # Try to solve LP.
    # problem.solve()
    #
    # print 'Status: %s\n' % LpStatus[problem.status]
    #
    # if LpStatus[problem.status] == 'Optimal':
    #
    #     print '** PEOPLE ASSIGNMENTS:'
    #     for i in range(0, num_rows):
    #         for j in range(0, num_columns):
    #             if int(value(variables[i][j])) == 1:
    #                 print '%s: %s' % (people_names[i].ljust(20), slot_names[j])
    #     print '\n'
    #
    #     print '** SLOT ASSIGNMENTS:'
    #     for j in range(0, num_columns):
    #         print '%s:' % slot_names[j]
    #         for i in range(0, num_rows):
    #             if int(value(variables[i][j])) == 1:
    #                 print '- %s' % people_names[i]
    #         print '\n'


def uglify_name(pretty_name):
    ugly_name = pretty_name.replace(' ', '-').lower()
    re.sub(r'[^\w]', '', ugly_name)
    return ugly_name


if __name__ == "__main__":
    main()