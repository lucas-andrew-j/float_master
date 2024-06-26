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
SES_COL = 23

DATE_COLON_INDEX = 11

mismatches_found = 0

fw = open('log.txt', 'a')
fw.write('\n###### START OF NEW RUN #######\n')

def main():
    fr = open('variables.txt', 'r')
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
                new_node.set_fp_done(True)
            
            if row[PS_COL] != '':
                date_time_parts = row[PS_COL].split(':')
                new_node.set_ps_with_time(date_time_parts[0], date_time_parts[1])

            if row[SES_COL] != '':
                date_time_parts = row[SES_COL].split(':')
                new_node.set_ses_with_time(date_time_parts[0], date_time_parts[1])

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
            nodes[row[0]].add_succ(row[1], nodes[row[1]].af_date != '')
            nodes[row[1]].add_pred(row[0], nodes[row[0]].af_date != '')

    #test_clear_nodes(nodes)

    holidays = Holiday_Handler(2020, 2030)
    start_date = dateutil.parser.parse('06/21/2024').date()
    
    print('Performing forward pass')
    for n in nodes:
        if nodes[n].unsched_pred_count == 0 and nodes[n].get_fp_done() == False:
            # TODO When I have verified that the forward pass is correct, this will be removed if it takes any
            # considerable time. If it's really fast, it would be good to still include this here for comparing
            # with the values that we get from the Concerto export.
            schedule_forward_pass(nodes[n], start_date, holidays, nodes)

    for n in nodes:
        fw.write('%s\n' % (nodes[n]))
        if nodes[n].get_fp_done() == False:
            fw.write('Unscheduled node: %s\n' % (nodes[n]))
    
    global mismatches_found
    print('Mismatches found: %d' % (mismatches_found))
    print('Complete')

def schedule_forward_pass(this_node, earliest_date, holidays, nodes):
    fw.write('Scheduling %s\n' % (this_node.name))
    this_node.forward_scheduled = True
    
    latest_finish = earliest_date
    latest_shift = 1
    
    for n in this_node.predecessors:
        if nodes[n].af_date != '' and nodes[n].af_date > latest_finish:
            latest_finish = nodes[n].af_date
            latest_shift = nodes[n].af_shift
        elif nodes[n].ef_date != '' and nodes[n].ef_date > latest_finish:
            latest_finish = nodes[n].ef_date
            latest_shift = nodes[n].ef_shift
        elif nodes[n].ef_date == latest_finish:
            latest_shift = max(latest_shift, nodes[n].es_shift)

    (es_date, es_shift) = next_working_date_shift(this_node, latest_finish, latest_shift, holidays)
    
    #TODO Need to make sure these are not putting the es_date and es_shift on a weekend or holiday
    #TODO Need to update to make sure that ps and ses are on a later date, or the same date with 
        # a later shift
    if this_node.ps_date != '' and (this_node.ps_date > es_date or (this_node.ps_date == es_date and this_node.ps_shift >= es_shift)):
        es_date = this_node.ps_date
        es_shift = this_node.ps_shift
    if this_node.ses_date != '' and (this_node.ses_date > es_date or (this_node.ses_date == es_date and this_node.ses_shift >= es_shift)):
        es_date = this_node.ses_date
        es_shift = this_node.ses_shift
        
    (es_date, es_shift) = next_working_date_shift_incl(this_node, es_date, es_shift, holidays)

    (ef_date, ef_shift) = calc_finish_date_shift(this_node, es_date, es_shift, holidays)
    global mismatches_found
    if this_node.ef_date.strftime('%y') == this_node.es_date.strftime('%y'):
        if this_node.ef_date != ef_date:
            fw.write('Mismatch between early finish dates: %s\n' % (this_node.name))
            fw.write('\tCalculated EF Date:\t%s\n' % (ef_date))
            fw.write('\tConcerto EF Date:\t%s\n' % (this_node.ef_date))
            fw.write('\tConcerto ES Shift:\t%s\n' % (this_node.es_shift))
            fw.write('\tCalculated ES Date:\t%s\n' % (es_date))
            fw.write('\tConcerto ES Date:\t%s\n' % (this_node.es_date))
            fw.write('\tConcerto RDU:\t\t%s\n' % (this_node.rdu))
            fw.write('\tConcerto Cal Code:\t%s\n' % (this_node.cal_code))
            mismatches_found = mismatches_found + 1
        if this_node.ef_shift != ef_shift:
            fw.write('Mismatch between early finish shifts: %s\n' % (this_node.name))
            fw.write('\tCalculated EF Shift:\t%s\n' % (ef_shift))
            fw.write('\tCalculated EF Date:\t%s\n' % (ef_date))
            fw.write('\tConcerto EF Shift:\t%s\n' % (this_node.ef_shift))
            fw.write('\tConcerto EF Date:\t%s\n' % (this_node.ef_date))
            fw.write('\tConcerto ES Shift:\t%s\n' % (this_node.es_shift))
            fw.write('\tConcerto ES Date:\t%s\n' % (this_node.es_date))
            fw.write('\tConcerto RDU:\t\t%s\n' % (this_node.rdu))
            fw.write('\tConcerto Cal Code:\t%s\n' % (this_node.cal_code))
            mismatches_found = mismatches_found + 1
    this_node.es_date = es_date
    this_node.es_shift = es_shift
    this_node.ef_date = ef_date
    this_node.ef_shift = ef_shift

    schedule_successors(this_node, earliest_date, holidays, nodes)
    
def is_working_day(this_node, date, holidays):
    cc_workdays = this_node.cal_code % 10
    
    if cc_workdays == 0:
        return True
    
    if date.weekday() >= cc_workdays:
        return False
    
    if holidays.is_holiday(date, this_node.cal_code):
        return False
    
    return True
            
#Finds the next working shift for the node, NOT including the date/shift that is passed in
def next_working_date_shift(this_node, prior_date, prior_shift, holidays):
    #print (dateutil.parser.parse('1/2/24').weekday())
    cc_workdays = this_node.cal_code % 10
    cc_workshifts = this_node.cal_code // 10
    
    if is_working_day(this_node, prior_date, holidays) and prior_shift < cc_workshifts:
        return prior_date, prior_shift + 1
    elif cc_workdays == 0:
        if prior_shift < cc_workshifts:
            return prior_date, prior_shift + 1
        else:
            return prior_date + timedelta(days = 1), 1
    
    prior_shift = 1
    prior_date = prior_date + timedelta(days = 1)
    
    # if not able to, move to the first working day
    while not is_working_day(this_node, prior_date, holidays):
        prior_date = prior_date + timedelta(days = 1)

    return prior_date, prior_shift

#Finds the next working shift for the node, INCLUDING the date/shift that is passed in
def next_working_date_shift_incl(this_node, prior_date, prior_shift, holidays):
    cc_workdays = this_node.cal_code % 10
    cc_workshifts = this_node.cal_code // 10
    
    if is_working_day(this_node, prior_date, holidays) and prior_shift <= cc_workshifts:
        return prior_date, prior_shift
    elif cc_workdays == 0:
        return prior_date + timedelta(days = 1), 1
    
    prior_shift = 1
    prior_date = prior_date + timedelta(days = 1)
    
    # if not able to, move to the first working day
    while not is_working_day(this_node, prior_date, holidays):
        prior_date = prior_date + timedelta(days = 1)
        
    return prior_date, prior_shift

def adjust_concerto_es_date(this_node, holidays):
    if this_node.cal_code % 10 != 0:
        while holidays.is_holiday(this_node.es_date, this_node.cal_code) or this_node.es_date.weekday() >= this_node.cal_code % 10:
            this_node.es_date = this_node.es_date + timedelta(days = 1)
            this_node.es_shift = 1

def calc_finish_date_shift(this_node, start_date, start_shift, holidays):
    #TODO Calculate the minimum date that the early finish could be (based on cal_code)
    shifts_per_day = this_node.cal_code // 10
    days_per_week = this_node.cal_code % 10
    weekend_days_per_week = 7 - days_per_week

    min_working_days = this_node.rdu // shifts_per_day
    if days_per_week != 0 and days_per_week != 7:
        min_work_weeks = min_working_days // days_per_week
        min_days = min_working_days + min_work_weeks * weekend_days_per_week
    else:
        min_days = min_working_days

    min_days = timedelta(days = min_days - 1)

    finish_date = start_date + min_days
    
    finish_date = start_date + min_days
    if finish_date > start_date:
        finish_shift = 1
    else:
        finish_shift = start_shift
       
    fw.write('Date before starting loop to find first workday that is non-holiday: %s\n' % (finish_date))
    while holidays.is_holiday(finish_date, this_node.cal_code) or (finish_date.weekday() >= days_per_week and days_per_week != 0):
        finish_date = finish_date + timedelta(days = 1)

    #TODO Keep incrementing the EF date forward until the DU between ES and EF equals RDU
    i = 0
    while du_between_workshifts(start_date, start_shift, finish_date, finish_shift, this_node.cal_code, holidays) < this_node.rdu:
        (finish_date, finish_shift) = next_working_date_shift(this_node, finish_date, finish_shift, holidays)
        i = i + 1
        if i == 300:
            print('Hit 300 iterations for %s' % (this_node.name))
            break
    return (finish_date, finish_shift)

# This should not accept invalid start and finish dates. Otherwise, we could could get a non-working day as the finish
# date and it would compute the same number of DU as if it ended on the preceding work day.
def du_between_workshifts(start_date, start_shift, finish_date, finish_shift, cal_code, holidays):
    #TODO Need to make sure that X0 cal_codes are handled here or somewhere else
    shifts_per_day = cal_code // 10
    days_per_week = cal_code % 10
    
    if holidays.is_holiday(start_date, cal_code):
        raise Exception('Attempted to calculate DU starting from a holiday.')
    
    if holidays.is_holiday(finish_date, cal_code):
        raise Exception('Attempted to calculate DU ending on a holiday.')
    
    if days_per_week != 0 :
        if finish_date.weekday() >= days_per_week:
            raise Exception('Attempted to calculate DU ending on a non-workday.')
        if start_date.weekday() >= days_per_week:
            raise Exception('Attempted to calculate DU ending on a non-workday.')
    
    num_days = (finish_date - start_date).days + 1
    num_wkends = (num_days - 1) // 7
    if start_date.weekday() > finish_date.weekday():
        num_wkends = num_wkends + 1
    
    working_days = num_days - num_wkends * (7 - days_per_week)
    
    #TODO Does this work when the start and finish dates are the same, or adjacent?
    if days_per_week == 0:
        middle_working_shifts = (num_days - 2) * shifts_per_day
    else:
        middle_working_shifts = (working_days - 2) * shifts_per_day
    first_day_shifts = shifts_per_day - start_shift + 1
    last_day_shifts = finish_shift
    holiday_shifts = holidays.count_holidays_between(start_date, finish_date, cal_code) * shifts_per_day
    fw.write('middle_working_shifts: %d, first_day_shifts: %d, last_day_shift: %d\n' % (middle_working_shifts, first_day_shifts, last_day_shifts))
    return middle_working_shifts + first_day_shifts + last_day_shifts - holiday_shifts
    
def schedule_successors(this_node, earliest_date, holidays, nodes):
    for n in this_node.successors:
        if nodes[n].unsched_pred_count == 1:
            schedule_forward_pass(nodes[n], earliest_date, holidays, nodes)
        nodes[n].decr_unsched_pred_count()

main()