from ruqqus.helpers.base36 import *
import math
import random
import time


class ID:
    @property
    def base36id(self):
        return base36encode(self.id)

class Time:

    @property
    def age_string(self):

        age = self.age

        if age < 60:
            return "just now"
        elif age < 3600:
            minutes = int(age / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif age < 86400:
            hours = int(age / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif age < 2592000:
            days = int(age / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"

        now = time.gmtime()
        ctd = time.gmtime(self.created_utc)
        months = now.tm_mon - ctd.tm_mon + 12 * (now.tm_year - ctd.tm_year)

        if months < 12:
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = int(months / 12)
            return f"{years} year{'s' if years > 1 else ''} ago"

    @property
    def edited_string(self):

        age = int(time.time()) - self.edited_utc

        if age < 60:
            return "just now"
        elif age < 3600:
            minutes = int(age / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif age < 86400:
            hours = int(age / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif age < 2592000:
            days = int(age / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"

        now = time.gmtime()
        ctd = time.gmtime(self.created_utc)
        months = now.tm_mon - ctd.tm_mon + 12 * (now.tm_year - ctd.tm_year)

        if months < 12:
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = now.tm_year - ctd.tm_year
            return f"{years} year{'s' if years > 1 else ''} ago"

    @property
    def created_date(self):
        return time.strftime("%d %B %Y", time.gmtime(self.created_utc))

    @property
    def edited_date(self):
        return time.strftime("%d %B %Y", time.gmtime(self.edited_utc))



class Fuzzing:
    @property
    def score_fuzzed(self, k=0.01):
        real = self.score
        a = math.floor(real * (1 - k))
        b = math.ceil(real * (1 + k))
        return random.randint(a, b)