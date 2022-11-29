"""
 ====================== Analysis Algorithm =========================================
"""
# The same thread and the function call stack keeps the same data
def get_duration_length(df):
    thread_list = []
    thread_list = df.tid.unique()
    records = []
    for thread in thread_list:
        thread_df = df[df.tid == thread]
        # note: use flame_graph without the address !
        compare_key = thread_df['flame_graph']
        # compare_key = thread_df.loc[:, ('flame_graph')]
        thread_df.loc[:, ('token')] = (compare_key != compare_key.shift()).cumsum()
        thread_df = thread_df.groupby(['token'], as_index=False).aggregate(lambda x: list(x))
        thread_df['duration_length'] = thread_df['top_function'].apply(lambda x: len(x))
        thread_df['tid'] = thread_df['tid'].apply(lambda x: x[0])
        thread_df['command'] = thread_df['command'].apply(lambda x: x[0])
        thread_df['event'] = thread_df['event'].apply(lambda x: x[0])
        thread_df['call_depth'] = thread_df['call_depth'].apply(lambda x: x[0])
        thread_df['flame_graph'] = thread_df['flame_graph'].apply(lambda x: x[0])
        thread_df['top_function'] = thread_df['top_function'].apply(lambda x: x[0])
        thread_df['ts_begin'] = thread_df['timestamp'].apply(lambda x: x[0])
        thread_df['ts_end'] = thread_df['timestamp'].apply(lambda x: x[-1])
        # note: to check run mode
        thread_df['call_graph'] = thread_df['call_graph'].apply(lambda x: x[0])
        records.append(thread_df)
    records_df = pd.concat(records)
    return records_df


# user defined DF (Degree of Freedom)
# Implementation based on dataframe
def get_user_defined_same_event(function_list, degrees_of_freedom, direction):
    """
    :param function_list: call graph list , a column of dataframe
    :param degrees_of_freedom: user defined degrees of freedom
    :param direction: bottom up 0 / top down 1
    :return: string
    """
    # degrees_of_freedom -1 means max
    original_length = len(function_list)
    length = min(degrees_of_freedom, original_length)
    if (length == -1):
        length = len(function_list)
    # direction 0 mean bottom up
    if (direction == 0):
        function_list = function_list[0:length]
    else:
        function_list = function_list[(original_length - length):length]
    res_function_call = ';'.join([' '.join(j.split()[1:]) for j in function_list])
    return res_function_call


# get duration_length by user defined same events
def get_thread_consecutive_same_event_duration_length(df, degrees_of_freedom, direction):
    """
    :param df: all records data (dataframe)
    :param degrees_of_freedom: user defined degrees of freedom
    :param direction: bottom up 0 / top down 1
    :return: records of dataframe
    """
    column_name = 'call_graph'
    df['user_defined_same_event'] = df[column_name].apply(lambda x:get_user_defined_same_event(x, degrees_of_freedom, direction))
    df['top_event'] = df['user_defined_same_event'].apply(lambda x:x.split(';')[-1])
    thread_list = df.tid.unique()
    records = []
    for thread in thread_list:
        thread_df = df[df.tid == thread]
        # note: Here we are calling stacks that do not use address information
        compare_key = thread_df['user_defined_same_event']
        # compare_key = thread_df.loc[:, ('flame_graph')]
        thread_df.loc[:, ('token')] = (compare_key != compare_key.shift()).cumsum()
        thread_df = thread_df.groupby(['token'], as_index=False).aggregate(lambda x: list(x))
        thread_df['duration_length'] = thread_df['top_function'].apply(lambda x: len(x))
        thread_df['tid'] = thread_df['tid'].apply(lambda x: x[0])
        thread_df['command'] = thread_df['command'].apply(lambda x: x[0])
        thread_df['event'] = thread_df['event'].apply(lambda x: x[0])
        thread_df['call_depth'] = thread_df['call_depth'].apply(lambda x: x[0])
        # thread_df['flame_graph'] = thread_df['flame_graph'].apply(lambda x:x[0])
        thread_df['top_function'] = thread_df['top_function'].apply(lambda x: x[0])
        thread_df['ts_begin'] = thread_df['timestamp'].apply(lambda x: x[0])
        thread_df['user_defined_same_event'] = thread_df['user_defined_same_event'].apply(lambda x: x[0])
        thread_df['ts_end'] = thread_df['timestamp'].apply(lambda x: x[-1])
        # note: to check run mode
        thread_df['call_graph'] = thread_df['call_graph'].apply(lambda x: x[0])
        thread_df['top_event'] = thread_df['top_event'].apply(lambda x:x[0])
        records.append(thread_df)
    records_df = pd.concat(records)
    return records_df


# divide tocc(time overlap clip collection)
def divide_tocc(df):
    length = len(df)
    #     df = df[df.command.str.contains("swapper")==False]
    df = df.sort_values(by=['ts_begin'])
    ts_begin_dic = {}
    tocc_list = []
    for i in range(length - 1):
        current_ts_begin = df.iloc[i]['ts_begin']
        current_ts_end = df.iloc[i]['ts_end']
        if (str(current_ts_begin) in ts_begin_dic.keys()):
            continue
        else:
            ts_begin_dic[str(current_ts_begin)] = 1
            ts_begin_bound = current_ts_begin
            ts_end_bound = current_ts_end
            tocc = []
            tocc.append(ts_begin_bound)
            for j in range(i + 1, length):
                tmp_ts_begin = df.iloc[j]['ts_begin']
                tmp_ts_end = df.iloc[j]['ts_end']
                if (str(tmp_ts_begin) in ts_begin_dic.keys()):
                    continue
                else:
                    if ((ts_begin_bound > tmp_ts_end) or (ts_end_bound < tmp_ts_begin)):
                        continue
                    else:
                        ts_begin_dic[str(tmp_ts_begin)] = 1
                        tocc.append(tmp_ts_begin)
                        if (ts_begin_bound > tmp_ts_begin):
                            ts_begin_bound = tmp_ts_begin
                        if (ts_end_bound < tmp_ts_end):
                            ts_end_bound = tmp_ts_end

            tocc_list.append(tocc)

    tocc_df_list = []
    tocc_list.sort(key=lambda x: len(x), reverse=True)

    # tocc > 1
    tmp_tocc_list = []
    for i in tocc_list:
        if (len(i) > 1):
            tmp_tocc_list.append(i)
    tocc_list = tmp_tocc_list

    for tocc in tocc_list:
        tmp_tocc_df = pd.DataFrame()
        tmp_tocc_df_list = []
        for i in range(len(tocc)):
            tmp_df = df[df.ts_begin == tocc[i]]
            tmp_tocc_df_list.append(tmp_df)
        tmp_tocc_df = pd.concat(tmp_tocc_df_list)
        #     gen_thread_time_cross_chart(tmp_tocc_df)
        tocc_df_list.append(tmp_tocc_df)
    return tocc_df_list


def judge_run_mode(call_graph_list):
    top_function = call_graph_list[-1]
    top_function_list = top_function.split(' ')
    function_address = top_function_list[0]
    function_name = top_function_list[1]
    function_source_path = top_function_list[2]
    # user 0 kernel 1
    run_mode = 0
    kernel_list = []
    kernel_address = 'ffffffff00000000'
    if (function_address >= kernel_address):
        run_mode = 1
    return run_mode


def divide_tocc_by_distinguishing_mode(df_list):
    # It is necessary to add a flag bit to judge the operation mode
    tocc_kernel_user_df_list = []
    for each_df in df_list:
        each_df['run_mode'] = each_df['call_graph'].apply(lambda x: judge_run_mode(x))
        tocc_kerne_each_df = each_df[each_df.run_mode == 1]
        tocc_user_each_df = each_df[each_df.run_mode == 0]
        tocc_kernel_user_each_df_list = [tocc_kerne_each_df, tocc_user_each_df]
        tocc_kernel_user_df_list.append(tocc_kernel_user_each_df_list)
    return tocc_kernel_user_df_list


# divide subTOCC ：More granular time division
def divide_subTocc(df):
    """
    :param df: tocc df
    :return:
    """
    # work time
    """
    Each spin lock task is performing an atomic operation, including locking, transaction 
    processing, and lock release. This time period is called critical zone time. Assuming 
    that each step requires a clock cycle, and assuming that the processor 
    frequency here is 2GHz, the time required is 3*1/2g = 3/2000000000.but..
    """
    delta = 0.05

    length = len(df)
    df = df.sort_values(by=['ts_begin'])

    subTocc_df_list = []
    subTocc_list = []
    ts_begin_dic = {}

    for i in range(length - 1):
        current_ts_begin = df.iloc[i]['ts_begin']
        current_ts_end = df.iloc[i]['ts_end']
        if (str(current_ts_begin) in ts_begin_dic.keys()):
            continue
        else:
            ts_begin_dic[str(current_ts_begin)] = 1
            ts_begin_bound = current_ts_begin
            ts_end_bound = current_ts_end
            subtocc = []
            subtocc.append(ts_begin_bound)
            for j in range(i + 1, length):
                tmp_ts_begin = df.iloc[j]['ts_begin']
                tmp_ts_end = df.iloc[j]['ts_end']
                if (str(tmp_ts_begin) in ts_begin_dic.keys()):
                    continue
                else:
                    if (abs(ts_end_bound - tmp_ts_end) <= delta):
                        ts_begin_dic[str(tmp_ts_begin)] = 1
                        subtocc.append(tmp_ts_begin)
                        if (ts_end_bound < tmp_ts_end):
                            ts_end_bound = tmp_ts_end
                    else:
                        continue

            subTocc_list.append(subtocc)

    subTocc_df_list = []
    subTocc_list.sort(key=lambda x: len(x), reverse=True)

    for subtocc in subTocc_list:
        tmp_tocc_df = pd.DataFrame()
        tmp_tocc_df_list = []
        for i in range(len(subtocc)):
            tmp_df = df[df.ts_begin == subtocc[i]]
            tmp_tocc_df_list.append(tmp_df)
        tmp_tocc_df = pd.concat(tmp_tocc_df_list)
        #     gen_thread_time_cross_chart(tmp_tocc_df)
        subTocc_df_list.append(tmp_tocc_df)
    return subTocc_df_list


# df : every tocc_df
def get_cluster_by_top_function(df):
    # top_event = 'top_function'
    top_event = 'top_function'
    top_func_df = df.groupby([top_event])['duration_length'].sum().reset_index(name='duration_length_total')
    # df : top function cluster
    top_func_df = top_func_df.sort_values(by=['duration_length_total'], ascending=[False])
    tmp_top_func_list = top_func_df['top_function'].tolist()
    # tmp_top_func_duration_length_total_list = tmp_records_df['duration_length_total'].tolist()
    #     for i in range(len(tmp_top_func_list)):
    #         print("------------------------------------------------------")
    #         print("No."+str(i+1)+": "+ str(tmp_top_func_list[i]))
    #         print("duration_length_total:" + str(top_func_df.iloc[i]['duration_length_total']))

    records_df_list = []
    for i in tmp_top_func_list:
        top_function_name = i
        tmp_df = df[df.top_function == top_function_name]
        tmp_records_df = tmp_df.sort_values(by=['duration_length', 'ts_begin'], ascending=[False, True])

        tmp_records_df_output = pd.DataFrame()
        tmp_records_df_output['tid'] = tmp_records_df['tid']
        tmp_records_df_output['flame_graph'] = tmp_records_df['flame_graph'].apply(lambda x:x[0])
        tmp_records_df_output['duration_length'] = tmp_records_df['duration_length']
        tmp_records_df_output['command'] = tmp_records_df['command']
        tmp_records_df_output['top_function'] = tmp_records_df['top_function']
        tmp_records_df_output = tmp_records_df_output.groupby(by=['flame_graph'], as_index=False).aggregate(
            lambda x: list(x))
        tmp_records_df_output['top_function'] = tmp_records_df_output['top_function'].apply(lambda x: x[0])
        tmp_records_df_output['duration_length_total'] = tmp_records_df_output['duration_length'].apply(
            lambda x: sum(x))
        records_df_list.append(tmp_records_df_output)

    return top_func_df, records_df_list
#
def get_all_cluster_by_top_function(tocc_kernel_user_df_list):
    top_func_df_list = []
    records_by_top_func_df_list = []
    for each_df in tocc_kernel_user_df_list:
        tocc_kernel_df = each_df[0]
        tocc_user_df = each_df[1]
        kernel_top_func_df, kernel_records_df_list = get_cluster_by_top_function(tocc_kernel_df)
        user_top_func_df, user_records_df_list = get_cluster_by_top_function(tocc_user_df)
        top_func_df_list.append([kernel_top_func_df,user_top_func_df])
        records_by_top_func_df_list.append([kernel_records_df_list,user_records_df_list])
    return top_func_df_list,records_by_top_func_df_list



# classify by top event
def get_cluster_by_top_event(df):
    top_event = 'top_event'
    user_defined_same_event = 'user_defined_same_event'
    # top_func_df means top_event_df !!!
    top_func_df = df.groupby([top_event])['duration_length'].sum().reset_index(name='duration_length_total')
    top_func_df = top_func_df.sort_values(by=['duration_length_total'], ascending=[False])
    tmp_top_func_list = top_func_df[top_event].tolist()
    records_df_list = []
    for i in tmp_top_func_list:
        top_function_name = i
        tmp_df = df[df.top_event == top_function_name]
        tmp_records_df = tmp_df.sort_values(by=['duration_length', 'ts_begin'], ascending=[False, True])
        tmp_records_df_output = pd.DataFrame()
        tmp_records_df_output['tid'] = tmp_records_df['tid']
        tmp_records_df_output['flame_graph'] = tmp_records_df['flame_graph'].apply(lambda x:x[0])
        tmp_records_df_output['duration_length'] = tmp_records_df['duration_length']
        tmp_records_df_output['command'] = tmp_records_df['command']
        tmp_records_df_output['top_event'] = tmp_records_df['top_event']
        tmp_records_df_output['top_function'] = tmp_records_df['top_function']
        tmp_records_df_output['user_defined_same_event'] = tmp_records_df['user_defined_same_event']
        tmp_records_df_output = tmp_records_df_output.groupby(by=[user_defined_same_event], as_index=False).aggregate(
            lambda x: list(x))
        tmp_records_df_output['top_function'] = tmp_records_df_output['top_function'].apply(lambda x:x[0])
        tmp_records_df_output['top_event'] = tmp_records_df_output['top_event'].apply(lambda x:x[0])
        tmp_records_df_output['duration_length_total'] = tmp_records_df_output['duration_length'].apply(
            lambda x: sum(x))
        records_df_list.append(tmp_records_df_output)
    return top_func_df, records_df_list

def get_all_cluster_by_top_event(tocc_kernel_user_df_list):
    top_func_df_list = []
    records_by_top_func_df_list = []
    for each_df in tocc_kernel_user_df_list:
        tocc_kernel_df = each_df[0]
        tocc_user_df = each_df[1]
        kernel_top_func_df, kernel_records_df_list = get_cluster_by_top_event(tocc_kernel_df)
        user_top_func_df, user_records_df_list = get_cluster_by_top_event(tocc_user_df)
        top_func_df_list.append([kernel_top_func_df,user_top_func_df])
        records_by_top_func_df_list.append([kernel_records_df_list,user_records_df_list])
    return top_func_df_list,records_by_top_func_df_list


def check_call_stack_for_discontinuities(df_list, all_records_df):
    """
        thread!
        df_list:tid_check_breakpoint_df_list
        all_records_df : raw records
    """
    for df in df_list:
        tid = df.iloc[0]['tid']
        command = df.iloc[0]['command']
        print("---------------------------------------------------------------")
        print("Command:" + str(command) + ",tid:" + str(tid))
        if (len(df) == 1):
            print("No breakpoint.")
        else:
            for i in range(len(df) - 1):
                first_call_graph = df.iloc[i]['flame_graph']
                first_ts_end = df.iloc[i]['ts_end']
                second_call_graph = df.iloc[i + 1]['flame_graph']
                second_ts_begin = df.iloc[i + 1]['ts_begin']
                mid_tid_raw_df = all_records_df[all_records_df.tid == tid]
                mid_tid_raw_df = mid_tid_raw_df[
                    (mid_tid_raw_df.timestamp > first_ts_end) & (mid_tid_raw_df.timestamp < second_ts_begin)]
                if (len(mid_tid_raw_df) == 0):
                    print("No record is collected in the middle.")
                    if (first_call_graph == second_call_graph):
                        print("no." + str(i + 1) + "possible missing sampling.")
                    else:
                        print("no." + str(i + 1) + ", Different before and after.")
                        print("first: " + str(first_call_graph))
                        print("second: " + str(second_call_graph))
                else:

                    print("There are other records collected in the middle.")
                    print("no." + str(i + 1) + ", Different before and after.")
                    print("records number:" + str(len(mid_tid_raw_df)))
                    mid_flame_graph_list = mid_tid_raw_df['flame_graph'].tolist()
    pass

# pruning operation
def df_of_pruning_operation(df):
    # maybe we need think about the threshold or hot defined
    threshold = 1
    # note: total_tid_num not means unique tid
#     total_tid_num = len(df)
#     total_tid_num = len(df.tid.unique())
#     total_duration_lenght = df.duration_length.sum()
#     avg_duration_length_per_tid = total_duration_lenght / total_tid_num
#     threshold = avg_duration_length_per_tid
    df = df[df.duration_length > threshold]
    useless_command_list = ["swapper"]
    for command in useless_command_list:
        df = df[df.command.str.contains(command) == False]

    # length = len(df)
    # res_df = pd.DataFrame()
    # df_list = []
    # for i in range(length):

    df = df.sort_values(by=['duration_length', 'ts_begin'], ascending=[False, True])
    return df



# function call chain generation
def gen_func_call_chain_message(df):
    import random
    df = df.sort_values(by=['ts_begin'])
    same_event = 'user_defined_same_event'
    tmp_df = df.groupby([same_event], as_index=False).aggregate(lambda x: list(x))
    tmp_df['ts_begin'] = tmp_df['ts_begin'].apply(lambda x: min(x))
    tmp_df['duration_length'] = tmp_df['duration_length'].apply(lambda x: sum(x))
    tmp_df['command'] = tmp_df['command'].apply(lambda x: list(set(x)))
    tmp_df = tmp_df.sort_values(by=['ts_begin'])
    # flame_graph means same function call events
    flame_graph_list = tmp_df[same_event].tolist()
    duration_length_list = tmp_df['duration_length'].tolist()
    command_list = tmp_df['command'].tolist()
    tmp_length = len(flame_graph_list)
    # linux_system_command_list = ['systemd','logrotate','crond']
    function_total_dic = {}
    function_name_list = []
    for i in range(tmp_length):
        tmp_flame_graph = flame_graph_list[i]
        tmp_function_list = tmp_flame_graph.split(';')
        for j in range(len(tmp_function_list)):
            if (tmp_function_list[j] != '[unknown]'):
                if (tmp_function_list[j] in function_name_list):
                    function_total_dic[tmp_function_list[j]] += duration_length_list[i]
                else:
                    function_total_dic[tmp_function_list[j]] = duration_length_list[i]
                    function_name_list.append(tmp_function_list[j])

    flame_graph_duration_length_list = []
    critical_section_function_list = []
    for i in range(tmp_length):
        tmp_flame_graph = flame_graph_list[i]
        tmp_function_list = tmp_flame_graph.split(';')
        tmp_flame_st = ""
        tmp_function_list_length = len(tmp_function_list)
        for j in range(tmp_function_list_length):
            if (tmp_function_list[j] == '[unknown]'):
                tmp_flame_st += str(tmp_function_list[j]) + "_total_" + str(duration_length_list[i])
            else:
                tmp_flame_st += str(tmp_function_list[j]) + "_total_" + str(function_total_dic[tmp_function_list[j]])
            #                 if(j == tmp_function_list_length - 1):
            #                     critical_section_function_list.append(str(tmp_function_list[j]) + "_total_" + str(function_total_dic[tmp_function_list[j]]))
            if (j != tmp_function_list_length - 1):
                tmp_flame_st += ';'

        flame_graph_duration_length_list.append(tmp_flame_st)

    # -- gen link graph
    quote = '"'
    print("strict digraph G {")
    print("fontname=" + quote + "Helvetica,Arial,sans-serif" + quote)
    print("node [fontname=" + quote + "Helvetica,Arial,sans-serif" + quote + "]")
    print("edge [fontname=" + quote + "Helvetica,Arial,sans-serif" + quote + "]")

    number = 0
    for i in range(len(flame_graph_duration_length_list)):

        number += 1
        tmp_call_graph = flame_graph_duration_length_list[i]

        st_list =  tmp_call_graph.split(";")
        st = ""
        for st_index in range(len(st_list)):
            tmp_st = st_list[st_index].split("(")[0]
            total_number = st_list[st_index].split("_total_")[1]
            st += tmp_st + "_total_duration_" + str(total_number)
            if(st_index != (len(st_list) - 1)):
                st += ";"

        st = st.replace("-", "_")

        st = st.replace(';', ' -> ')
        st = st.replace(".", "_")
        st = st.replace("@", "_")

        color_list = ['blue', 'purple', 'darkred', 'chocolate', 'teal', 'orange']
        color_st = color_list[random.randint(0, len(color_list) - 1)]

        print("subgraph cluster_" + str(number) + "{")
        print("node [style=filled];")
        st = st.replace(" ","_")
        st = st.replace('[', "")
        st = st.replace(']', "")
        st = st.replace('+', "")
        st = st.replace('(', "_")
        st = st.replace(")", "_")
        st = st.replace("/", "")
        st = st.replace("\ /", "")
        st = st.replace(":", "_")
        st = st.replace("*", "_")
        unknown_number = "unknown" + str(number)
        st = st.replace('unknown', unknown_number)
        st = "process" + str(number) + " -> " + st

        critical_section_function_st = st.split('->')[-1]
        if ("unknown" not in critical_section_function_st):
            critical_section_function_list.append(critical_section_function_st)

        st += " [ color= " + str(color_st) + "];"
        print(st)
        print("label = " + '"' + str(command_list[0][0]) + "..#" + str(number) + '"' + ";")

        print("color=" + str(color_st))
        print("}")

    print("critical_section [style=" + quote + "dashed" + quote + "," + "shape =" + quote + "Mdiamond" + quote + "]")
    for i in range(len(critical_section_function_list)):
        print(str(
            critical_section_function_list[i]) + "-> critical_section " + "[style=" + quote + "dashed" + quote + "]")
    print("}")
    pass


# output_flame_graph_path(tocc_kernel_user_df_list[0])


"""
 ====================== Analysis Algorithm =========================================
"""