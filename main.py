import csv
import node
from shift_converter import *
from datetime import *

def schedule_forward_pass(node, earliest_date, holidays, nodes):
    node.f.write("Scheduling %s\n" % (node.name))
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

    #TODO Set the ES of this job to the first working shift after the date found in the previous step
    (node.es_date, node.es_shift) = find_next_working_date_shift(node, latest_finish, latest_shift, holidays)

    (node.ef_date, node.ef_shift) = calc_finish_date_shift(node, node.es_date, node.es_shift, holidays)

    schedule_successors(node, earliest_date, holidays, nodes)
            
#Finds the next working shift for the node, not including the date/shift that is passed in
def find_next_working_date_shift(node, prior_date, prior_shift, holidays):
    #print (dateutil.parser.parse("1/2/24").weekday())

    if prior_shift >= 3:
        prior_shift = 1
        next_date = prior_date + timedelta(days = 5)
    else:
        next_shift = prior_shift + 1

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

    #TODO Keep incrementing the EF date forward until the DU between ES and EF equals RDU

    return (finish_date, start_shift)
    
def schedule_successors(node, earliest_date, holidays, nodes):
    for n in node.successors:
        if nodes[n].unsched_pred_count == 1:
            schedule_forward_pass(nodes[n], earliest_date, holidays, nodes)
        else:
            nodes[n].decr_unsched_pred_count()

print(date.today())
print(MINYEAR)

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

#TODO Get file names from a variables file that will not be version controlled.
f = open("variables.txt", "r")
nodes_file = f.readline().strip()
links_file = f.readline().strip()

nodes = {}

with open(nodes_file, newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(file_reader)
    row_num = 1
    
    nodes = {}
    
    for row in file_reader:
        #print(', '.join(row))
        new_node = node.Node(row[ID_COL], int(row[RDU_COL]), int(row[CALNUM_COL]))
        
        #TODO Add the rest of the fields to new_node if they exist
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
        
with open(links_file, newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(file_reader)
    
    for row in file_reader:
        nodes[row[0]].add_succ(row[1])
        nodes[row[1]].add_pred(row[0])
        
#test_clear_nodes(nodes)

#TODO Create holiday manager

for n in nodes:
    if nodes[n].unsched_pred_count == 0:
        schedule_forward_pass(nodes[n], date.today(), [], nodes)
        
for n in nodes:
    print(nodes[n])
    if nodes[n].forward_scheduled == False:
        print("Unscheduled node: %s" % (nodes[n]))