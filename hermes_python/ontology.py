# -*- coding: utf-8 -*-

from __future__ import absolute_import
from collections import defaultdict
from six.moves import range


from ctypes import string_at, c_double
from .ffi.ontology import CAmountOfMoneyValue, CTemperatureValue, CInstantTimeValue, CTimeIntervalValue, CDurationValue


class IntentMessage(object):
    def __init__(self, session_id, custom_data, site_id, input, intent, slots):
        self.session_id = session_id
        self.custom_data = custom_data
        self.site_id = site_id
        self.input = input
        self.intent = intent
        self.slots = slots

    @classmethod
    def from_c_repr(cls, c_repr):
        session_id = c_repr.session_id
        custom_data = c_repr.custom_data
        site_id = c_repr.site_id
        input = c_repr.input
        intent = IntentClassifierResult.from_c_repr(c_repr.intent.contents)
        slots = SlotMap.from_c_repr(c_repr.slots.contents)  # TODO : Handle no slot case !
        return cls(session_id, custom_data, site_id, input, intent, slots)

class IntentClassifierResult(object):
    def __init__(self, intent_name, probability):
        self.intent_name = intent_name
        self.probability = probability

    @classmethod
    def from_c_repr(cls, c_repr):
        intent_name = c_repr.intent_name
        probability = c_repr.probability
        return cls(intent_name, probability)


class SlotMap(object):
    def __init__(self, mapping):
        self.__data = mapping

    def __getattr__(self, name):
        return self.__data.get(name, None)

    @classmethod
    def from_c_repr(cls, c_slots_list_repr):
        mapping = defaultdict(SlotsList)

        slots_list_length = c_slots_list_repr.size
        c_slots_array_repr = c_slots_list_repr.slots

        for i in range(slots_list_length):
            slot = Slot.from_c_repr(c_slots_array_repr[i])
            mapping[slot.slot_name].append(slot)
        return cls(mapping)


class SlotsList(list):  # An extension to make things easier to reach slot_values that are deeply nested in the IntentMessage datastructure.
    def first(self):
        if len(self) > 0:
            return self[0].slot_value
        else:
            return None
    def all(self):
        if len(self) > 0:
            return [element.slot_value for element in self]
        else:
            return None


class Slot(object):
    def __init__(self, slot_value, raw_value, entity, slot_name, range_start, range_end):
        self.slot_value = slot_value
        self.raw_value = raw_value
        self.entity = entity
        self.slot_name = slot_name
        self.range_start = range_start
        self.range_end = range_end

    @classmethod
    def from_c_repr(cls, c_repr):
        slot_value = SlotValue.from_c_repr(c_repr.value)
        raw_value = c_repr.raw_value
        entity = c_repr.entity
        slot_name = c_repr.slot_name
        range_start = c_repr.range_start
        range_end = c_repr.range_end

        return cls(slot_value, raw_value, entity, slot_name, range_start, range_end)


class SlotValue(object):
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = value

    @classmethod
    def from_c_repr(cls, c_repr):  # TODO : refactor to make it more generic
        value_type = c_repr.value_type

        if 1 == value_type:  # CUSTOM
            c_repr_custom_value = c_repr.value
            string_value = string_at(c_repr_custom_value)
            value = CustomValue(string_value)
        elif 2 == value_type: # NUMBER
            c_repr_number = c_double.from_address(c_repr.value)
            number = c_repr_number.value
            value = NumberValue(number)
        elif 3 == value_type: # ORDINAL
            value = None
        elif 4 == value_type: # INSTANTTIME
            c_repr_instant_time_value = CInstantTimeValue.from_address(c_repr.value)
            value = InstantTimeValue.from_c_repr(c_repr_instant_time_value)
        elif 5 == value_type: # TIMEINTERVAL
            c_repr_time_interval_value = CTimeIntervalValue.from_address(c_repr.value)
            value = TimeIntervalValue.from_c_repr(c_repr_time_interval_value)
        elif 6 == value_type: # AMOUNTOFMONEY
            c_repr_amount_of_money_value = CAmountOfMoneyValue.from_address(c_repr.value)
            value = AmountOfMoneyValue.from_c_repr(c_repr_amount_of_money_value)
        elif 7 == value_type: # TEMPERATURE
            c_repr_temperature_value = CTemperatureValue.from_address(c_repr.value)
            value = TemperatureValue.from_c_repr(c_repr_temperature_value)
        elif 8 == value_type: # DURATION
            c_repr_duration_value = CDurationValue.from_address(c_repr.value)
            value = DurationValue.from_c_repr(c_repr_duration_value)
        elif 9 == value_type: # PERCENTAGE
            c_repr_percentage = c_double.from_address(c_repr.value)
            value = float(c_repr_percentage)

        return cls(value_type, value)

    def first(self):
        pass

    def values(self):
        pass


class SessionStartedMessage(object):
    def __init__(self, session_id, custom_data, site_id, reactivated_from_session_id):
        self.session_id = session_id
        self.custom_data = custom_data
        self.site_id = site_id

    @classmethod
    def from_c_repr(cls, c_repr):
        session_id = c_repr.session_id
        custom_data = c_repr.custom_data
        site_id = c_repr.site_id
        reactivated_from_session_id = c_repr.reactivated_from_session_id
        return cls(session_id, custom_data, site_id, reactivated_from_session_id)


class SessionEndedMessage(object):
    def __init__(self, session_id, custom_data, site_id, termination):
        self.session_id = session_id
        self.custom_data = custom_data
        self.site_id = site_id
        self.termination = termination

    @classmethod
    def from_c_repr(cls, c_repr):
        session_id = c_repr.session_id
        custom_data = c_repr.custom_data
        site_id = c_repr.site_id
        termination = SessionTermination.from_c_repr(c_repr.termination)
        return cls(session_id, custom_data, site_id, termination)


class SessionQueuedMessage(object):
    def __init__(self, session_id, custom_data, site_id):
        self.session_id = session_id
        self.custom_data = custom_data
        self.site_id = site_id

    @classmethod
    def from_c_repr(cls, c_repr):
        session_id = c_repr.session_id
        custom_data = c_repr.custom_data
        site_id = c_repr.site_id
        return cls(session_id, custom_data, site_id)


class SessionTermination(object):
    def __init__(self, termination_type, data):
        self.termination_type = termination_type
        self.data = data

    @classmethod
    def from_c_repr(cls, c_repr):
        termination_type = c_repr.termination_type
        data = c_repr.data
        return cls(termination_type, data)

class CustomValue(object):
    def __init__(self, string_value):
        self.value = string_value


class NumberValue(object):
    def __init__(self, value):
        self.value = value



class AmountOfMoneyValue(object):
    def __init__(self, unit, value, precision):
        self.unit = unit
        self.value = value
        self.precision = precision

    @classmethod
    def from_c_repr(cls, c_repr):
        unit = c_repr.unit
        value = c_repr.value
        precision = c_repr.precision

        return cls(unit, value, precision)


class TemperatureValue(object):
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    @classmethod
    def from_c_repr(cls, c_repr):
        unit = c_repr.unit
        value = c_repr.value
        return cls(unit, value)


class InstantTimeValue(object):
    def __init__(self, value, grain, precision):
        self.value = value
        self.grain = grain
        self.precision = precision

    @classmethod
    def from_c_repr(cls, c_repr):
        value = c_repr.value
        grain = c_repr.grain
        precision = c_repr.precision

        return cls(value, grain, precision)


class TimeIntervalValue(object):
    def __init__(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date

    @classmethod
    def from_c_repr(cls, c_repr):
        from_date = c_repr.from_date
        to_date = c_repr.to_date
        return cls(from_date, to_date)


class DurationValue(object):
    def __init__(self, years, quarters, months, weeks, days, hours, minutes, seconds, precision):
        self.years = years
        self.quarters = quarters
        self.months = months
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.precision = precision

    @classmethod
    def from_c_repr(cls, c_repr):
        years = c_repr.years
        quarters = c_repr.quarters
        months = c_repr.months
        weeks = c_repr.weeks
        days = c_repr.days
        hours = c_repr.hours
        minutes = c_repr.minutes
        seconds = c_repr.seconds
        precision = c_repr.precision
        return cls(years, quarters, months, weeks, days, hours, minutes, seconds, precision)