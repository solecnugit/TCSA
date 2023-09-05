import pandas as pd




def identify_consecutive_identical_call_stacks(perf_records_df: pd.DataFrame, degrees_of_freedom: int, direction: int) -> pd.DataFrame:
    """

    :param perf_records_df: timing call stacks
    :param degrees_of_freedom: The number of user-defined call stack layers. For the number of recognized layers of 
                               the call stack per thread, -1 means that the entire call stack is recognized.
    :param direction: bottom up 0 / top down 1。
    :return: 
    """

    column_name = 'call_stack'
    perf_records_df['user_defined_indentical_call_stacks'] = perf_records_df[column_name].apply(
        lambda x: get_user_defined_indentical_call_stacks(x, degrees_of_freedom, direction))
    perf_records_df['top_function'] = perf_records_df['user_defined_indentical_call_stacks'].apply(lambda x: x.split(';')[-1])

    threads_list = perf_records_df.tid.unique()
    records_df_list = [] 
    for thread in threads_list:
        thread_df = perf_records_df[perf_records_df.tid == thread]
        # Message: sometimes we use " compare_key = tmp_thread_df.loc[:, ('user_defined_indentical_call_stacks')] "
        compare_key = thread_df['user_defined_indentical_call_stacks']
        thread_df.loc[:, ('token')] = (compare_key != compare_key.shift()).cumsum()
        thread_df = thread_df.groupby(['token'], as_index=False).aggregate(lambda x: list(x))
        thread_df['duration_length'] = thread_df['user_defined_indentical_call_stacks'].apply(lambda x: len(x))
        thread_df['tid'] = thread_df['tid'].apply(lambda x: x[0])
        thread_df['command'] = thread_df['command'].apply(lambda x: x[0])
        thread_df['event'] = thread_df['event'].apply(lambda x: x[0])
        thread_df['ts_begin'] = thread_df['timestamp'].apply(lambda x: x[0])
        thread_df['ts_end'] = thread_df['timestamp'].apply(lambda x: x[-1])
        thread_df['user_defined_indentical_call_stacks'] = thread_df['user_defined_indentical_call_stacks'].apply(lambda x: x[0])
        thread_df['function_call_stack'] = thread_df['function_call_stack'].apply(lambda x: x[0])
        thread_df['call_stack'] = thread_df['call_stack'].apply(lambda x: x[0])
        records_df_list.append(thread_df)
    records_df = pd.concat(records_df_list)
    return records_df


def get_user_defined_indentical_call_stacks(function_list: list, degrees_of_freedom: int, direction: int) -> str:
    """

    :param function_list: a column of dataframs
    :param degrees_of_freedom: 
    :param direction: bottom up 0 / top down 1
    :return: string of the function call chain
    """
    original_length = len(function_list)
    length = min(degrees_of_freedom, original_length)

    # degrees_of_freedom -1 means max
    if (length == -1): 
        length = len(function_list)

    # direction 0 mean bottom up
    if (direction == 0): 
        function_list = function_list[0:length]
    else:
        function_list = function_list[(original_length - length):length]
    res_function_call = ';'.join([' '.join(j.split()[1:]) for j in function_list])
    return res_function_call


def filtering_operation(df: pd.DataFrame) -> pd.DataFrame:
    """ Filter out data from threads where the consecutive identical call stacks do not occur consistently.
        Support presetting of thread IDs/process names that do not care.

    :param df: 
    :return:
    """
    threshold_duration_length = 1
    df = df[df.duration_length > threshold_duration_length]
    useless_command_list = ["swapper"]
    for command in useless_command_list:
        df = df[df.command.str.contains(command) == False]
    # df = df.sort_values(by=['duration_length', 'ts_begin'], ascending=[False, True])
    return df


def divide_TOCC(df: pd.DataFrame) -> list:
    """

    :param df: 
    :return: 
    """
    length = len(df)
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
            if (len(tocc) > 1):
                tocc_list.append(tocc)

    tocc_df_list = []
    tocc_list.sort(key=lambda x: len(x), reverse=True)
    for tocc in tocc_list:
        tmp_tocc_df_list = []
        for i in range(len(tocc)):
            tmp_df = df[df.ts_begin == tocc[i]]
            tmp_tocc_df_list.append(tmp_df)
        tmp_tocc_df = pd.concat(tmp_tocc_df_list)
        tocc_df_list.append(tmp_tocc_df)
    return tocc_df_list


def distinguish_execution_mode(df_list: list) -> list:
    """

    :param df_list: each DataFrame in the list is each item in the TOCC.
    :return: Return a list with two DataFrames nested within each item, one for the user mode and one for the kernel mode.
        for example：
        [ [ df_kernel_1, df_user_1 ],
          [ df_kernel_2, df_user_2 ] ]
    """
    tocc_df_list = []
    for each_df in df_list:
        each_df['execution_mode'] = each_df['call_stack'].apply(lambda x: judge_execution_mode(x))
        kernel_tocc_df = each_df[each_df.execution_mode == 0]
        user_tocc_df = each_df[each_df.execution_mode == 1]
        kernel_user_tocc_df_list = [kernel_tocc_df, user_tocc_df]
        tocc_df_list.append(kernel_user_tocc_df_list)
    return tocc_df_list



def judge_execution_mode(call_stack: list) -> int:
    """Determine the mode of operation of the function executed by the thread.

    :param call_stack: call stack 
    :return:
    """
    top_function = call_stack[-1]
    top_function_list = top_function.split(' ')
    # Here the length of top_function_list is 3, 
    # 0 is the function address, 
    # 1 is the function name, 
    # 2 is the function source code corresponding path
    function_address = top_function_list[0]
    execution_mode = 1  # kernel 0, user 1

    # 64bit kernel space: 0xffffffff80000000~0xffffffffffffffff
    # 64bit user space: 0x0000000000000000~0x00007fffffffffff
    # 32bit kernel space: 0xc0000000~0xffffffff
    # 32bit user space: 0x00000000~0xbfffffff
    # TODO: Remove magic number.
    function_address_len = len(function_address)
    if(function_address_len > 10):
        if(function_address >= 'ffffffff80000000' and function_address <= 'ffffffffffffffff'):
            execution_mode = 0
    else:
        if(function_address >= 'c0000000' and function_address <= 'xffffffff'):
          execution_mode = 0  
 
    return execution_mode


def pruning_by_threshold(df_list: list, duration_length_threshold: int) -> list:
    """Implementation of filter pruning, mainly for the setting and implementation of custom thresholds

    :param df_list:
    :param threshold: 
    :return: 
        example：
        [df_1, df_2, df_3, ...]
    """
    res_df_list = []
    for each_df in df_list:
        if (duration_length_threshold == -1):
            tid_num = len(each_df)
            duration_length_sum = each_df['duration_length'].sum()
            duration_length_threshold = duration_length_sum / tid_num
        tmp_df = each_df[each_df.duration_length >= duration_length_threshold]
        res_df_list.append(tmp_df)
    return res_df_list


def duration_threshold_setting(df_list: list, duration_length_threshold: int = -1) -> list:
    """Customize thresholds for filtering.

    :param df_list: Each item in the list is a DataFrame List to be filtered, which depends 
                    largely on the processing time when the threads of
                     different time periods are stored in different DataFrames.
    :param duration_length_threshold: Custom set threshold value. We specify: -1 means use the mean value.
    :return: 
        example of results ：
        [ [df_kernel_1, df_kernel_2, ...],
          [df_user_1, df_user_2, ...] ]
    """
    kernel_tocc_df_list = []
    user_tocc_df_list = []
    for each_df_list in df_list:
        if (len(each_df_list[0]) > 0):
            kernel_tocc_df_list.append(each_df_list[0])
        if (len(each_df_list[1]) > 0):
            user_tocc_df_list.append(each_df_list[1])
    res_df_list = []
    tmp_res_df_list = [kernel_tocc_df_list, user_tocc_df_list]
    for each_df_list in tmp_res_df_list:
        tmp_res_df = pruning_by_threshold(each_df_list, duration_length_threshold)
        res_df_list.append(tmp_res_df)

    return res_df_list


def divide_each_subTOCC(df_list: list) -> list:
    """ Time overlap division for threads inside a single DataFrame

    :param df_list: 
    :return:
        example：
        [df_1, df_2, df_3, ...]
    """
    each_subTOCC_df_list = []
    for each_df in df_list:
        tmp_subTOCC_df_list = divide_TOCC(each_df)  # redivide
        each_subTOCC_df_list += tmp_subTOCC_df_list

    # NOTE: We believe that the more threads in a DataFrame, the more likely there is competition and therefore prioritize display.
    each_subTOCC_df_list = sorted(each_subTOCC_df_list, key=lambda x: len(x), reverse=True) 
    return each_subTOCC_df_list




def divide_subTOCC(df_list: list) -> list:
    """divide subTOCC

    :param df_list: 
    :return: 
        example：
         [ [df_kernel_1, df_kernel_2, ...],
          [df_user_1, df_user_2, ...] ]
    """
    # Handles kernel mode and user mode in TOCC, so here the df_list length is 2.
    subTOCC_df_list = []
    for each_df_list in df_list:
        # The first one is a list of df's in kernel mode, the second one is in user mode.
        tmp_subTOCC_df_list = divide_each_subTOCC(each_df_list)
        subTOCC_df_list.append(tmp_subTOCC_df_list)
    return subTOCC_df_list
