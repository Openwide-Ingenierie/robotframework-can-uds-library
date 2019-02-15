#!/usr/bin/env python3
import time


class AverageTime:
    """ AverageTime calculate the average time between given ticks
        The precision can go to 100µs between two ticks, faster it
        will be unprecise
    """

    def __init__(self):
        """Instanciate a AverageTime object
        """
        self.tick = time.time()
        self.last_tick = time.time()
        self.time_array = []
        self.average = 0
        self.isnew = 1

    def put_tick(self):
        """ Add a tick
        """
        if self.isnew == 1:
            self.tick = time.time()
            self.isnew = 0
        else:
            self.last_tick = time.time()
            time_elapsed = self.last_tick - self.tick
            self.time_array.append(time_elapsed)
            self.tick = time.time()

    def get_average(self):
        """ Return average time between ticks
        """
        self.average = sum(self.time_array)/float(len(self.time_array))
        return self.average

    def get_list(self):
        """ Return list of elapsed times
        """
        return self.time_array

    def clean_list(self):
        """ Clean the list
        """
        self.time_array = []
