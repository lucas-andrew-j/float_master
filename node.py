import dateutil
from shift_converter import *
from datetime import timedelta

class Node:
    f = open("log.txt", "a")
    f.write("\n###### START OF NEW RUN #######\n")
    
    def __init__(self, name, rdu, cal_code):
        self.name = name
        self.rdu = rdu
        self.cal_code = cal_code
        
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
        
        self.ss_date = ''
        self.ss_shift = 0 
        self.forward_scheduled = False
        
    # ps = early_start
    def set_ps_with_time(self, date, time):
        self.ps_date = date
        self.ps_shift = convert_start_to_shift(time)
    
    def get_ps_date(self):
        return self.ps_date
    
    def get_ps_shift(self):
        return self.ps_shift
    
    # as = actual_start
    def set_as(self, date, shift):
        self.as_date = date
        self.as_shift = shift
        
    def set_as_with_time(self, date, time):
        self.as_date = date
        self.as_shift = convert_start_to_shift(time)
    
    def get_as_date(self):
        return self.as_date
    
    def get_as_shift(self):
        return self.as_shift
    
    # af = actual_finish
    def set_af(self, date, shift):
        self.af_date = date
        self.af_shift = shift
        
    def set_af_with_time(self, date, time):
        self.af_date = date
        self.af_shift = convert_end_to_shift(time)
    
    def get_af_date(self):
        return self.af_date
    
    def get_af_shift(self):
        return self.af_shift
        
    # es = early_start
    def set_es(self, date, shift):
        self.es_date = date
        self.es_shift = shift
        
    def set_es_with_time(self, date, time):
        self.es_date = date
        self.es_shift = convert_start_to_shift(time)
    
    def get_es_date(self):
        return self.es_date
    
    def get_es_shift(self):
        return self.es_shift
    
    # ef = early_finish
    def set_ef(self, date, shift):
        self.ef_date = date
        self.ef_shift = shift
        
    def set_ef_with_time(self, date, time):
        self.ef_date = date
        self.ef_shift = convert_end_to_shift(time)
    
    def get_ef_date(self):
        return self.ef_date
    
    def get_ef_shift(self):
        return self.ef_shift
    
    # ls = late_start
    def set_ls(self, date, shift):
        self.ls_date = date
        self.ls_shift = shift
        
    def set_ls(self, date, time):
        self.ls_date = date
        self.ls_shift = convert_start_to_shift(time)
    
    def get_ls_date(self):
        return self.ls_date
    
    def get_ls_shift(self):
        return self.ls_shift
    
    # lf = late_finish
    def set_lf(self, date, shift):
        self.lf_date = date
        self.lf_shift = shift
        
    def set_lf(self, date, time):
        self.lf_date = date
        self.lf_shift = convert_end_to_shift(time)
    
    def get_lf_date(self):
        return self.lf_date
    
    def get_lf_shift(self):
        return self.lf_shift
    
    # ss = scheduled_start
    def set_ss_with_time(self, date, time):
        self.ss_date = date
        self.ss_shift = convert_start_to_shift(time)
    
    def get_ss_date(self):
        return self.ss_date
    
    def get_ss_shift(self):
        return self.ss_shift
    
    def set_fp_done(self, status):
        self.fp_done = status
    
    def get_fp_done(self):
        return self.fp_done
    
    def set_bp_done(self, status):
        self.bp_done = status
    
    def get_bp_done(self):
        return self.bp_done
       
    def add_pred(self, predecessor):
        self.predecessors.append(predecessor)
        self.unsched_pred_count = self.unsched_pred_count + 1
       
    def decr_unsched_pred_count(self):
        self.unsched_pred_count = self.unsched_pred_count - 1
    
    def add_succ(self, successor):
        self.successors.append(successor)
        self.unsched_succ_count = self.unsched_succ_count + 1
    
    def decr_unsched_succ_count(self):
        self.unsched_succ_count = self.unsched_succ_count - 1
    
    def __str__(self):
        return "Name: %s,\tDU: %s,\tCal Code: %s,\tPred: %s,\tSucc: %s,\tES: %s,\tEF: %s" % (self.name, self.rdu, self.cal_code, self.unsched_pred_count, self.unsched_succ_count, self.es_date, self.ef_date)
    
    def __repr__(self):
        return "something"