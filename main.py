import csv
import node
from shift_converter import *
from datetime import *
from holiday_handler import *

ID_HEADER = 'PE'
DU_HEADER = 'DU'
RDU_HEADER = 'RDU'
PS_HEADER = 'PS'
CALNUM_HEADER = 'CALNUM'
AS_HEADER = 'AS'
AF_HEADER = 'AF'
ES_HEADER = 'ES'
EF_HEADER = 'EF'
LS_HEADER = 'LS'
LF_HEADER = 'LF'
SES_HEADER = 'SES'
AE_HEADER = 'AUTHORIZED_EVENT_DATE'
AT_HEADER = 'ACTIVITY_TYPE'

DATE_COLON_INDEX = 11

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
        
        #TODO I think we check headers here
        header_row = next(file_reader)
        
        global ID_COL
        global DU_COL
        global RDU_COL
        global PS_COL
        global CALNUM_COL
        global AS_COL
        global AF_COL
        global ES_COL
        global EF_COL
        global LS_COL
        global LF_COL
        global SES_COL
        global AE_COL
        global AT_COL

        ID_COL = get_col_num(header_row, ID_HEADER)
        DU_COL = get_col_num(header_row, DU_HEADER)
        RDU_COL = get_col_num(header_row, RDU_HEADER)    
        PS_COL = get_col_num(header_row, PS_HEADER)
        CALNUM_COL = get_col_num(header_row, CALNUM_HEADER)
        AS_COL = get_col_num(header_row, AS_HEADER)
        AF_COL = get_col_num(header_row, AF_HEADER)
        ES_COL = get_col_num(header_row, ES_HEADER)
        EF_COL = get_col_num(header_row, EF_HEADER)
        LS_COL = get_col_num(header_row, LS_HEADER)
        LF_COL = get_col_num(header_row, LF_HEADER)
        SES_COL = get_col_num(header_row, SES_HEADER)
        AE_COL = get_col_num(header_row, AE_HEADER)
        AT_COL = get_col_num(header_row, AT_HEADER)
                             
        row_num = 1

        nodes = {}

        for row in file_reader:
            #print(', '.join(row))
            new_node = node.Node(row[ID_COL], int(row[DU_COL]), int(row[RDU_COL]), int(row[CALNUM_COL]), row[AT_COL])

            #TODO Add the rest of the fields to new_node if they exist
            if row[ES_COL] != '':
                date_time_parts = row[ES_COL].split(':')
                new_node.set_es_with_time(date_time_parts[0], date_time_parts[1])
                
            if row[EF_COL] != '':
                date_time_parts = row[EF_COL].split(':')
                new_node.set_ef_with_time(date_time_parts[0], date_time_parts[1])
                
            if row[LS_COL] != '':
                date_time_parts = row[LS_COL].split(':')
                new_node.set_ls_with_time(date_time_parts[0], date_time_parts[1])
                
            if row[LF_COL] != '':
                date_time_parts = row[LF_COL].split(':')
                new_node.set_lf_with_time(date_time_parts[0], date_time_parts[1])
                
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
                
            if row[AE_COL] != '':
                date_time_parts = row[AE_COL].split(':')
                new_node.set_ae_with_time(date_time_parts[0], date_time_parts[1])

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
            
            if nodes[row[0]].af_date == '' and nodes[row[1]].as_date != '':
                nodes[row[1]].out_of_order = True
                
            if nodes[row[0]].out_of_order == True and nodes[row[1]].as_date != '':
                nodes[row[1]].out_of_order = True

    #test_clear_nodes(nodes)
    print('Marking tied nodes')
    mark_tied_nodes(nodes['EG00'], nodes)

    holidays = Holiday_Handler(2020, 2030)
    start_date = dateutil.parser.parse('08/22/2024').date()
    
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
            
    print('Verifying results')
    
    # TODO Find number of mismatches here
    with open(nodes_file, newline='') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        
        #TODO I think we check headers here
        header_row = next(file_reader)
        
        mismatched_es_date = 0
        mismatched_ef_date = 0
        mismatched_es_shift = 0
        mismatched_ef_shift = 0
        
        for row in file_reader:
            new_node = node.Node(row[ID_COL], int(row[DU_COL]), int(row[RDU_COL]), int(row[CALNUM_COL]), row[AT_COL])
            matching_node = nodes[new_node.name]

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
                
            if row[AE_COL] != '':
                date_time_parts = row[AE_COL].split(':')
                new_node.set_ae_with_time(date_time_parts[0], date_time_parts[1])
                
            if new_node.es_date != matching_node.es_date:
                mismatched_es_date = mismatched_es_date + 1
            
            if new_node.ef_date != matching_node.ef_date:
                mismatched_ef_date = mismatched_ef_date + 1
                
            if new_node.es_shift != matching_node.es_shift:
                mismatched_es_shift = mismatched_es_shift + 1
            
            if new_node.ef_shift != matching_node.ef_shift:
                mismatched_ef_shift = mismatched_ef_shift + 1
                
        print('Mismatched ES Date:  %d' % (mismatched_es_date))
        print('Mismatched ES Shift: %d' % (mismatched_es_shift))
        print('Mismatched EF Date:  %d' % (mismatched_ef_date))
        print('Mismatched EF Shift: %d' % (mismatched_ef_shift))
    print('Complete')
    
def get_col_num(header_row, col_header):
    for i in range(0, len(header_row)):
        if header_row[i] == col_header:
            return i
        
    raise Exception('Could not find a required header.')

def schedule_forward_pass(this_node, earliest_date, holidays, nodes):
    fw.write('Scheduling %s\n' % (this_node.name))
    
    # This can happen when work is out of order
    if this_node.forward_scheduled == True:
        return
    else:
        this_node.forward_scheduled = True
    
    (latest_finish, latest_shift) = find_latest_pred_finish(this_node, earliest_date, nodes, False)
    
    (es_date, es_shift) = next_working_date_shift(this_node, latest_finish, latest_shift, holidays)
    
    #TODO Need to make sure these are not putting the es_date and es_shift on a weekend or holiday
    #TODO Need to update the use of SES to ignore it if it makes the job go negative. This should wait until
        # backward passes are done, because the ES ending up before the LS will be the indication that
        # SES could be making the job go negative. PS will still be honored if it makes the job go negative.    
    if this_node.ps_date != '' and (this_node.ps_date > es_date or (this_node.ps_date == es_date and this_node.ps_shift >= es_shift)):
        es_date = this_node.ps_date
        es_shift = this_node.ps_shift
    
    #TODO Replace the check for SES being after the known ES. Need to compare with the LS after the backward pass is implemented.
    if this_node.ses_date != '' and (this_node.ses_date > es_date or (this_node.ses_date == es_date and this_node.ses_shift >= es_shift)) and (this_node.ses_date < this_node.es_date or (this_node.ses_date == this_node.es_date and this_node.ses_shift <= this_node.es_shift)):
        es_date = this_node.ses_date
        es_shift = this_node.ses_shift
    
    (es_date, es_shift) = next_working_date_shift_incl(this_node, es_date, es_shift, holidays)
    
    if this_node.ae_date != '' and (this_node.act_type == 'Completion Milestone' or (this_node.ae_date > es_date or (this_node.ae_date == es_date and this_node.ae_shift >= es_shift))):
        es_date = this_node.ae_date
        es_shift = this_node.ae_shift
    
    (ef_date, ef_shift) = calc_finish_date_shift(this_node, es_date, es_shift, holidays)
    
    # TODO This is relying on Concerto to flag when a sequence is not tied properly. Untied sequences can be checked during backward passes,
    #      so when backward passes are being implemented, we should use the results of that for the conditional.
    # es_date and es_shift are directly from Concerto because they are based on import dates, which are not available in exports.
    # ef_date and ef_shift are directly from Concerto because it does not calculate consistently.
    if this_node.tied == False:
        es_date = this_node.es_date
        es_shift = this_node.es_shift
        ef_date = this_node.ef_date
        ef_shift = this_node.ef_shift
    
    #The LOE exclusion here is because it won't be fixed until the backward pass is implemented
    if this_node.ef_date != ef_date and this_node.act_type != 'LOE':# and this_node.es_date == es_date and this_node.es_shift == es_shift and this_node.rdu < 90 and this_node.rdu != 0:
        fw.write('Mismatch between early finish dates: %s\n' % (this_node.name))
        fw.write('\tConcerto ES Date:\t%s\n' % (this_node.es_date))
        fw.write('\tCalculated ES Date:\t%s\n' % (es_date))
        fw.write('\tConcerto ES Shift:\t%s\n' % (this_node.es_shift))
        fw.write('\tCalculated ES Shift:%s\n' % (es_shift))
        fw.write('\tCalculated EF Date:\t%s\n' % (ef_date))
        fw.write('\tConcerto EF Date:\t%s\n' % (this_node.ef_date))
        fw.write('\tConcerto RDU:\t\t%s\n' % (this_node.rdu))
        fw.write('\tConcerto Cal Code:\t%s\n' % (this_node.cal_code))

    # The check for du or rdu not being zero is because milestones that have an ES/PS
    # time of 0000 sometimes end at 2359 the day before, or at 0000 on the same day.
    elif this_node.ef_shift != ef_shift and (this_node.du != 0 or this_node.rdu != 0):
        fw.write('Mismatch between early finish shifts: %s\n' % (this_node.name))
        fw.write('\tConcerto ES Date:\t%s\n' % (this_node.es_date))
        fw.write('\tCalculated ES Date:\t%s\n' % (es_date))
        fw.write('\tConcerto ES Shift:\t%s\n' % (this_node.es_shift))
        fw.write('\tCalculated ES Shift:%s\n' % (es_shift))
        fw.write('\tCalculated EF Date:\t%s\n' % (ef_date))
        fw.write('\tConcerto EF Date:\t%s\n' % (this_node.ef_date))
        fw.write('\tCalculated EF Shift:\t%s\n' % (ef_shift))
        fw.write('\tConcerto EF Shift:\t%s\n' % (this_node.ef_shift))
        fw.write('\tConcerto RDU:\t\t%s\n' % (this_node.rdu))
        fw.write('\tConcerto Cal Code:\t%s\n' % (this_node.cal_code))
        
    this_node.es_date = es_date
    this_node.es_shift = es_shift
    this_node.ef_date = ef_date
    this_node.ef_shift = ef_shift

    schedule_successors(this_node, earliest_date, holidays, nodes)
    
def find_latest_pred_finish(this_node, earliest_date, nodes, loe_recurse):
    latest_finish = earliest_date - timedelta(days=1)
    latest_shift = 3
    
    if not (this_node.act_type == 'LOE' and this_node.as_date != '') or loe_recurse:
        for n in this_node.predecessors:
            (pred_prev_es_date, pred_prev_es_shift) = prev_date_shift(nodes[n].es_date, nodes[n].es_shift)

            # TODO Verify these conditionals will handle the case that ef_date == latest_finish and ef_shift > latest_shift
            # TODO I don't think these AF checks are needed, because EF will have the same data if there is an AF.
            if nodes[n].act_type == 'LOE':
                if nodes[n].as_date != '':
                    #TODO Need to change this to look back recursively instead of assuming LOE work's ES is the right ES.
                    (pred_latest_finish, pred_latest_shift) = find_latest_pred_finish(nodes[n], earliest_date, nodes, True)
                    if pred_latest_finish > latest_finish or (pred_latest_finish == latest_finish and pred_latest_shift > latest_shift):
                        latest_finish = pred_latest_finish
                        latest_shift = pred_latest_shift
                else:
                    if pred_prev_es_date > latest_finish or (pred_prev_es_date == latest_finish and pred_prev_es_shift > latest_shift):
                        latest_finish = pred_prev_es_date
                        latest_shift = pred_prev_es_shift
            elif nodes[n].ef_date != '' and nodes[n].ef_date > latest_finish:
                latest_finish = nodes[n].ef_date
                latest_shift = nodes[n].ef_shift
            elif nodes[n].ef_date == latest_finish:
                latest_shift = max(latest_shift, nodes[n].ef_shift)
            elif nodes[n].af_date != '' and nodes[n].out_of_order == True: #and nodes[n].af_date > latest_finish:
                (af_latest_finish, af_latest_shift) = find_latest_pred_finish(nodes[n], earliest_date, nodes, False)
                
                if af_latest_finish > latest_finish or (af_latest_finish == latest_finish and af_latest_shift > latest_shift):
                    latest_finish = af_latest_finish
                    latest_shift = af_latest_shift
    
    return latest_finish, latest_shift
    
def is_working_day(this_node, date, holidays):
    cc_workdays = this_node.cal_code % 10
    
    if cc_workdays == 0:
        return True
    
    if date.weekday() >= cc_workdays:
        return False
    
    if holidays.is_holiday(date, this_node.cal_code):
        return False
    
    return True

#Finds the shift immediately before the given date and shift
def prev_date_shift(date, shift):
    if shift == 1:
        return date - timedelta(days = 1), 3
    else:
        return date, shift - 1

# Finds the next working shift for the node, NOT including the date/shift that is passed in
# Does NOT assume that prior date is a valid workday
def next_working_date_shift(this_node, prior_date, prior_shift, holidays):
    #print (dateutil.parser.parse('1/2/24').weekday())
    cc_workdays = this_node.cal_code % 10
    cc_workshifts = this_node.cal_code // 10
    default_starting_shift = (3 - cc_workshifts) + cc_workshifts // 2
    
    if cc_workshifts != 1 and prior_shift != 3:
        return prior_date, prior_shift + 1
    elif cc_workdays == 0:
        return prior_date + timedelta(days = 1), default_starting_shift
    elif cc_workshifts != 3 and prior_shift == 1:
        return prior_date, 2
    
    prior_date = prior_date + timedelta(days = 1)
    
    while not is_working_day(this_node, prior_date, holidays):
        prior_date = prior_date + timedelta(days = 1)

    return prior_date, default_starting_shift

# Finds the next working shift for the node, INCLUDING the date/shift that is passed in
# Does NOT assume that prior date is a valid workday
def next_working_date_shift_incl(this_node, prior_date, prior_shift, holidays):
    cc_workdays = this_node.cal_code % 10
    cc_workshifts = this_node.cal_code // 10
    default_starting_shift = (3 - cc_workshifts) + cc_workshifts // 2
    
    # Move prior_shift to a valid work shift
    if cc_workshifts != 3 and prior_shift != 3:
        prior_shift = default_starting_shift
    elif cc_workshifts == 1 and prior_shift == 3:
        prior_shift = default_starting_shift
        prior_date = prior_date + timedelta(days = 1)
    
    # Move prior_date to a valid workday, setting prior_shift to the default value if prior_date is moved
    while not is_working_day(this_node, prior_date, holidays):
        prior_date = prior_date + timedelta(days = 1)
        prior_shift = default_starting_shift

    return prior_date, prior_shift

def adjust_concerto_es_date(this_node, holidays):
    if this_node.cal_code % 10 != 0:
        while holidays.is_holiday(this_node.es_date, this_node.cal_code) or this_node.es_date.weekday() >= this_node.cal_code % 10:
            this_node.es_date = this_node.es_date + timedelta(days = 1)
            this_node.es_shift = 1

def calc_finish_date_shift(this_node, start_date, start_shift, holidays):
    # TODO This needs to not capture LOE when the backward pass is done. EF should be the same as LF for LOE, and LF won't use this function.
    if this_node.rdu == 0:
        if start_shift == 1:
            return start_date - timedelta(days = 1), 3
        else:
            return start_date, start_shift - 1
    
    #TODO Calculate the minimum date that the early finish could be (based on cal_code)
    shifts_per_day = this_node.cal_code // 10
    days_per_week = this_node.cal_code % 10
    weekend_days_per_week = 7 - days_per_week

    min_working_days = (this_node.rdu) // shifts_per_day
    
    if days_per_week == 0 or days_per_week == 7:
        min_days = min_working_days
    else:
        min_work_weeks = min_working_days // days_per_week - 1
        min_days = min_working_days + min_work_weeks * weekend_days_per_week

    min_days = timedelta(days = min_days - 1)
    finish_date = start_date + min_days
    
    if finish_date > start_date:
        finish_shift = 2
    else:
        finish_shift = start_shift
       
    fw.write('Date before starting loop to find first workday that is non-holiday: %s\n' % (finish_date))
    while holidays.is_holiday(finish_date, this_node.cal_code) or (finish_date.weekday() >= days_per_week and days_per_week != 0):
        finish_date = finish_date + timedelta(days = 1)
    
    i = 0
    while du_between_workshifts(start_date, start_shift, finish_date, finish_shift, this_node.cal_code, holidays) < this_node.rdu:
        (finish_date, finish_shift) = next_working_date_shift(this_node, finish_date, finish_shift, holidays)

        i = i + 1
        #TODO Remove this
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
        
    if shifts_per_day == 1:
        first_day_shifts = 1
    else:
        first_day_shifts = 4 - start_shift
    
    if shifts_per_day == 3:
        last_day_shifts = finish_shift
    else:
        last_day_shifts = finish_shift - 1
    
    if days_per_week != 0:
        holiday_shifts = holidays.count_holidays_between(start_date, finish_date, cal_code) * shifts_per_day
    else:
        holiday_shifts = 0
    fw.write('%s, shift %d: middle_working_shifts: %d, first_day_shifts: %d, last_day_shift: %d, holiday_shifts: %d\n' % (finish_date, finish_shift, middle_working_shifts, first_day_shifts, last_day_shifts, holiday_shifts))
    return middle_working_shifts + first_day_shifts + last_day_shifts - holiday_shifts
    
def schedule_successors(this_node, earliest_date, holidays, nodes):
    for n in this_node.successors:
        if nodes[n].unsched_pred_count == 1:
            schedule_forward_pass(nodes[n], earliest_date, holidays, nodes)
        nodes[n].decr_unsched_pred_count()

def mark_tied_nodes(this_node, nodes):
    this_node.tied = True
    
    for n in this_node.predecessors:
        if nodes[n].tied == False:
            mark_tied_nodes(nodes[n], nodes)
        
main()