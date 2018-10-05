#!/usr/bin/env python
# -*- coding: utf-8 -*-

import googlemaps
import json
from datetime import datetime

# Init api
API_KEY = "YOUR API KEY"
gmaps = googlemaps.Client(key=API_KEY)


date_points = ["7:00AM",
               "8:00AM",
               "9:00AM",
               "10:00AM",
               "4:00PM",
               "5:00PM",
               "6:00PM",
               "7:00PM"]


def get_steps_addresses(result):
    steps = []
    for index, leg in enumerate(result[0]["legs"]):
        if index == 0:
            start = leg["start_address"]
            steps.append(start)
        step = leg["end_address"]
        steps.append(step)
    return steps


def calc_duration(result, start_address, end_address):

    total_duration = 0
    in_interesting_interval = False
    for index, leg in enumerate(result[0]["legs"]):
        leg_start = leg["start_address"]
        leg_end = leg["end_address"]

        if leg_start == start_address:
            in_interesting_interval = True
        elif leg_start == end_address:
            in_interesting_interval = False

        if in_interesting_interval:
            leg_duration = (1/60.0) * float(leg["duration"]["value"])
            total_duration += leg_duration

    return total_duration


def test_query():
    # Request directions via public transit
    start = "Aachen"
    end = "Köln"
    waypoints = ["Düren", "Lechenich"]
    dep_time = datetime.now()
    result = gmaps.directions(start,
                              end,
                              waypoints=waypoints,
                              mode="driving",
                              departure_time=dep_time,
                              arrival_time=None,
                              optimize_waypoints=False)

    steps = get_steps_addresses(result)
    print(steps.__str__().replace("', ", "\n"))

    print(calc_duration(result, steps[0], steps[2]))
    print(calc_duration(result, steps[0], steps[1]))
    print(calc_duration(result, steps[1], steps[2]))
    print(calc_duration(result, steps[0], steps[3]))


if __name__ == "__main__":

    #test_query()

    living_places = [
        "Groß-Gerau",
        "Gross-Gerau, Am Römerhof",
        "Gross-Gerau, Wasserweg",
        "Gross-Gerau, Saalburgstraße",
        "Nauheim, Thomas-Mann-Straße",
        "Nauheim, Thomas-Mann-Straße",
        "Nauheim, Schillerstraße",
        "Nauheim, Schillerstraße"
    ]
    working_places = [
        "ING-Diba, Theodor-Heuss-Allee",
        "ING-Diba, Theodor-Heuss-Allee",
        "ING-Diba, Theodor-Heuss-Allee",
        "ING-Diba, Theodor-Heuss-Allee",
        "European Central Bank, Sonnemannstraße 20, 60314 Frankfurt am Main",
        "European Central Bank, Sonnemannstraße 20, 60314 Frankfurt am Main",
        "European Central Bank, Sonnemannstraße 20, 60314 Frankfurt am Main",
        "European Central Bank, Sonnemannstraße 20, 60314 Frankfurt am Main"
    ]

    user_requests = [
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7)
    ]

    start = living_places[0]
    end = working_places[-1]
    waypoints = living_places[1:] + working_places[:-1]
    #print(waypoints.__str__().replace("',", "\n"))
    result_total_route = gmaps.directions(start,
                              end,
                              waypoints=waypoints,
                              mode="driving",
                              arrival_time=None,
                              optimize_waypoints=False)
    print("Result len: %r" % len(result_total_route))

    steps = get_steps_addresses(result_total_route)
    print("Number of steps %r" % len(steps))

    sum_combined_routes = 0
    sum_individual_routes = 0
    sum_ratio = 0
    for start_index, stop_index in user_requests:

        # Get duration in combined route
        start_step = steps[start_index]
        end_step = steps[stop_index + 8]
        print("%r - to - %r" % (start_step, end_step))
        combined_route_duration = calc_duration(result_total_route, start_step, end_step)
        print(" -> combined duration: %r min" % combined_route_duration)

        # Get duration in individual route
        # Query route
        result_individual_route = gmaps.directions(
            living_places[start_index],
            working_places[stop_index],
            mode="driving",
            arrival_time=None)
        # Get duration
        individual_route_duration = calc_duration(
            result_individual_route,
            steps[start_index],
            steps[stop_index + 8]
        )
        print(" -> individual duration: %r min" % individual_route_duration)

        sum_combined_routes += combined_route_duration
        sum_individual_routes += individual_route_duration
        sum_ratio += combined_route_duration / individual_route_duration

    total_duration = calc_duration(result_total_route, steps[0], steps[-1])
    print("------ total route duration %r" % total_duration)

    print("combined: %r, individual: %r, rel: %r" % (sum_combined_routes, sum_individual_routes, sum_ratio / 8))


