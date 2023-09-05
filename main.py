
import os
import warnings
import sys
import time
from timing import DataPreparation
from filtering import distinguish_execution_mode, divide_TOCC, divide_subTOCC, duration_threshold_setting, filtering_operation, identify_consecutive_identical_call_stacks
from modeling import TimingGraph, gen_call_chains, output_result_file

warnings.filterwarnings("ignore")


def input_argv() -> str:
    """Handling the input parameters.

    :return:
    """
    try:
        perf_file_path = sys.argv[1]
    except Exception as e:
        print(e)
    try:
        output_path = sys.argv[2]
    except Exception as e:
        print(e)
    try:
        direction = int(sys.argv[3])
    except:
        direction = 0  # 0 represents a bottom-up call stack, and 1 represents a top-down call stack.
    try:
        degrees_of_freedom = int(sys.argv[4])
    except:
        degrees_of_freedom = -1  # -1 indicates that the entire call stack of the thread is matched.
    try:
        threshold = int(sys.argv[5])
    except:
        threshold = -1  # Set the threshold for the duration, with the default -1 indicating the use of the mean value.
    return perf_file_path,output_path,direction,degrees_of_freedom,threshold


if __name__ == '__main__':
   
    input_file_path,output_file_path,direction,degrees_of_freedom,threshold = input_argv()

    # The following parameters can be used for testing convenience.
    # -- test begin
    # input_file_path = "data/perf_data.txt"
    # output_file_path = "data/result"
    # direction = 0
    # degrees_of_freedom = -1
    # threshold = -1
    # -- test end

    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    start_time = time.time() 
    raw_data = DataPreparation().data_loading(input_file_path=input_file_path)
    timing_call_stacks_data = DataPreparation().data_processing(raw_data)

    end_time_2 = time.time()  
    records_df = identify_consecutive_identical_call_stacks(timing_call_stacks_data, degrees_of_freedom, direction)  
    records_df = filtering_operation(records_df) 
    tocc_df_list = divide_TOCC(records_df) 
    tocc_df_list = distinguish_execution_mode(tocc_df_list)  
    tocc_df_list_pruning = duration_threshold_setting(tocc_df_list, threshold)
    subTocc_df_list = divide_subTOCC(tocc_df_list_pruning)  
    # example:
    # [ [subTOCC_kernel_1,subTOCC_kernel_2,...]
    #   [subTOCC_user_1,subTOCC_user_2,...] ]

    end_time_3 = time.time() 
    # print("Time：" + str(end_time_8 - start_time))
    perf_records_df_length = len(timing_call_stacks_data)
    # print("Size of data volume：" + str(perf_records_df_length))
    # print("Time taken to load/process data:" + str(end_time_2 - start_time))
    print("Detecting time consuming(excluding time spent loading data):" + str(end_time_3-end_time_2))

    file_name_pre = 'res_'
    num = 1
    for each_df_list in subTocc_df_list:
        for each_df in each_df_list:
            file_name = file_name_pre + str(num)
            TimingGraph(output_file_path,file_name).gen_thread_timing_event_graph(each_df)
            output_result_file(output_file_path,file_name,each_df)
            gen_call_chains(output_file_path, file_name, each_df)
            num += 1



