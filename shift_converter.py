import dateutil

def convert_start_to_shift(start_time):
    if start_time == '':
        return
    
    start_time = int(start_time)
    
    if start_time < 800:
        return 1
    elif start_time < 1600:
        return 2
    else:
        return 3
        
def convert_end_to_shift(end_time):
    if end_time == '':
        return
    
    end_time = int(end_time)
    
    if end_time == 0:
        return 3
    elif end_time <= 800:
        return 1
    elif end_time <= 1600:
        return 2
    else:
        return 3
    
def convert_shift_to_start(shift):
    if shift == 2:
         return "0800"
    elif shift == 3:
         return "1600"
    elif shift == 1:
         return "0000"
    else:
        return "0800"
    
def convert_shift_to_end(shift):
    if shift == 2:
         return "1600"
    elif shift == 3:
         return "2359"
    elif shift == 1:
         return "0800"
    else:
        return "1600"