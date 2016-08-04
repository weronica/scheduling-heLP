import csv
import re

from pulp import *

DEFAULT_PRIORITY = 1
DEFAULT_CAPACITY = 2
DEFAULT_MUST_BE_FILLED = False
DEFAULT_MAX_ASSIGNMENTS = 1
DEFAULT_ROLE = 'Person'
NAME_KEY = 'name'
INDEX_KEY = 'index'
ROLE_KEY = 'role'
CAPACITY_KEY = 'capacity'
MAX_ASSIGNMENTS_KEY = 'maximum-assignments'
AVAILABLE_STRING = 'available'
PREFERRED_STRING = 'preferred'
NOT_AVAILABLE_STRING = 'not available'


def construct_components_from_csv(availability_csv_filename,
                                  slot_info_csv_filename,
                                  person_info_csv_filename):
    # Data structures to fill.
    people_names = []
    people_info = {}
    slot_names = []
    slot_info = {}
    role_names = set()
    availabilities = []

    # Extract row names, column names, and coefficients from CSV file.
    with open(availability_csv_filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        header_row = next(csv_reader)
        for i, pretty_slot_name in enumerate(header_row[1:]):
            ugly_slot_name = uglify_name(pretty_slot_name)
            slot_names.append(ugly_slot_name)
            slot_info[ugly_slot_name] = {}
            slot_info[ugly_slot_name][NAME_KEY] = pretty_slot_name
            slot_info[ugly_slot_name][CAPACITY_KEY] = {}

        for i, row in enumerate(csv_reader):
            pretty_person_name = row[0]
            ugly_person_name = uglify_name(pretty_person_name)

            people_names.append(ugly_person_name)
            people_info[ugly_person_name] = {}
            people_info[ugly_person_name][NAME_KEY] = pretty_person_name
            people_info[ugly_person_name][INDEX_KEY] = i

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
            availabilities.append(coefficients_row)

    # Insert default slot capacity info.
    for ugly_slot_name in slot_names:
        for role in role_names:
            slot_info[ugly_slot_name][CAPACITY_KEY][role] = DEFAULT_CAPACITY
        slot_info[ugly_slot_name][CAPACITY_KEY][DEFAULT_ROLE] = \
            DEFAULT_CAPACITY

    # Insert default role, maximum assignments info.
    for ugly_person_name in people_names:
        people_info[ugly_person_name][ROLE_KEY] = DEFAULT_ROLE
        people_info[ugly_person_name][MAX_ASSIGNMENTS_KEY] = \
            DEFAULT_MAX_ASSIGNMENTS
    role_names.add(DEFAULT_ROLE)

    # Extract slot info.
    if slot_info_csv_filename is not None:
        with open(slot_info_csv_filename, 'rb') as csv_infile:
            csv_reader = csv.reader(csv_infile)

            header_row = next(csv_reader)
            capacity_indices = {}
            for i, column_name in enumerate(header_row):
                if column_name.split()[-1].lower() == CAPACITY_KEY:
                    role_name = column_name.split('-')[0].strip()
                    capacity_indices[role_name] = i

            for i, row in enumerate(csv_reader):
                pretty_slot_name = row[0]
                ugly_slot_name = uglify_name(pretty_slot_name)

                # Convert to lowercase.
                row = [x.lower() for x in row]
                for role_name, capacity_index in capacity_indices.iteritems():
                    slot_info[ugly_slot_name][CAPACITY_KEY][role_name] = \
                        int(row[capacity_index])

    # Extract person info.
    if person_info_csv_filename is not None:
        with open(person_info_csv_filename, 'rb') as csv_infile:
            csv_reader = csv.reader(csv_infile)

            header_row = [x.lower() for x in next(csv_reader)]
            role_index = header_row.index('role')
            max_assignments_index = header_row.index('maximum assignments')

            for i, row in enumerate(csv_reader):
                pretty_person_name = row[0]
                ugly_person_name = uglify_name(pretty_person_name)

                if role_index != -1:
                    role = row[role_index]
                    people_info[ugly_person_name][ROLE_KEY] = role
                    role_names.add(role)
                if max_assignments_index != -1:
                    people_info[ugly_person_name][MAX_ASSIGNMENTS_KEY] = \
                        int(row[max_assignments_index])

    return people_names, people_info, slot_names, slot_info, role_names, \
        availabilities


def find_schedule(people_names, people_info, slot_names, slot_info, role_names,
                  availabilities, lp_file_name=None):
    # Construct LP problem.
    problem = LpProblem('Schedule', LpMaximize)
    variables = []
    num_rows = len(people_names)
    num_columns = len(slot_names)

    # Construct LP variables.
    for i, row in enumerate(availabilities):
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
            d[variables[i][j]] = availabilities[i][j]
    exp = LpAffineExpression(d)
    problem.objective = exp

    # Construct constraints.

    # Capacity constraints for each slot and for each role.
    for j in range(0, num_columns):  # Slots.
        for role in role_names:
            d = {}
            for i in range(0, num_rows):  # People.
                person = people_names[i]
                if people_info[person][ROLE_KEY] == role:
                    d[variables[i][j]] = 1

            capacity = int(slot_info[slot_names[j]][CAPACITY_KEY][role])

            exp = LpAffineExpression(d)
            constraint = LpConstraint(
                e=exp,
                sense=LpConstraintLE,
                name='At most %d people with role %s in slot %d' %
                     (capacity, role, j),
                rhs=capacity
            )
            problem += constraint

    # Person constraints for total number of slots to which they can be
    # assigned.
    for i in range(0, num_rows):  # People.
        person = people_names[i]
        max_assignments = int(people_info[person][MAX_ASSIGNMENTS_KEY])
        d = {}
        for j in range(0, num_columns):  # Slots.
            d[variables[i][j]] = 1
        exp = LpAffineExpression(d)
        constraint = LpConstraint(
            e=exp,
            sense=LpConstraintLE,
            name='%s is assigned to at most %d slot(s)' %
                 (person, max_assignments),
            rhs=max_assignments
        )
        problem += constraint

    # Everyone must be assigned to a slot in which they are available.
    for i in range(0, num_rows):  # People.
        for j in range(0, num_columns):  # Slots.
            d = {variables[i][j]: 1}
            exp = LpAffineExpression(d)
            constraint = LpConstraint(
                e=exp,
                sense=LpConstraintLE,
                name='Person %d is assigned to a %d when they are available' %
                     (i, j),
                rhs=availabilities[i][j]
            )
            problem += constraint

    # If requested, save LP to file.
    if lp_file_name is not None:
        problem.writeLP(str(lp_file_name) + '.lp')

    # Try to solve LP.
    problem.solve()

    return variables, LpStatus[problem.status]


def uglify_name(pretty_name):
    ugly_name = pretty_name.replace(' ', '-').lower()
    re.sub(r'[^\w]', '', ugly_name)
    return ugly_name
