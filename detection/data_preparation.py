"""
   Used to check all codes
"""
# lib
import pandas as pd
import matplotlib.pyplot as plt
import sys
import csv
from IPython.display import SVG, display
import warnings
warnings.filterwarnings("ignore")


"""
 ====================== Data Load Processing =========================================
"""
# load data
# note: acquisition command usage:perf record -ag -F xx xx
# data format : perf script -i data &> out.txt
def load_data(file_path):
    """
    :param file_path: perf data path
    :return: dataframe of all records
    """
    raw_data = []
    with open(file_path, "r") as f:
        for fLine in f:
            raw_data.append(fLine)
    print("total lines:" + str(len(raw_data)))

    # data to datafame
    top_message, all_method, call_graph = [], [], []
    command, timestamp, event_value, event, cpu, tid = '', '', '', '', '', ''

    # when the perf version is higher (usage -ag), the number of cycles will be collected more
    # perf version
    perf_version_flag = 0
    for line in raw_data:
        if line[0] == '#' or line[0] == '\t' or line[0] == '\n':
            continue
        else:
            perf_records_data = line.replace(':', '').replace('\n', '').split(']')[1]
            perf_records_data = perf_records_data.split()
            if (len(perf_records_data) == 2):
                perf_version_flag = 0
            elif (len(perf_records_data) == 3):
                perf_version_flag = 1
            break

    # perf usage :-ag
    if (perf_version_flag == 0):
        for line in raw_data:
            if line[0] == '#':
                top_message.append(line)
            elif line[0] == '\t':
                call_graph.append(line.replace('\t', '').replace('\n', ''))
            elif line[0] == '\n':
                all_method.append((timestamp, command, tid, cpu, event, call_graph))
                call_graph = []
                command, timestamp, event, cpu, tid = '', '', '', '', ''
            else:
                perf_records_data = line.replace(':', '').replace('\n', '').split(']')
                timestamp, event = perf_records_data[1].split()
                perf_records_data = perf_records_data[0].replace('[', '').split()
                tid, cpu = perf_records_data[-2], perf_records_data[-1]
                for data_index in range(len(perf_records_data) - 2):
                    command += str(perf_records_data[data_index]) + " "
                continue
        title_columns = ['timestamp', 'command', 'tid', 'cpu', 'event', 'call_graph']
    elif (perf_version_flag == 1):
        for line in raw_data:
            if line[0] == '#':
                top_message.append(line)
            elif line[0] == '\t':
                call_graph.append(line.replace('\t', '').replace('\n', ''))
            elif line[0] == '\n':
                all_method.append((timestamp, command, tid, cpu, event_value, event, call_graph))
                call_graph = []
                command, timestamp, event_value, event, cpu, tid = '', '', '', '', '', ''
            else:
                perf_records_data = line.replace(':', '').replace('\n', '').split(']')
                timestamp, event_value, event = perf_records_data[1].split()
                perf_records_data = perf_records_data[0].replace('[', '').split()
                tid, cpu = perf_records_data[-2], perf_records_data[-1]
                for data_index in range(len(perf_records_data) - 2):
                    command += str(perf_records_data[data_index]) + " "
                continue
        title_columns = ['timestamp', 'command', 'tid', 'cpu', 'event_value', 'event', 'call_graph']

    # data transform DataFrame
    all_method_df = pd.DataFrame(all_method, columns=title_columns)
    all_method_df['tid'] = all_method_df['tid'].astype(int)
    all_method_df['cpu'] = all_method_df['cpu'].astype(int)
    all_method_df['timestamp'] = all_method_df['timestamp'].astype(float)
    # all_method_df.head()
    # return all_method_df, top_message
    return all_method_df


# to solve the data as a string
def top_function_to_string(record):
    if len(record) == 0:
        return []
    return ' '.join(record.split()[1:])


# to correlate perf timestamp with use land timestamp
def correction_time(timestamp):
    # nothing to do now
    # maybe we can realize some functions when we need to calibrate the time
    # if we can find a time difference
    pass


# processing data
def data_processing(all_method_df):
    """
    :param all_method_df: all data records
    :return: processed data
    """
    # all_method_df['timestamp'] = all_method_df['timestamp'].apply(lambda x: float(x))
    # process the df ,count the depth of call graph ,and add new column as top function
    all_method_df['call_depth'] = all_method_df.apply(lambda x: len(x.call_graph), axis=1)
    all_method_df['top_function'] = all_method_df.apply(lambda x: x.call_graph[0] if len(x.call_graph) > 0 else [],
                                                        axis=1)
    all_method_df['top_function'] = all_method_df.apply(lambda x: top_function_to_string(x.top_function), axis=1)
    all_method_df['top_function'] = all_method_df.top_function.astype(str)
    all_method_df['call_graph_with_address'] = all_method_df['call_graph'].apply(
        lambda x: ';'.join([' '.join(j.split()[0:-1]) for j in x]))
    # cpu should be distinguished
    # all_method_df['ts_diff'] = all_method_df['timestamp'].shift(-1) - all_method_df['timestamp']
    # add new column to make flame graph by the call graph data
    all_method_df['call_graph'].apply(lambda x: x.reverse())
    all_method_df['flame_graph'] = all_method_df['call_graph'].apply(
        lambda x: ';'.join([' '.join(j.split()[1:-1]) for j in x]))
    # correction_time()
    all_method_df['flame_graph'] = all_method_df['flame_graph'].astype(str)

    return all_method_df


"""
 ====================== Data Load Processing =========================================
"""

