#!/usr/bin/python3
from datetime import date, datetime
import os
import sys
import csv
import re


def check_arg_is_dir(i_dir):
    if not os.path.isdir(i_dir):
        return False
    return True


def open_csv_files(i_dir):
    file_and_csvreader_tuple_list = []
    for dirpath, subdirs, files in os.walk(i_dir):
        for file in files:
            if file.endswith('.csv') and file.startswith('participant-') and not file.endswith('result.csv'):
                f = open(os.path.join('', dirpath, file),
                         'r', encoding='UTF-16')
                csv_reader = csv.reader(f, delimiter='\t')
                file_and_csvreader_tuple_list.append((f, csv_reader))
    return file_and_csvreader_tuple_list


def close_files(files):
    for tuple in files:
        tuple[0].close()


def generate_attendance_dicts_list(files_tuples):
    attendance_list = []
    empty_dict = {}
    for tuple in files_tuples:
        attendance_dict = empty_dict.copy()
        line_count = 0
        for row in tuple[1]:
            if line_count != 0:
                attendance_dict[row[3]] = 0
            line_count += 1
        attendance_list.append(attendance_dict)
    return attendance_list


def get_meetings_duration_in_minutes(files_tuples):
    total_minutes_in_all_meetings = 0
    for tuple in files_tuples:
        line_count = 0
        tuple[0].seek(0)
        for row in tuple[1]:
            if line_count != 0:
                meeting_start_date = datetime.strptime(
                    row[1].split('=')[1][1:-1], "%Y-%m-%d %H:%M:%S")
                meeting_end_date = datetime.strptime(
                    row[2].split('=')[1][1:-1], "%Y-%m-%d %H:%M:%S")
                total_minutes_in_all_meetings += (
                    (meeting_end_date - meeting_start_date).seconds / 60)
                break
            line_count += 1
    return total_minutes_in_all_meetings


def calculate_minutes_for_attendancies(attendance_dicts, files_tuples):
    index = 0
    for triplet in files_tuples:
        file = triplet[0]
        file.seek(0)
        line_count = 0
        for row in triplet[1]:
            if line_count != 0:
                attendance_dicts[index][row[3]] += int(row[7].split()[0])
            line_count += 1
        index += 1


def make_dicts_name_unique(dicts_list):
    unique_dicts_list = []
    empty_dict = {}
    for dict in dicts_list:
        names_list = dict.keys()
        unique_dict = empty_dict.copy()
        for name in names_list:
            output = re.sub(r'[^A-Za-z ]', '', name).strip().lower().title()
            if output in unique_dict:
                unique_dict[output].append(name)
            else:
                unique_dict[output] = [name]
        unique_dicts_list.append(unique_dict)
    return unique_dicts_list


def sum_minutes_from_dicts(unique_names_dicts_list, attendance_dicts_with_minutes):
    dicts_list_result = []
    empty_dict = {}
    for unique_dict_name, attendance_dict in zip(unique_names_dicts_list, attendance_dicts_with_minutes):
        result_dict = empty_dict.copy()
        for name in unique_dict_name:
            if name == '':  # edge case for hebrew names
                for hebrew_attendee_name in unique_dict_name[name]:
                    if hebrew_attendee_name in result_dict:
                        result_dict[hebrew_attendee_name] += attendance_dict[hebrew_attendee_name]
                    else:
                        result_dict[hebrew_attendee_name] = attendance_dict[hebrew_attendee_name]
            else:
                for attendee_name in unique_dict_name[name]:
                    if name in result_dict:
                        result_dict[name] += attendance_dict[attendee_name]
                    else:
                        result_dict[name] = attendance_dict[attendee_name]
        dicts_list_result.append(result_dict)
    return dicts_list_result


def calculate_final_dict(dicts_list, directory, total_minutes):
    result_dict = {}
    for dict in dicts_list:
        for attendee_name in dict:
            if not attendee_name in result_dict:
                result_dict[attendee_name] = {
                    'attendance_duration': dict[attendee_name],
                    'attendance_percentage': 0
                }
            else:
                result_dict[attendee_name]['attendance_duration'] += dict[attendee_name]
        for attendee_name in result_dict:
            total_attendace_of_attendee_percentage = None
            if result_dict[attendee_name]['attendance_duration'] > total_minutes:
                total_attendace_of_attendee_percentage = 100
                result_dict[attendee_name]['attendance_duration'] = total_minutes
            else:
                total_attendace_of_attendee_percentage = round(
                    (result_dict[attendee_name]['attendance_duration'] / total_minutes) * 100, 2)

            result_dict[attendee_name] = {
                'attendance_duration': result_dict[attendee_name]['attendance_duration'],
                'attendance_percentage': total_attendace_of_attendee_percentage
            }
    result_dict['total_meetings_duration'] = total_minutes
    return result_dict


def get_attendance_dict_result(directory) -> dict | None:
    files_tuples = []
    try:
        input_dir = directory
        if not check_arg_is_dir(input_dir):
            print(
                f'Unable to locate participants file in given directory: {input_dir}')
            return {}
        else:
            files_tuples = open_csv_files(input_dir)
            attendance_dicts_list = generate_attendance_dicts_list(
                files_tuples)
            calculate_minutes_for_attendancies(
                attendance_dicts_list, files_tuples)
            unique_attendance_names_dicts_list = make_dicts_name_unique(
                attendance_dicts_list)
            dicts_list_result = sum_minutes_from_dicts(
                unique_attendance_names_dicts_list, attendance_dicts_list)
            total_minutes_for_all_meetings = get_meetings_duration_in_minutes(
                files_tuples)
            res = calculate_final_dict(
                dicts_list_result, input_dir, total_minutes_for_all_meetings)
            close_files(files_tuples)
            return res
    except Exception as ex:
        print('Something went wrong... unable to load data from file')
        print(ex)
        close_files(files_tuples)
        return {}
