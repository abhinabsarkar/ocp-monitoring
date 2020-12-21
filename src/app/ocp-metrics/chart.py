import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as mtick

def bar_chart(ns_list, max_cpu_list, max_memory_list):
    # Set data in the graph
    data = {"Max CPU":max_cpu_list, "Max Memory":max_memory_list }
    # Plot the graph
    plotdata = pd.DataFrame(data, 
        index=ns_list
    )
    # Set the chart type as bar chart
    ax = plotdata.plot(kind='bar')
    # Set the title of the chart
    plt.title("Max CPU & Memory utilization (CPU threshold < 50%)")
    # Label x axis
    plt.xlabel("Namespaces")
    # Label y axis
    plt.ylabel("Utilization in %")
    # Set the y axis to 100%
    plt.ylim([0.0, 100.0])
    # Set the y axis in percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100, decimals=None, symbol='%'))
    # Set the grid lines in the graph
    plt.grid(True)
    # Save the chart as a file. bbox - adjusts the plot size
    plt.savefig('chart.png',dpi=125, bbox_inches = "tight")
    # Display the chart
    plt.show()