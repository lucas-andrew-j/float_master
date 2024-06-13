import csv
import node
from shift_converter import *
from datetime import *
from holiday_handler import *

ID_COL = 1
RDU_COL = 4
PS_COL = 5
CALNUM_COL = 9
AS_COL = 10
AF_COL = 11
ES_COL = 12
EF_COL = 13
LS_COL = 14
SS_COL = 23

DATE_COLON_INDEX = 11

fw = open("log.txt", "a")
fw.write("\n###### START OF NEW RUN #######\n")

def main():
    #TODO Get file names from a variables file that will not be version controlled.
    fr = open("variables.txt", "r")
    nodes_file = fr.readline().strip()
    links_file = fr.readline().strip()

    nodes = {}
    
    print('Scraping nodes')
    with open(nodes_file, newline='') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(file_reader)
        row_num = 1

        nodes = {}

        for row in file_reader:
            #print(', '.join(row))
            new_node = node.Node(row[ID_COL], int(row[RDU_COL]), int(row[CALNUM_COL]))

            #TODO Add the rest of the fields to new_node if they exist
            if row[ES_COL] != '':
                date_time_parts = row[ES_COL].split(':')
                new_node.set_es_with_time(date_time_parts[0], date_time_parts[1])
                
            if row[EF_COL] != '':
                date_time_parts = row[EF_COL].split(':')
                new_node.set_ef_with_time(date_time_parts[0], date_time_parts[1])
                
            if row[AS_COL] != '':
                date_time_parts = row[AS_COL].split(':')
                new_node.set_as_with_time(date_time_parts[0], date_time_parts[1])
                
            if row[AF_COL] != '':
                date_time_parts = row[AF_COL].split(':')
                new_node.set_af_with_time(date_time_parts[0], date_time_parts[1])
            
            if row[PS_COL] != '':
                date_time_parts = row[PS_COL].split(':')
                new_node.set_ps_with_time(date_time_parts[0], date_time_parts[1])

            if row[SS_COL] != '':
                date_time_parts = row[SS_COL].split(':')
                new_node.set_ss_with_time(date_time_parts[0], date_time_parts[1])

            #print(row[AS_COL][DATE_COLON_INDEX + 1:])
            #convert_start_to_shift(row[AS_COL][DATE_COLON_INDEX + 1:])
            nodes[row[1]] = new_node

            #if row_num == 100:
            #    break
            #else:
            #    row_num = row_num + 1

    print('Linking nodes')
    with open(links_file, newline='') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(file_reader)

        for row in file_reader:
            # TODO Need to change these to also pass booleans indicating if the predecessor is already finished.
            # Don't want to count predecessors are unscheduled if they are already complete.
            nodes[row[0]].add_succ(row[1])
            nodes[row[1]].add_pred(row[0])

    #test_clear_nodes(nodes)

    holidays = Holiday_Handler(2020, 2030)
    start_date = dateutil.parser.parse("10/17/2023").date()
    
    # TODO Need to go thorugh all the nodes and calculate finish dates for the ones that have a start date already.
    print('Calculating finishes for started nodes')
    for n in nodes:
        if nodes[n].as_date != '' and nodes[n].af_date == '':
            calc_finish_date_shift(nodes[n], nodes[n].es_date, nodes[n].es_shift, holidays)
            fw.write('Calculating finish date for %s\n' % (nodes[n].name))
    
    print('Performing forward pass')
    for n in nodes:
        if nodes[n].unsched_pred_count == 0:
            # TODO When I have verified that the forward pass is correct, this will be removed if it takes any
            # considerable time. If it's really fast, it would be good to still include this here for comparing
            # with the values that we get from the Concerto export.
            schedule_forward_pass(nodes[n], start_date, holidays, nodes)

    for n in nodes:
        fw.write('%s\n' % (nodes[n]))
        if nodes[n].forward_scheduled == False:
            fw.write("Unscheduled node: %s\n" % (nodes[n]))
            
    print('Complete')

def schedule_forward_pass(node, earliest_date, holidays, nodes):
    fw.write("Scheduling %s\n" % (node.name))
    node.forward_scheduled = True
    #TODO Schedule this node

    latest_finish = earliest_date
    latest_shift = 1
    for n in node.predecessors:
        if nodes[n].af_date != '' and nodes[n].af_date > latest_finish:
            latest_finish = nodes[n].af_date
            latest_shift = nodes[n].af_shift
        elif nodes[n].ef_date != '' and nodes[n].ef_date > latest_finish:
            latest_finish = nodes[n].ef_date
            latest_shift = nodes[n].ef_shift
        elif nodes[n].ef_date == latest_finish:
            latest_shift = max(latest_shift, nodes[n].es_shift)

    #TODO Compare the calculated ES with the ES that we got from the Concerto export
    (node.es_date, node.es_shift) = next_working_date_shift(node, latest_finish, latest_shift, holidays)

    (node.ef_date, node.ef_shift) = calc_finish_date_shift(node, node.es_date, node.es_shift, holidays)

    schedule_successors(node, earliest_date, holidays, nodes)
            
#Finds the next working shift for the node, not including the date/shift that is passed in
#TODO This incorrectly assumes that the job will have the same work week as its predecessors.
    #The latest finish predecessors for this job could be a 27, ending day shift on a Saturday, 
    #while this job is a 25. This algorithm would return Saturday swing shift, when it should return Monday day shift.
def next_working_date_shift(node, prior_date, prior_shift, holidays):
    #print (dateutil.parser.parse("1/2/24").weekday())
    cc_workdays = node.cal_code % 10
    cc_workshifts = node.cal_code // 10
    
    if prior_shift < cc_workshifts:
        return prior_date, prior_shift + 1
    
    prior_shift = 1
    
    # if not able to, move to the first working day
    while holidays.is_holiday(prior_date, node.cal_code) or not prior_date.weekday() < cc_workshifts:
        prior_date = prior_date + timedelta(days = 1)

    return prior_date, prior_shift

def calc_finish_date_shift(node, start_date, start_shift, holidays):
    #TODO Calculate the minimum date that the early finish could be (based on cal_code)
    shifts_per_day = node.cal_code // 10
    days_per_week = node.cal_code % 10
    weekend_days_per_week = 7 - days_per_week

    min_working_days = node.rdu // shifts_per_day
    if days_per_week != 0 and days_per_week != 7:
        min_work_weeks = min_working_days // days_per_week
        min_days = min_working_days + min_work_weeks * weekend_days_per_week
    else:
        min_days = min_working_days

    min_days = timedelta(days = min_days)

    finish_date = start_date + min_days
    
    finish_date = start_date + min_days
    if finish_date > start_date:
        finish_shift = 1
    else:
        finish_shift = start_shift

    #TODO Keep incrementing the EF date forward until the DU between ES and EF equals RDU
    while du_between_workshifts(start_date, start_shift, finish_date, finish_shift, node.cal_code, holidays) < node.rdu:
        #TODO move to next shift
        break

    return (finish_date, start_shift)

def du_between_workshifts(start_date, start_shift, finish_date, finish_shift, cal_code, holidays):
    #TODO Need to make sure that X0 cal_codes are handled here or somewhere else
    shifts_per_day = cal_code // 10
    days_per_week = cal_code % 10
    
    num_days = (finish_date - start_date).days
    num_wkends = num_days // 7
    if start_date.weekday() > finish_date.weekday():
        num_wkends = num_wkends + 1
    
    working_days = num_days + 1 - num_wkends * (7 - days_per_week)
    
    #TODO Does this work when the start and finish dates are the same, or adjacent?
    return (working_days - 2) * shifts_per_day + shifts_per_day - start_shift + 1 + finish_shift
    
def schedule_successors(node, earliest_date, holidays, nodes):
    for n in node.successors:
        if nodes[n].unsched_pred_count == 1:
            schedule_forward_pass(nodes[n], earliest_date, holidays, nodes)
        else:
            nodes[n].decr_unsched_pred_count()

main()