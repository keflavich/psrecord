import sys
import psutil
import time
import argparse

def main():

    parser = argparse.ArgumentParser(description='Record CPU and memory usage for a process')

    parser.add_argument('process_id', type=int, help='the process id')

    parser.add_argument('--log', type=str,
                        help='output the statistics to a file')

    parser.add_argument('--plot', type=str,
                        help='output the statistics to a plot')

    parser.add_argument('--duration', type=float,
                        help='how long to record for (in seconds). If not '
                             'specified, the recording is continuous until '
                             'the job exits.')

    parser.add_argument('--interval', type=int,
                        help='how long to wait between each sample (in '
                             'seconds). By default the process is sampled '
                             'as often as possible.')

    args = parser.parse_args()

    # Attach to process
    pr = psutil.Process(args.process_id)

    # Record start time
    start_time = time.time()

    if args.log:
        f = open(args.filename, 'w')

    log = {}
    log['times'] = []
    log['cpu'] = []
    log['mem_real'] = []
    log['mem_virtual'] = []

    # Start main event loop
    while True:

        # Find current time
        current_time = time.time()

        # Check if we have reached the maximum time
        if args.duration is not None and current_time - start_time > args.duration:
            break

        # Get current CPU and memory
        try:
            current_cpu = pr.get_cpu_percent()
            current_mem = pr.get_memory_info()
        except:
            break
        current_mem_real = current_mem.rss / 1024. ** 2
        current_mem_virtual = current_mem.vms / 1024. ** 2

        if args.log:
            f.write("{0:10.3f} {1:10.3f} {2:10.3f} {3:10.3f}\n".format(current_time, current_cpu, current_mem_real, current_mem_virtual))
            f.flush()

        if args.interval is not None:
            time.sleep(args.interval)

        # If plotting, record the values
        if args.plot:
            log['times'].append(current_time - start_time)
            log['cpu'].append(current_cpu)
            log['mem_real'].append(current_mem_real)
            log['mem_virtual'].append(current_mem_virtual)

    if args.log:
        f.close()

    if args.plot:

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

        ax.plot(log['times'],log['cpu'], '-', lw=1, color='r')

        ax.set_ylabel('CPU (%)', color='r')
        ax.set_xlabel('time (s)')

        ax2 = ax.twinx()

        ax2.plot(log['times'],log['mem_real'], '-', lw=1, color='b')

        ax2.set_ylabel('Real Memory (MB)', color='b')

        ax.grid()

        fig.savefig(args.plot)

    