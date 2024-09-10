import dateutil
from shift_converter import *
from datetime import timedelta

class Node:
    def __init__(self, name, du, rdu, cal_code, act_type):
        self.name = name
        self.rdu = rdu
        self.du = du
        self.cal_code = cal_code
        self.act_type = act_type
        self.out_of_order = False
        self.tied = False
        
        self.predecessors = []
        self.unsched_pred_count = 0
        self.successors = []
        self.unsched_succ_count = 0
        
        self.ps_date = ''
        self.ps_shift = 0
        
        self.as_date = ''
        self.as_shift = 0
        
        self.af_date = ''
        self.af_shift = 0
        
        self.es_date = ''
        self.es_shift = 0
        
        self.ef_date = ''
        self.ef_shift = 0
        
        self.ls_date = ''
        self.ls_shift = 0
        
        self.lf_date = ''
        self.lf_shift = 0
        
        self.ses_date = ''
        self.ses_shift = 0
        
        self.ae_date = ''
        self.ae_shift = 0 
        
        self.forward_scheduled = False
        
    # ps = early_start
    def set_ps_with_time(self, date, time):
        self.ps_shift = convert_start_to_shift(time)
        if self.ps_shift == 3:
            self.ps_date = dateutil.parser.parse(date).date() - timedelta(days = 1)
        else:
            self.ps_date = dateutil.parser.parse(date).date()
    
    def get_ps_date(self):
        return self.ps_date
    
    def get_ps_shift(self):
        return self.ps_shift
    
    # as = actual_start
    def set_as(self, date, shift):
        self.as_date = dateutil.parser.parse(date).date()
        self.as_shift = shift
        
    def set_as_with_time(self, date, time):
        self.as_shift = convert_start_to_shift(time)
        self.as_date = dateutil.parser.parse(date).date()
    
    def get_as_date(self):
        return self.as_date
    
    def get_as_shift(self):
        return self.as_shift
    
    # af = actual_finish
    def set_af(self, date, shift):
        self.af_date = dateutil.parser.parse(date).date()
        self.af_shift = shift
        
    def set_af_with_time(self, date, time):
        self.af_shift = convert_end_to_shift(time)
        if time == "0000":
            self.af_date = dateutil.parser.parse(date).date() - timedelta(days = 1)
        else:
            self.af_date = dateutil.parser.parse(date).date()
    
    def get_af_date(self):
        return self.af_date
    
    def get_af_shift(self):
        return self.af_shift
        
    # es = early_start
    def set_es(self, date, shift):
        self.es_date = dateutil.parser.parse(date).date()
        self.es_shift = shift
        
    def set_es_with_time(self, date, time):
        self.es_shift = convert_start_to_shift(time)
        self.es_date = dateutil.parser.parse(date).date()
    
    def get_es_date(self):
        return self.es_date
    
    def get_es_shift(self):
        return self.es_shift
    
    # ef = early_finish
    def set_ef(self, date, shift):
        self.ef_date = dateutil.parser.parse(date).date()
        self.ef_shift = shift
        
    def set_ef_with_time(self, date, time):
        self.ef_shift = convert_end_to_shift(time)
        
        if time == '0000':
            self.ef_date = dateutil.parser.parse(date).date() - timedelta(days = 1)
        else:
            self.ef_date = dateutil.parser.parse(date).date()
    
    def get_ef_date(self):
        return self.ef_date
    
    def get_ef_shift(self):
        return self.ef_shift
    
    # ls = late_start
    def set_ls(self, date, shift):
        self.ls_date = dateutil.parser.parse(date).date()
        self.ls_shift = shift
        
    def set_ls_with_time(self, date, time):
        self.ls_shift = convert_start_to_shift(time)
        self.ls_date = dateutil.parser.parse(date).date()
    
    def get_ls_date(self):
        return self.ls_date
    
    def get_ls_shift(self):
        return self.ls_shift
    
    # lf = late_finish
    def set_lf(self, date, shift):
        self.lf_date = dateutil.parser.parse(date).date()
        self.lf_shift = shift
        
    def set_lf_with_time(self, date, time):
        self.lf_shift = convert_end_to_shift(time)
        
        if time == '0000':
            self.lf_date = dateutil.parser.parse(date).date() - timedelta(days = 1)
        else:
            self.lf_date = dateutil.parser.parse(date).date()
        
    def set_lf(self, date, time):
        self.lf_date = dateutil.parser.parse(date).date()
        self.lf_shift = convert_end_to_shift(time)
    
    def get_lf_date(self):
        return self.lf_date
    
    def get_lf_shift(self):
        return self.lf_shift
    
    # ses = scheduled_early_start
    def set_ses_with_time(self, date, time):
        self.ses_shift = convert_start_to_shift(time)
        self.ses_date = dateutil.parser.parse(date).date()
    
    def get_ses_date(self):
        return self.ses_date
    
    def get_ses_shift(self):
        return self.ses_shift
    
    # ae = authorized_event_date
    def set_ae_with_time(self, date, time):
        self.ae_shift = convert_start_to_shift(time)
        self.ae_date = dateutil.parser.parse(date).date()
    
    def get_ae_date(self):
        return self.ae_date
    
    def get_ae_shift(self):
        return self.ae_shift
    
    def set_fp_done(self, status):
        self.forward_scheduled = status
    
    def get_fp_done(self):
        return self.forward_scheduled
    
    def set_bp_done(self, status):
        self.bp_done = status
    
    def get_bp_done(self):
        return self.bp_done
       
    def add_pred(self, predecessor, pred_complete):
        self.predecessors.append(predecessor)
        if not pred_complete:
            self.unsched_pred_count = self.unsched_pred_count + 1
       
    def decr_unsched_pred_count(self):
        self.unsched_pred_count = self.unsched_pred_count - 1
    
    def add_succ(self, successor, succ_complete):
        self.successors.append(successor)
        if not succ_complete:
            self.unsched_succ_count = self.unsched_succ_count + 1
    
    def decr_unsched_succ_count(self):
        self.unsched_succ_count = self.unsched_succ_count - 1
    
    def __str__(self):
        return "Name: %s,\tDU: %s,\tCal Code: %s,\tPred: %s,\tSucc: %s,\tES: %s, %d,\tEF: %s, %d" % (self.name, self.rdu, self.cal_code, self.unsched_pred_count, self.unsched_succ_count, self.es_date, self.es_shift, self.ef_date, self.ef_shift)
    
    def __repr__(self):
        return "something"