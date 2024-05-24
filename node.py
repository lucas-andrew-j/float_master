import dateutil

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
        
    # es = early_start
    def set_es(self, date, shift):
        self.es_date = date
        self.es_shift = shift
    
    def get_es_date(self):
        return self.es_date
    
    def get_es_shift(self):
        return self.es_shift
    
    # ef = early_finish
    def set_ef(self, date, shift):
        self.ef_date = date
        self.ef_shift = shift
    
    def get_ef_date(self):
        return self.ef_date
    
    def get_ef_shift(self):
        return self.ef_shift
    
    # ls = late_start
    def set_ls(self, date, shift):
        self.ls_date = date
        self.ls_shift = shift
    
    def get_ls_date(self):
        return self.ls_date
    
    def get_ls_shift(self):
        return self.ls_shift
    
    # lf = late_finish
    def set_lf(self, date, shift):
        self.lf_date = date
        self.lf_shift = shift
    
    def get_lf_date(self):
        return self.lf_date
    
    def get_lf_shift(self):
        return self.lf_shift
    
    # ss = scheduled_start
    def set_ss(self, date, shift):
        self.ss_date = date
        self.ss_shift = shift
    
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
        
    def schedule_forward_pass(self, earliest_date, holidays, nodes):
        self.f.write("Scheduling %s\n" % (self.name))
        self.forward_scheduled = True
        #TODO Schedule this node

        latest_finish = earliest_date
        latest_shift = 1
        for n in self.successors:
            if nodes[n].ef_date > latest_finish:
                latest_finish = nodes[n].ef_date
                latest_shift = nodes[n].ef_shift
            elif nodes[n].ef_date == latest_finish:
                latest_shift = max(latest_shift, nodes[n].es_shift)
        
        #TODO Set the ES of this job to the first working shift after the date found in the previous step
        (self.es_date, self.es_shift) = self.__find_next_working_date_shift(latest_finish, latest_shift, holidays)

        #TODO Calculate the minimum date that the early finish could be (based on cal_code)
        #TODO Keep incrementing the EF date forward until the DU between ES and EF equals RDU

        self.__schedule_successors(earliest_date, holidays, nodes)
            
    #Finds the next working shift for the node, not including the date/shift that is passed in
    def __find_next_working_date_shift(self, starting_date, starting_shift, holidays):
        return starting_date, starting_shift
    
    def __schedule_successors(self, earliest_date, holidays, nodes):
        for n in self.successors:
            if nodes[n].unsched_pred_count == 1:
                nodes[n].schedule_forward_pass(earliest_date, holidays, nodes)
            else:
                nodes[n].decr_unsched_pred_count()
    
    def __str__(self):
        return "Name: %s, \tDU: %s, \tCal Code: %s, \tPred: %s, \tSucc: %s" % (self.name, self.rdu, self.cal_code, self.unsched_pred_count, self.unsched_succ_count)
    
    def __repr__(self):
        return "something"