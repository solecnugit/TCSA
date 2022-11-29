# How to use `detect_bw_sync.py`？

A new methodology for detecting busy-wait synchronization performance bugs through timing call stack.

# Usage
**`python detect_bw_sync.py <file_path> <output_path> [direction] [degrees_of_freedom] [threshold]`**

`file_path` : The path of the collected function call stack data, include the file name.

`output_path` : The path to store the output results.

` direction ` : The direction of identification of consecutive identical events(i.e., consecutive identical call stacks). 1 means top-down, 0 means bottom-up.

`degrees_of_freedom` : The depth when judging consecutive identical events for threads. 

` threshold ` : Set the threshold value for the number of durations. The default -1 means use the average value.




# Workflow
运行示例：

`python  detect_bw_sync.py /data/perf_script.txt /data/result 0 -1 -1` 

或（等同）

`python  detect_bw_sync.py /data/perf_script.txt /data/result` 

Step1: 加载和处理数据。
- 根据输入的路经(file_path)加载 perf script 转换的文本数据。 
- 如上：/data/perf_script.txt

Step2: 识别“连续相同事件（连续相同调用栈）。
- 用户设置识别的方向（direction）和识别的层数/深度（degrees_of_freedom）。
- 识别的方向可以设置为0或1，其中 bottom up 0 / top down 1。
- 识别的层数/深度，例如在 direction = 0 时，degrees_of_freedom = 2, 则识别 A->B->C->D 中的 A->B。默认值是 -1，识别调用栈中的全部函数。

Step3: 划分时间重叠的线程。

Step4: 用户设置阈值(threshold)。
- 设置对阈值用于过滤“连续相同次数”小于该值的线程记录。
- 默认情况下，使用均值（threshold = -1）做为阈值。

Step4: 区分线程的执行模式。

Step5: 输出检测结果。
- 结果包括检测的结果列表，列表中每一项对应着一个线程连续想相同事件时序图和对其中函数调用栈构建成的函数调用链。
- 结果存放在指定的路径：output_path。
- 如上： /data/result ，在 result 文件夹下，会有一个总结果文件和多个独立的待分析结果（每一个结果对应一个文本文件、一张线程时序图、一张函数调用链图）。

# Update Records
- 2022-11-1 init 
- 2022-11-4 补充结果输出和参数设置说明。
- 2022-11-19 补充函数调用链和用例说明。

