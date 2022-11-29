from data_preparation import load_data, data_processing
from identify_ICE import get_thread_consecutive_same_event_duration_length, df_of_pruning_operation, divide_tocc, \
    divide_tocc_by_distinguishing_mode, get_all_cluster_by_top_event

# -- main funciton start--
if __name__ == '__main__':
    # calculate program run time - walltime
    import time

    start_time = time.time()
    # run only when the data is first loaded
    file_path = "/Users/ningli/Desktop/work/data/mysql/perf_script.txt"

    print("--------------- start data loading ... ------------------------")
    all_method_df = load_data(file_path)
    end_time_1 = time.time()
    print("end data loading," + "run time {:.3f}".format(end_time_1 - start_time))

    print("start data processing(including calling stack depth, stack top function, etc. )......")
    all_method_df = data_processing(all_method_df)
    all_method_df_back = all_method_df  # used in jupyter for backup
    all_method_df_length = len(all_method_df)
    end_time_2 = time.time()
    print("end of data processing, df_name: all_method_df , total records:" + str(
        all_method_df_length) + " ,run time {:.3f}".format(end_time_2 - end_time_1))

    print("---------------  identify consecutive identical events... ----------------")
    # records_df = get_duration_length(all_method_df)
    degrees_of_freedom = -1
    # bottom up 0 / top down 1
    direction = 0
    records_df = get_thread_consecutive_same_event_duration_length(all_method_df, degrees_of_freedom, direction)
    end_time_3 = time.time()
    print("end of processing, df_name: records_df " + " ,run time {:.3f}".format(end_time_3 - end_time_2))

    # pruning operation
    records_df_after_pruning = df_of_pruning_operation(records_df)
    end_time_4 = time.time()
    print("records_df_after_pruning: length is " + str(len(records_df_after_pruning)) + " ,run time {:.3f}".format(
        end_time_4 - end_time_3))

    # divide TOCC
    print("start divide tocc and get clusters......")
    tocc_df_list = divide_tocc(records_df_after_pruning)
    print("name of tocc: tooc_df_list (include: tocc1,tocc2,...,toccn), number of tocc:" + str(len(tocc_df_list)))

    tocc_kernel_user_df_list = divide_tocc_by_distinguishing_mode(tocc_df_list)
    print("tocc_kernel_user_df_list: [ [tocc_user_1, tocc_kernel_1], ... [tocc_user_n, tocc_kernel_n] ] ")
    print("the result is a ranking that is most likely to cause resource competition")

    # top_func_df_list : [
    #                       [tocc_kernel_1_top_func_df, tocc_user_1_top_func_df]
    #                       ,...,
    #                       [tocc_kernel_n_top_func_df, tocc_user_n_top_func_df]
    #                    ]
    # records_by_top_func_df_list : [ [ [tocc_kernel_1_top_func_1_records_df , ... , tocc_kernel_1_top_func_n_records_df],
    #                                   [tocc_user_1_top_func_1_records_df , ... , tocc_user_1_top_func_n_records_df]
    #                                   ] , ... ,
    #                                  [ [tocc_kernel_1_top_func_1_records_df , ... , tocc_kernel_1_top_func_n_records_df],
    #                                   [tocc_user_1_top_func_1_records_df , ... , tocc_user_1_top_func_n_records_df] ] ]
    top_func_df_list, records_by_top_func_df_list = get_all_cluster_by_top_event(tocc_kernel_user_df_list)
    end_time_5 = time.time()
    print("end divide tocc and get clusters , run time {:.3f}".format(end_time_5 - end_time_4))
    print(
        "top_func_df_list : [ tocc1 = [tocc_kernel_1_top_func_df, tocc_user_1_top_func_df] ,..., toccn = [tocc_kernel_n_top_func_df, tocc_user_n_top_func_df] ] ")
    print("records_by_top_func_df_list :"
          " [  tocc1 = [ tocc_kernel_1_top_func_df = [tocc_kernel_1_top_func_1_records_df , ... , tocc_kernel_1_top_func_n_records_df], tocc_user_1_top_func_df = [tocc_user_1_top_func_1_records_df , ... , tocc_user_1_top_func_n_records_df] ] ,"
          " ... , ]")

