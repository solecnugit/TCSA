import os
import subprocess
from matplotlib import pyplot as plt
import pandas as pd

class TimingGraph:
    def __init__(self,output_path,file_name):
        self.output_path = output_path
        self.file_name = file_name
        pass

    def gen_random_color(self) -> str:
   
        import random
        num_set = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        color = ""
        for i in range(6):
            color += num_set[random.randint(0, 14)]
        return "#" + color


    def gen_thread_timing_event_graph(self,df: pd.DataFrame) -> None:
        """

        :param df: The DataFrame needs to contain ts_begin, ts_end and the same events continuously.
        :return: 
        """
        df = df.sort_values(by=['ts_begin'])
        ts_begin_list = df['ts_begin'].tolist()
        ts_end_list = df['ts_end'].tolist()
        x_data = ts_begin_list + ts_end_list
        x_data.sort()

        tmp_df = df.groupby(['command', 'tid'], as_index=False).aggregate(lambda x: list(x))
        tmp_df['ts_begin'] = tmp_df['ts_begin'].apply(lambda x: min(x))
        tmp_df = tmp_df.sort_values(by=['ts_begin'])

        command_list = tmp_df['command'].tolist()
        tid_list = tmp_df['tid'].tolist()
        tid_set_list = tid_list
        tid_set_list = list(set(tid_set_list))
        tmp_tid_set_list_length = len(tid_set_list)
        tmp_length = len(tid_list)

        # Set the canvas size according to the number of threads
        if (tmp_length < 10):
            fig_width = 30
            fig_length = 10
        elif (tmp_length < 30):
            fig_width = 30
            fig_length = 40
        elif (tmp_length < 300):
            fig_width = 40
            fig_length = 100
        else:
            fig_width = 50
            fig_length = 200

        # Set canvas size
        fig, ax = plt.subplots(figsize=(fig_width, fig_length))

        # The width of the bar graph of the same event (consecutive identical call path) in the timing graph
        barh_y_height = 1 

        # The distance between two adjacent bar graphs
        barh_y_position = [i for i in range(2, 2 * (tmp_length + 1), 2)]  

        # For check breakpoint
        tid_check_breakpoint_df_list = []

        # Mark the same call path with the same color.
        identical_event = 'user_defined_indentical_call_stacks'
        identical_event_list = df[identical_event].tolist()
        identical_event_list = list(set(identical_event_list))
        identical_event_color = {}
        colors = []
        while (1):
            if (len(colors) == len(identical_event_list)):
                break
            else:
                while (1):
                    color = self.gen_random_color()
                    if (color not in colors):
                        colors.append(color)
                        break
                    else:
                        continue
        # Initialize the color corresponding to identical call paths.
        index = 0
        for i in identical_event_list:
            identical_event_color[i] = colors[index]
            index += 1

        y_data = [] 
        # The coloring generates a graph of persistent identical events of threads, which is plotted on a thread-by-thread basis, 
        # i.e., different "persistent identical events" of different time periods will be plotted at the same y-coordinate,
        # displaying different colors, and each thread will only appear once on the y-axis of the graph.
        for i in range(len(tid_list)):
            
            tmp_df = df[df.tid == tid_list[i]]
            tid_check_breakpoint_df_list.append(tmp_df)  # for check breakpoint
            cur_ts_begin_list = tmp_df['ts_begin'].tolist()
            cur_ts_end_list = tmp_df['ts_end'].tolist()
            cur_same_event = tmp_df[identical_event].tolist()
            cur_ax_data = []
            for j in range(len(cur_ts_begin_list)):
                ts_duration = cur_ts_end_list[j] - cur_ts_begin_list[j]
                cur_ax_data.append((cur_ts_begin_list[j], ts_duration))
                ax.broken_barh([(cur_ts_begin_list[j], ts_duration)], (barh_y_position[i], barh_y_height),
                               facecolors=identical_event_color[cur_same_event[j]])

            tmp_st = str(command_list[i]) + " " + str(tid_list[i])  
            y_data.append(tmp_st)

        xlim_min = min(ts_begin_list)
        xlim_max = max(ts_end_list)
        ax.set_xlim(xlim_min - 0.05, xlim_max + 0.05)
        ylim_min = 0
        ylim_max = (tmp_length + 1) * 2
        ax.set_ylim(ylim_min, ylim_max)
        ax.set_xlabel('time-thread')
        # ax.set_xticks(x_data)
        ax.set_yticks(barh_y_position[0:tmp_length])
        ax.set_yticklabels(y_data)
        ax.grid(True)

        output_file = self.output_path + "/thread_timing_evets_graph_" + self.file_name
        plt.savefig(output_file)

        # return tid_check_breakpoint_df_list  # Checking information on breakpoints
        pass


def gen_call_chains(output_path: str, file_name: str, df: pd.DataFrame) -> None:
    """

    :param output_path: 
    :param file_name: 
    :param df: 
    :return:
    """

    command_list = df['command'].tolist()
    call_stack_list = df['call_stack'].tolist()
    output_file = 'tmp_call_chains.txt'
    with open(output_file, "w") as f:
        com_length = len(command_list)
        for i in range(0,com_length):
            command = command_list[i]
            f.write(str(command) + "\n")
            call_stack = call_stack_list[i]
            call_stack.reverse()
            for each_func in call_stack:
                f.write("	" + str(each_func) + "\n")
            f.write("\n")

    filename = output_path + '/call_chains_' + file_name + '.svg'

    current_dir = os.path.dirname(os.path.abspath(__file__))
    gprof2dot_path = "gprof2dot.py"
    abs_script_path = os.path.join(current_dir, gprof2dot_path)

    cmd = "python3 " + abs_script_path + " -f perf -n0 -e0 tmp_call_chains.txt | dot -Tsvg -o {}".format(filename)
    subprocess.run(cmd,shell=True)
    os.remove('tmp_call_chains.txt')
    pass



def output_result_file(output_path: str, file_name: str, df: pd.DataFrame) -> None:
    """

    :param output_path: 
    :param file_name: 
    :param df: 
    :return:
    """
    output_result = []
    all_res_list = []
    df = df.groupby(['function_call_stack'],as_index=False).aggregate(lambda x: list(x))
    df['ts_begin'] = df['ts_begin'].apply(lambda x:min(x))
    df['ts_end'] = df['ts_end'].apply(lambda x:max(x))
    df = df.sort_values(by=['ts_begin'])
    ts_min = df['ts_begin'].min()
    ts_max = df['ts_end'].max()
    tmp_str = "=========================================="
    output_result.append(tmp_str)
    all_res_list.append(tmp_str)

    file_name_num = file_name.split('_')[1]
    tmp_str = "Contention group " + str(file_name_num) + " :" 
    all_res_list.append(tmp_str)
    tmp_str = "Time period: " + str(ts_min) + " ~ " + str(ts_max) 
    output_result.append(tmp_str)
    tmp_str = "Duration: " + str(ts_max - ts_min)
    all_res_list.append(tmp_str)
    df_length = len(df)
    tmp_str = "Function call stacks: " + str(df_length)
    all_res_list.append(tmp_str)
    all_threads_list = df['tid'].tolist()
    tmp_list = []
    for i in all_threads_list:
        tmp_list += i
    all_threads_list = list(set(tmp_list))
    all_threads = len(all_threads_list)
    tmp_str = "Total threads: " + str(all_threads)
    all_res_list.append(tmp_str)

    all_command_list = df['command'].tolist()
    tmp_list = []
    for i in all_command_list:
        tmp_list += i
    all_command_list = list(set(tmp_list))
    all_command = len(all_command_list)
    tmp_str = "Total processes: " + str(all_command)
    all_res_list.append(tmp_str)
    tmp_str = "Detailed information:" + file_name
    all_res_list.append(tmp_str)


    for i in range(df_length):
        tmp_str = "------------------------------------------"
        output_result.append(tmp_str)
        tmp_str = "Function call stack chain " + str(i+1)
        tmp_call_stack_chain = df.iloc[i]['function_call_stack']
        output_result.append(tmp_str)
        output_result.append(tmp_call_stack_chain)

        tmp_command = df.iloc[i]['command']
        tmp_command = list(set(tmp_command))
        tmp_str = "Processes: " + ','.join(str(x) for x in tmp_command)
        output_result.append(tmp_str)

        tmp_tid = df.iloc[i]['tid']
        tmp_tid = list(set(tmp_tid))
        tmp_str = "Threads: " +','.join(str(x) for x in tmp_tid)
        output_result.append(tmp_str)

    output_file = output_path + '/' + file_name
    with open(output_file, "w") as f:
        for each_line in output_result:
            f.write(str(each_line) + "\n")

    all_res_file = output_path + '/' + 'res'
    with open(all_res_file, "a+") as f:
        for each_line in all_res_list:
            f.write(str(each_line) + "\n")
    pass