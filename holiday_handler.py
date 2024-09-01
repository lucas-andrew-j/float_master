import dateutil
from datetime import timedelta

class Holiday_Handler:
    
    holiday_set = set()
    holiday_arr = []
    
    closure_saturdays_set = set()
    closure_saturdays_arr = []
    
    closure_sundays_set = set()
    closure_sundays_arr = []
    
    lowest_year = 0
    highest_year = 0
    
    def __init__(self, first_year, last_year):
        if last_year < first_year:
            num_years = first_year - last_year
            first_year = last_year
            last_year = first_year + num_years
        
        for year in range(first_year, last_year + 1):
            self.__add_year(year)
        
        self.lowest_year = first_year
        self.highest_year = last_year
        
        
    
    def add_year(self, year):
        if year == self.highest_year + 1:
            self.__add_year(year)
            self.highest_year = year
        elif year == self.lowest_year - 1:
            self.__add_year(year)
            self.lowest_year = year
            self.holiday_arr.sort()
            self.closure_saturdays_arr.sort()
            self.closure_sundays_arr.sort()
        else:
            raise Exception("Attempted to add year to holidays that is not adjacent to the lowest or highest current years")
    
    def is_holiday(self, date, cal_code):
        if cal_code % 10 == 0:
            return False
        
        result = date in self.holiday_set
        
        if cal_code % 10 == 7:
            result = result and date in self.closure_sundays_set
            
        if cal_code % 10 >= 6:
            result = result and date in self.closure_saturdays_set
        
        return result
    
    # Returns the number of holidays between the two given dates (including either date if they are holidays)
    def count_holidays_between(self, start_date, finish_date, cal_code):
        start_index = Holiday_Handler.__get_index_closest_gte(start_date, self.holiday_arr)
        finish_index = Holiday_Handler.__get_index_closest_lte(finish_date, self.holiday_arr)
        
        count = finish_index - start_index + 1
        
        if cal_code % 10 == 7:
            start_index = Holiday_Handler.__get_index_closest_gte(start_date, self.closure_sundays_arr)
            finish_index = Holiday_Handler.__get_index_closest_lte(finish_date, self.closure_sundays_arr)
            count = count + finish_index - start_index + 1
            
        if cal_code % 10 >= 6:
            start_index = Holiday_Handler.__get_index_closest_gte(start_date, self.closure_saturdays_arr)
            finish_index = Holiday_Handler.__get_index_closest_lte(finish_date, self.closure_saturdays_arr)
            count = count + finish_index - start_index + 1
        
        return count
            
    def __add_year(self, year):
        # TODO Remove this. It's here because the project I'm testing with does not have any holidays past 2026.
        if year > 2026:
            print("Year %d bypassed." % (year))
            return
        
        self.__add_new_year(year)
        self.__add_mlk_holiday(year)
        self.__add_presidents_day(year)
        self.__add_memorial_day(year)
        self.__add_juneteenth(year)
        self.__add_independence_day(year)
        self.__add_labor_day(year)
        self.__add_columbus_day(year)
        self.__add_veterans_day(year)
        self.__add_thanksgiving(year)
        self.__add_add_christmas(year)
        self.__add_closure(year)
    
    def __add_new_year(self, year):
        actual_holiday = dateutil.parser.parse("1/1/%d" % year).date()
        observed_holiday = Holiday_Handler.__nearest_weekend_day(actual_holiday)
        # Sometimes this is on the 31st of the year before, which overlaps with closures.
        # This prevents duplication of these dates in the array.
        if not observed_holiday in self.holiday_set:
            self.holiday_set.add(observed_holiday)
            self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_mlk_holiday(self, year):
        observed_holiday = Holiday_Handler.__get_nth_weekday(0, 3, 1, year)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_presidents_day(self, year):
        observed_holiday = Holiday_Handler.__get_nth_weekday(0, 3, 2, year)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_memorial_day(self, year):    
        last_weekday = dateutil.parser.parse("5/31/%d" % (year)).weekday()
        day = 31 - last_weekday
        holiday = dateutil.parser.parse("5/%d/%d" % (day, year)).date()
        
        self.holiday_set.add(holiday)
        self.holiday_arr.append(holiday)
        return holiday
    
    def __add_juneteenth(self, year):
        actual_holiday = dateutil.parser.parse("6/19/%d" % year).date()
        observed_holiday = Holiday_Handler.__nearest_weekend_day(actual_holiday)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_independence_day(self, year):
        actual_holiday = dateutil.parser.parse("7/4/%d" % year).date()
        observed_holiday = Holiday_Handler.__nearest_weekend_day(actual_holiday)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_labor_day(self, year):
        observed_holiday = Holiday_Handler.__get_nth_weekday(0, 1, 9, year)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_columbus_day(self, year):
        observed_holiday = Holiday_Handler.__get_nth_weekday(0, 2, 10, year)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_veterans_day(self, year):
        actual_holiday = dateutil.parser.parse("11/11/%d" % year).date()
        observed_holiday = Holiday_Handler.__nearest_weekend_day(actual_holiday)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_thanksgiving(self, year):
        observed_holiday = Holiday_Handler.__get_nth_weekday(3, 4, 11, year)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    def __add_add_christmas(self, year):
        actual_holiday = dateutil.parser.parse("12/25/%d" % year).date()
        observed_holiday = Holiday_Handler.__nearest_weekend_day(actual_holiday)
        self.holiday_set.add(observed_holiday)
        self.holiday_arr.append(observed_holiday)
        return observed_holiday
    
    # TODO This does not extend the closure to include the Monday and weekend before xmas if 
    # xmas is on Tuesday. Is this right?
    def __add_closure(self, year):
        current_date = Holiday_Handler.__get_closure_start(year)
        end_date = Holiday_Handler.__get_closure_end(year + 1)
        
        while current_date <= end_date: #dateutil.parser.parse("12/31/%d" % year).date():
            if current_date.weekday() == 5:
                self.closure_saturdays_set.add(current_date)
                self.closure_saturdays_arr.append(current_date)
            elif current_date.weekday() == 6:
                self.closure_sundays_set.add(current_date)
                self.closure_sundays_arr.append(current_date)
            else:
                if not current_date in self.holiday_set:
                    self.holiday_set.add(current_date)
                    self.holiday_arr.append(current_date)
                    current_date
            
            current_date = current_date + timedelta(days = 1)
        
    @staticmethod
    def __nearest_weekend_day(date):
        weekend_day = date.weekday()
        return date + timedelta(days = (((weekend_day + 1) // 6) * -1 + ((weekend_day + 1) // 7) * 2))
    
    @staticmethod
    def __get_nth_weekday(weekday, n, month, year):
        first_weekday = dateutil.parser.parse("%d/1/%d" % (month, year)).weekday()
        
        if weekday >= first_weekday:
            n = n - 1
        
        day = 1 + weekday - first_weekday + n * 7
        
        return dateutil.parser.parse("%d/%d/%d" % (month, day, year)).date()
    
    @staticmethod
    def __get_closure_start(year):
        xmas_holiday = dateutil.parser.parse("12/25/%d" % year).date()
        observed_holiday = Holiday_Handler.__nearest_weekend_day(xmas_holiday)
        return observed_holiday
    
    @staticmethod
    def __get_closure_end(year):
        # TODO Remove this. It's here because the project I'm testing with does not have any holidays past 2026.
        if year > 2026:
            return dateutil.parser.parse("12/31/%d" % (year - 1)).date()
        
        new_year_holiday = dateutil.parser.parse("1/1/%d" % year).date()
        new_year_weekday = new_year_holiday.weekday()
        
        if new_year_weekday <= 2:
            return new_year_holiday
        else:
            return new_year_holiday + timedelta(days = 6 - new_year_weekday)
    
    # Returns the index of the closest holiday that is greater than or equal to the given date
    @staticmethod
    def __get_index_closest_gte(date, date_arr):
        middle = len(date_arr) // 2
        lower = 0
        upper = len(date_arr) - 1
        
        while True:
            if date_arr[middle] == date:
                start_index = middle
                break
            elif date_arr[middle] > date:
                upper = middle - 1
            else:
                lower = middle + 1
            
            middle = (upper - lower) // 2 + lower
            
            if middle >= upper and middle <= lower:
                break
        
        if date_arr[middle] < date:
            middle = middle + 1
            
        return middle
            
    # Returns the index of the closest holiday that is less than or equal to the given date
    @staticmethod
    def __get_index_closest_lte(date, date_arr):
        middle = len(date_arr) // 2
        lower = 0
        upper = len(date_arr) - 1
        
        while True:
            if date_arr[middle] == date:
                start_index = middle
                break
            elif date_arr[middle] > date:
                upper = middle - 1
            else:
                lower = middle + 1
            
            middle = (upper - lower) // 2 + lower
            
            if middle >= upper and middle <= lower:
                break
        
        if date_arr[middle] > date:
            middle = middle - 1
            
        return middle