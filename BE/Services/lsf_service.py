import json
from datetime import datetime

from rpds import List


def find_optimal_schedule(modules: List) -> List:
    selected_modules = find_selected_modules(modules)

    # Generate all possible combinations of timeslots
    timeslot_combinations = generate_combinations(selected_modules)

    # Find the combination with the minimum total time (including breaks)
    optimal_combination = find_optimal_combination(timeslot_combinations)

    return optimal_combination


def find_selected_modules(modules: List) -> List:
    selected_events = []
    # Filter the events for the selected modules
    with open("../Test_Data/LSF_data/veranstaltungen.json", 'r') as data:
        courses = json.loads(data.read())
        for module in courses:
            if module['modul'] in modules:
                for unit in module['einheiten']:
                    selected_events.append(unit)
    return selected_events


def generate_combinations(events):
    if not events:
        return [[]]

    result = []
    first, rest = events[0], events[1:]
    rest_combinations = generate_combinations(rest)

    for timeslot in first["termine"]:
        for combination in rest_combinations:
            result.append([{"title": first["name"], **timeslot}] + combination)

    return result


def find_optimal_combination(combinations):
    time_comb = []

    for combination in combinations:
        totalTime = 0
        sorted = sort_by_day(combination)
        for key, value in sorted.items():
            time = calculate_total_time(value)
            totalTime = totalTime + time
        time_comb.append((totalTime, combination))
    print(time_comb)
    best = time_comb[0]
    for time, comb in time_comb:
        if time < best[0]:
            best = (time, comb)
    return best


def sort_by_day(combination: List) -> dict:
    weekdays: dict = {}
    for unit in combination:
        if unit['wochentag'] not in weekdays.keys():
            weekdays[unit['wochentag']] = [unit]
        else:
            weekdays[unit['wochentag']].append(unit)
    return weekdays


def calculate_total_time(timeslots):
    times = [(time_str_to_datetime(slot['begin']), time_str_to_datetime(slot['ende'])) for slot in timeslots]
    min_time = min(start for start, end in times)
    max_time = max(end for start, end in times)
    return (max_time - min_time).total_seconds() / 3600  # return hours


def time_str_to_datetime(time_str):
    return datetime.strptime(time_str, '%H:%M')


# Example usage
#selected_modules = ["Einführung in die BWL und VWL", "Mathematik", "Einführung in die Wirtschaftsinformatik", "Grundlagen der Programmierung", "Rechnernetze", "Grundlagen des Software-Engineering"]
#optimal_schedule = find_optimal_schedule(selected_modules)
#
#print(optimal_schedule)
#time, comb = optimal_schedule
#print(time)
#for unit in comb:
#    print(unit)


def get_module_names() -> List:
    names = []
    with open("../Test_Data/LSF_data/veranstaltungen.json", "r") as data:
        modules = json.loads(data.read())
        for module in modules:
            names.append(module['modul'])
    return names