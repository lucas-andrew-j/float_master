import dateutil
from datetime import timedelta

class Holiday_Handler:
    
    holiday_dict = {}
    holidays_arr = []
    
    def __init__(self, first_year, last_year):
        if last_year < first_year:
            num_years = first_year - last_year
            first_year = last_year
            last_year = first_year + num_years
        
        for year in range(first_year, last_year + 1):
            self.__add_year(year)
            
    def __add_year(self, year):
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
    
    def __add_new_year(self, year):
        actual_holiday = dateutil.parser.parse("1/1/%d" % year).date()
        return Holiday_Handler.__nearest_weekend_day(actual_holiday)
    
    def __add_mlk_holiday(self, year):
        return Holiday_Handler.__get_nth_weekday(0, 3, 1, year)
    
    def __add_presidents_day(self, year):
        return Holiday_Handler.__get_nth_weekday(0, 3, 2, year)
    
    def __add_memorial_day(self, year):
        return Holiday_Handler.__get_nth_weekday(0, 4, 5, year)
    
    def __add_juneteenth(self, year):
        actual_holiday = dateutil.parser.parse("6/19/%d" % year).date()
        return Holiday_Handler.__nearest_weekend_day(actual_holiday)
    
    def __add_independence_day(self, year):
        actual_holiday = dateutil.parser.parse("7/4/%d" % year).date()
        return Holiday_Handler.__nearest_weekend_day(actual_holiday)
    
    def __add_labor_day(self, year):
        return Holiday_Handler.__get_nth_weekday(0, 1, 9, year)
    
    def __add_columbus_day(self, year):
        return Holiday_Handler.__get_nth_weekday(0, 2, 10, year)
    
    def __add_veterans_day(self, year):
        return Holiday_Handler.__get_nth_weekday(0, 2, 11, year)
    
    def __add_thanksgiving(self, year):
        return Holiday_Handler.__get_nth_weekday(3, 4, 11, year)
    
    def __add_add_christmas(self, year):
        actual_holiday = dateutil.parser.parse("12/25/%d" % year).date()
        return Holiday_Handler.__nearest_weekend_day(actual_holiday)
        
    @staticmethod
    def __nearest_weekend_day(date):
        weekend_day = date.weekday()
        return date + timedelta(days = (((weekend_day + 1) // 6) * -1 + ((weekend_day + 1) // 7) * 2))
    
    @staticmethod
    def __get_nth_weekday(weekday, n, month, year):
        first_weekday = dateutil.parser.parse("1/%d/%d" % (month, year)).weekday()
        
        if weekday > first_weekday:
            n = - 1
        
        day = 1 + weekday - first_weekday + n * 7
        
        return dateutil.parser.parse("%d/%d/%d" % (day, month, year))
        
