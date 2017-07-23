# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 15:13:51 2017

@author: Arnab

"""
import datetime
#from datetime import datetime,date
import calendar
from random import randint

#week_dictionary = {"1":"Sunday", "2":"Monday","3":"Tuesday","4":"Wednesday","5":"Thursday","6":"Friday","7":"Saturday"}

# This is a global variable
week_dictionary = {0:"Sunday", 1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",5:"Friday",6:"Saturday"}

max_delay_day = 10
min_delay_day = 3

delay_backward = randint(1,8)


# Given a week day it will return some day after that
def returnWeekDayForward(my_week_day,delay_forward):
    for i in week_dictionary:
        print i
        if(week_dictionary[i] == my_week_day): 
            i = (i + delay_forward) % 7
            break
    #print(week_dictionary[i])
    return week_dictionary[i]


# Given a week day it will return some day after that
def returnWeekDayBackward(my_week_day,delay_backward):
    for i in week_dictionary:
        print i
        if(week_dictionary[i] == my_week_day):            
            i = (i - delay_backward) 
            if(i < 0):
                 i = i * (-1)
            i = i % 7
            break
    return week_dictionary[i]


def getDeliveryDate():
    delivery_hrs_forward =  randint(10,18)
    if(delivery_hrs_forward < 10):
        delivery_hrs_forward = str(0) + str(delivery_hrs_forward)
        
    delivery_min_forward = randint(0,60)
    if(delivery_min_forward < 10):
        delivery_min_forward = str(0) + str(delivery_min_forward)
        
    delay_forward = randint(min_delay_day,max_delay_day)
    my_date = datetime.date.today()
    my_week_day = calendar.day_name[my_date.weekday()]
    
    my_date = my_date.strftime('%m/%d/%y')
    date_1 = datetime.datetime.strptime(my_date, "%m/%d/%y")
    delivery_date = date_1 + datetime.timedelta(days=delay_forward)    
    delivery_week_day = returnWeekDayForward(my_week_day,delay_forward)
    return (delivery_date.strftime('%m/%d/%Y') + " " + delivery_week_day + " " +  str(delivery_hrs_forward)+":"+str(delivery_min_forward))


def getBookingDate():
    booking_hrs_backwards =  randint(10,18)
    if(booking_hrs_backwards < 10):
        booking_hrs_backwards = str(0) + str(booking_hrs_backwards)
        
    booking_min_backwards = randint(0,60)
    if(booking_min_backwards < 10):
        booking_min_backwards = str(0) + str(booking_min_backwards)
        
    my_date = datetime.date.today()
    my_week_day = calendar.day_name[my_date.weekday()]
    
    my_date = my_date.strftime('%m/%d/%y')
    date_1 = datetime.datetime.strptime(my_date, "%m/%d/%y")
    booking_date = date_1 - datetime.timedelta(days=delay_backward)    
    booking_week_day = returnWeekDayBackward(my_week_day,delay_backward)
    return ( booking_date.strftime('%m/%d/%Y') + " "  + booking_week_day + " " + str(booking_hrs_backwards)+":"+str(booking_min_backwards))
    

def getContactNo():
    ext = randint(0,999)
    if(ext < 10):
        ext = str("00")+str(ext)
    elif(ext > 10 and ext < 100):
        ext = str("0")+str(ext)
    else:
        ext = str(ext)
        
    num = randint(100000,999999)    
    return str(ext)+"-"+ str(num)






