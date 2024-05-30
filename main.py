import csv
import node
from shift_converter import *
from datetime import *

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
        new_node = node.Node(row[ID_COL], row[RDU_COL], row[CALNUM_COL])
        
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

for n in nodes:
    if nodes[n].unsched_pred_count == 0:
        nodes[n].schedule_forward_pass(date.today(), [], nodes)
        
for n in nodes:
    print(nodes[n])
    if nodes[n].forward_scheduled == False:
        print("Unscheduled node: %s" % (nodes[n]))