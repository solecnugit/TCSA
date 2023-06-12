import pandas as pd

class DataPreparation():
    """Handle performance data such as function call stacks collected by Linux perf.
    
    """
    
    def __init__(self) -> None:
        pass
    
    def data_loading(self,input_file_path:str) -> pd.DataFrame:
        """Loading data.

        :param file_path: 
        :return: 
        """

        top_message = []  
        perf_records = []  
        call_stack = []  # temp call stacks
        command, timestamp, event_value, event, cpu, tid = '', '', '', '', '', ''
        with open(input_file_path, "r") as input_file:
            perf_file = input_file.readlines()
            for each_line in perf_file:
                if each_line[0] == '#':
                    top_message.append(each_line)
                elif each_line[0] == '\t':
                    call_stack.append(each_line.replace('\t', '').replace('\n', ''))
                elif each_line[0] == '\n':
                    call_stack.reverse()
                    perf_records.append((timestamp, command, tid, cpu, event, call_stack))
                    call_stack = []
                    command, timestamp, event, cpu, tid = '', '', '', '', ''
                else:
                    # Note: different versions of perf and different parameters collect different types of data
                    # swapper     0 [000] 691089.368816:     250000 cpu-clock:pppH:
                    position_flag = each_line.rfind('[')
                    if position_flag != -1:
                        tmp_perf_record = each_line[: position_flag - 1].split()
                        command = " ".join(
                            str(x) for x in tmp_perf_record[: len(tmp_perf_record) - 1]
                        )
                        tid = tmp_perf_record[len(tmp_perf_record) - 1]
                        tmp_perf_record = (
                            each_line[position_flag:]
                                .replace(':',"")
                                .replace('[',"")
                                .replace(']',"")
                                .split()
                        )
                        # tmp_perf_record: ['000', '694345.695642', '10101010', 'cpu-clockpppH']
                        cpu = tmp_perf_record[0]
                        timestamp = tmp_perf_record[1]
                        event = tmp_perf_record[2]
                    else:
                        tmp_perf_record = each_line.strip().split()
                        timestamp = tmp_perf_record[-3]
                        event = tmp_perf_record[-1]
                        tid = tmp_perf_record[-4]
                        command = "".join(
                            str(x) for x in tmp_perf_record[: -4]
                        )
        # Transform DataFrame
        title_columns = ['timestamp', 'command', 'tid', 'cpu', 'event', 'call_stack']
        perf_records_df = pd.DataFrame(perf_records, columns=title_columns)           
        return perf_records_df
    
    def data_processing(self,perf_records_df:pd.DataFrame) -> pd.DataFrame:
        # DataFrame -> ['timestamp', 'command', 'tid', 'cpu', 'event', 'call_stack']
        perf_records_df['tid'] = perf_records_df['tid'].astype(int)
        perf_records_df['cpu'] = perf_records_df['cpu'].astype(int)
        perf_records_df['timestamp'] = perf_records_df['timestamp'].astype(float)
        perf_records_df['top_function'] = perf_records_df.apply(
            lambda x: x.call_stack[0] if len(x.call_stack) > 0 else [], axis = 1
        )
        perf_records_df['top_function'] = perf_records_df['top_function'].astype(str)
        perf_records_df['function_call_stack'] = perf_records_df['call_stack'].apply(
            lambda x: ';'.join([' '.join(j.split()[1:-1]) for j in x])
        )
        perf_records_df['function_call_stack'] = perf_records_df['function_call_stack'].astype(str)

        return perf_records_df


# input_file_path = "/home/critical_path_analysis/TCSA/test_data/perf_data.txt"
# # input_file_path = "/home/critical_path_analysis/test_data/perf.txt"
# # input_file_path = "/home/data/redis_data/perf_script_ag_8.txt"
# result = DataPreparation().data_loading(input_file_path=input_file_path)
# result = DataPreparation().data_processing(result)
# print(result)
