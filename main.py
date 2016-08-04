from scheduling_help import *

NUM_ARGUMENTS = 4


def main():
    if len(sys.argv) != NUM_ARGUMENTS:
        print >> sys.stderr, '** usage: python main.py <availaibility.csv> ' \
                             '<slot_info.csv> ''<people_info.csv>'
        exit(1)
    availability_csv_filename = sys.argv[1]
    slot_info_csv_filename = sys.argv[2]
    person_info_csv_filename = sys.argv[3]

    # Extract constraints from CSV file.
    people_names, people_info, slot_names, slot_info, role_names, \
        availabilities = construct_components_from_csv(
            availability_csv_filename=availability_csv_filename,
            slot_info_csv_filename=slot_info_csv_filename,
            person_info_csv_filename=person_info_csv_filename
        )

    # Construct and solve linear program.
    variables, status = find_schedule(
        people_names=people_names,
        people_info=people_info,
        slot_names=slot_names,
        slot_info=slot_info,
        role_names=role_names,
        availabilities=availabilities
    )

    # Could an optimal solution be found?
    print 'Status: %s\n' % status

    # Print schedule.
    if status == 'Optimal':

        print '** PEOPLE ASSIGNMENTS:'
        for i in range(0, len(variables)):
            for j in range(0, len(variables[i])):
                if int(value(variables[i][j])) == 1:
                    pretty_person_name = people_info[people_names[i]][NAME_KEY]
                    pretty_slot_name = slot_info[slot_names[j]][NAME_KEY]
                    print '%s: %s' % \
                          (pretty_person_name.ljust(20), pretty_slot_name)
        print '\n'

        print '** SLOT ASSIGNMENTS:'
        for j in range(0, len(variables[0])):
            pretty_slot_name = slot_info[slot_names[j]][NAME_KEY]
            print '%s:' % pretty_slot_name
            for i in range(0, len(variables)):
                if int(value(variables[i][j])) == 1:
                    pretty_person_name = people_info[people_names[i]][NAME_KEY]
                    role = people_info[people_names[i]][ROLE_KEY]
                    print '- %s (%s)' % (pretty_person_name, role)
            print '\n'


if __name__ == '__main__':
    main()