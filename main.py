import csv
import node

#TODO Get file names from a variables file that will not be version controlled.
f = open("variables.txt", "r")
nodes_file = f.readline().strip()
links_file = f.readline().strip()

nodes = {}

with open(nodes_file, newline='') as csvfile:
    file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(file_reader)
    #row_num = 1
    
    nodes = {}
    
    for row in file_reader:
        #print(', '.join(row))
        new_node = node.Node(row[1], row[3], row[8])
        
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
        nodes[n].schedule_forward_pass('', [], nodes)
        #print(nodes[n])
        
for n in nodes:
    if nodes[n].forward_scheduled == False:
        print("Unscheduled node: %s" % (nodes[n]))