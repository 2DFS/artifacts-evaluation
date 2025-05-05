import os
from random import getrandbits
import subprocess
import json
from datetime import datetime
import csv
import time
from utils import *
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
from matplotlib.lines import Line2D
import matplotlib.patches as patches
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerTuple
from tqdm import tqdm
import colorcet as cc
import numpy as np
from datetime import date
import psutil

REPEAT = os.getenv("EXPERIMENT_REPEAT", 1)
COOLDOWN = 3 #SECONDS
EXPERIMENT_ALLOTMENT_RATIO = [0.25,0.5,0.75,1]
TDFS_FILES = [
    "splits/efficientnet_v2L_seperated/field.json",
    "splits/resnet50_seperated/field.json",
    ]

TDFS_COLS = [1,1,1,1,1,1,1,1,1,1,1,1,1,1]

plt.rcParams['font.size'] = 20
plt.rcParams['axes.linewidth'] = 2
plt.rcParams.update({'figure.autolayout': True})
plt.rcParams.update({'font.size': 20})
plt.rcParams['axes.axisbelow'] = True
plt.rcParams['font.family'] = "sans-serif"
plt.tight_layout()


def start_cpu_monitoring():
    """
    Start CPU monitoring using psutil.
    """
    cpu_monitor = subprocess.Popen(
        ["bash","extra/cpu.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return cpu_monitor


def start_bandwidth_monitoring():
    """
    Start Bandwidth monitoring using psutil.
    """
    bw_monitor = subprocess.Popen(
        ["bash","extra/bandwidth.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return bw_monitor

def map_name(x):
    if  "efficientnet_v2B0" in x:
        return "ENv2B0"
    if  "efficientnet_v2B1" in x:
        return "ENv2B1"
    if  "efficientnet_v2B2" in x:
        return "ENv2B2"
    if  "efficientnet_v2B3" in x:
        return "ENv2B3"
    if "efficientnet_v2S" in x:
        return "ENv2S"
    if "efficientnet_v2M" in x:
        return "ENv2M"
    if "efficientnet_v2L" in x:
        return "ENv2L"
    if "resnet50" in x:
        return "RN50"
    if "resnet101" in x:
        return "RN101"
    if "resnet152" in x:
        return "RN152"
    if "deeplab_v3" in x:
        return "DLv3"
    if "mobilenet_v2_seperated" in x:
        return "MNv2"
    if "mobilenet_v2_14" in x:
        return "MNv2L"
    if "yolov3" in x:
        return "YOLOv3"
    
def gen_fig11():

    df = pd.read_csv("results_fig11.csv")
    df['ratio'] = df['ratio']*100
    df['ratio'] = df['ratio'].astype(int)
    df['hue'] = df['tool'] + "-" + df['file'].astype(str) 

    fig = plt.figure(figsize=[6,5.3])
    colors=sns.color_palette("Paired")

    ax = sns.barplot(data=df, x="ratio", y="tot", hue="hue", errorbar="sd", palette=colors, linewidth=1, edgecolor='black', estimator="median")
    ax.bar_label(ax.containers[0], fontsize=15, rotation=90, padding=10)
    ax.bar_label(ax.containers[1], fontsize=15, rotation=90, padding=10)
    ax.bar_label(ax.containers[2], fontsize=15, rotation=90, padding=10)
    ax.bar_label(ax.containers[3], fontsize=15, rotation=90, padding=10)
    custom_lines = [patches.Patch(facecolor=colors[0],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[1],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[2],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[3],linewidth=1, edgecolor='black')]

    legend_colors = [[colors[0],colors[1]], 
            [colors[2],colors[3]]]
    categories = ['2DFS/Docker ENv2L', '2DFS/Docker RN50']
    legend_dict=dict(zip(categories,legend_colors))
    custom_lines = []
    for cat, col in legend_dict.items():
        custom_lines.append([mpatches.Patch(facecolor=c, label=cat) for c in col])
    ax.legend(handles=custom_lines,labels=categories,handler_map = {list: HandlerTuple(None)}, loc = "upper left", frameon = False,bbox_to_anchor=(-0.03, 1.04),ncol=1,fontsize='small')

    ax.set_ylabel("Time (s)")
    ax.set_xlabel("Partition Size (\%)")

    ax.set_ylim(ymin=0)
    ax.set_yticks(range(0,7,1),labels=range(0,7,1),fontfamily='sans-serif')

    fig.savefig('fig11_reproduced.pdf', bbox_inches='tight')


def gen_fig12():

    df = pd.read_csv("results_fig11.csv")
    df['ratio'] = df['ratio']*100
    df['ratio'] = df['ratio'].astype(int)
    df['hue'] = df['tool'] + "-" + df['file'].astype(str) 

    today = date.today()
    exp_date = str(today.strftime("%Y-%m-%d"))
    bandwidth_data = []
    bandwidth_data.append(["Time","docker0-in","docker0-out","tot-in","tot-out"])
    with open("bandwidth-result.log") as f:
        lines = f.readlines()
        for line in lines:
            if not "Time" in line and not "HH:MM:SS" in line:
                line_split = line.split(" ")
                filtered_words = []
                for word in line_split:
                    if word.strip():
                        filtered_words.append(word.replace("\n", ""))
                bandwidth_data.append(filtered_words)

    df_bandwidth = pd.DataFrame(bandwidth_data[1:], columns=bandwidth_data[0])

    #convert time from yyyy-mm-dd HH:MM:SS to unix timestamp millis
    df_bandwidth['Time'] = df_bandwidth['Time'] + " " + exp_date
    # Assuming 'df_bandwidth' is your DataFrame
    df_bandwidth['Time'] = pd.to_datetime(df_bandwidth['Time'], format='%H:%M:%S %Y-%m-%d')
    #get current timezone 
    timezone = datetime.now().astimezone().tzinfo
    df_bandwidth['Time'] = df_bandwidth['Time'].dt.tz_localize(timezone).astype(int) / 10**6
    df_bandwidth['Time'] = df_bandwidth['Time'].astype(int)


    colors=sns.color_palette("Paired")

    fig = plt.figure(figsize=[6,5.3])

    for index, row in df.iterrows():
        df.loc[index, 'bandwidth-in'] = df_bandwidth[df_bandwidth["Time"].between(row["timestamp"]-(row["tot"]*1000),row["timestamp"]+1000)]["docker0-in"].astype(float).mean()
        df.loc[index, 'bandwidth-out'] = df_bandwidth[df_bandwidth["Time"].between(row["timestamp"]-(row["tot"]*1000),row["timestamp"]+1000)]["docker0-out"].astype(float).mean()

    ax = sns.barplot(data=df, x="ratio", y="bandwidth-in", hue="hue", errorbar="sd", palette=colors,linewidth=1, edgecolor='black')


    legend_colors = [[colors[0],colors[1]], 
            [colors[2],colors[3]]]
    categories = ['2DFS/Docker ENv2L', '2DFS/Docker RN50']
    legend_dict=dict(zip(categories,legend_colors))
    custom_lines = []
    for cat, col in legend_dict.items():
        custom_lines.append([mpatches.Patch(facecolor=c, label=cat) for c in col])
    ax.legend(handles=custom_lines,labels=categories,handler_map = {list: HandlerTuple(None)}, loc = "upper left", frameon = False,bbox_to_anchor=(0, 1.03),ncol=1,fontsize='small')

    ax.set_ylim(ymin=0)
    #ax.set_yticks(range(0,90000,20000),range(0,90000,20000),fontfamily='sans-serif')

    ax.set_ylabel("Usage (KB/s)")
    ax.set_xlabel("Partition Size (\%)")
    fig.savefig('fig12_reproduced.pdf', bbox_inches='tight')     


def gen_fig13():

    df = pd.read_csv("results_fig11.csv")
    df['ratio'] = df['ratio']*100
    df['ratio'] = df['ratio'].astype(int)
    df['hue'] = df['tool'] + "-" + df['file'].astype(str) 

    cpu_df = pd.read_csv("cpumemoryusage.csv")
    cpu_df['amount'] = cpu_df['amount'].astype(str)
    cpu_df['type'] = cpu_df['type'].astype(str)
    cpu_df['time'] = cpu_df['time'].astype(float)
    cpu_df['type'] = cpu_df['type'].str.replace("%","")
    cpu_df['amount'] = cpu_df['amount'].str.replace("%","").str.replace("Gi","").str.replace("Mi","").astype(float)
    total_memory = psutil.virtual_memory().total / (1024 ** 3)
    cpu_df['amount'] = cpu_df.apply(
        lambda row: row['amount']*100 / total_memory if row['type'] == "MEM" else row['amount'],
        axis=1
    )
    print(cpu_df)

    colors = sns.color_palette(cc.glasbey_light, n_colors=25)
    fig = plt.figure(figsize=[6,5.3])

    for index, row in df.iterrows():
        df.loc[index, 'cpu'] = cpu_df[cpu_df["time"].between(row["timestamp"]-(row["tot"]*1000)-5000,row["timestamp"]+5000)][cpu_df["type"]=="CPU"]["amount"].mean()
        df.loc[index, 'mem'] = cpu_df[cpu_df["time"].between(row["timestamp"]-(row["tot"]*1000),row["timestamp"])][cpu_df["type"]=="MEM"]["amount"].mean()
    #    df.loc[index, 'disk'] = cpu_df[cpu_df["time"].between(row["timestamp"]-(row["tot"]*1000),row["timestamp"]-1000)][cpu_df["type"]=="DISK"]["amount"].mean()/2

    ax = sns.ecdfplot(data=df[df["tool"]=="tdfs"], x="cpu", hue="ratio", palette=colors[1:], linewidth=2)
    ax = sns.ecdfplot(data=df[df["tool"]=="docker"], x="cpu", hue="ratio", palette=colors[1:], linewidth=2, linestyle='--')
    #ax = sns.lineplot(data=df, x="ratio", y="disk", hue="tool", errorbar="sd", palette=colors[1:], linewidth=2, linestyle='-.')




    custom_lines = [Line2D([0], [0], color=colors[1], linewidth=2, linestyle='-'),
                    Line2D([0], [0], color=colors[2], linewidth=2, linestyle='-'),
                    Line2D([0], [0], color=colors[3], linewidth=2, linestyle='-'),
                    Line2D([0], [0], color=colors[4], linewidth=2, linestyle='-'),
                    Line2D([0], [0], color="black", linewidth=2, linestyle='-'),
                    Line2D([0], [0], color="black", linewidth=2, linestyle='--')]
                    #Line2D([0], [0], color="black", linewidth=2, linestyle='-.')]
    ax.legend(custom_lines, ['25%','50%','75%','100%','Docker', '2DFS'], loc = "lower right", frameon = False, ncol=1, title="Partition Size",fontsize='small')
    ax.set_ylim(ymin=0)

    ax.set_ylabel("CDF")
    ax.set_xlabel("CPU Usage During Pull (\%)")
    ax.set_yticks([0,0.2,0.4,0.6,0.8,1],[0,0.2,0.4,0.6,0.8,1],fontfamily='sans-serif')



    fig.savefig('fig13_reproduced.pdf', bbox_inches='tight')


if __name__ == "__main__":
    
    cpumonitor = None
    bandwidthmonitor = None

    try:
        cpumonitor = start_cpu_monitoring()
        bandwidthmonitor = start_bandwidth_monitoring()
        
        csvoutput = [
        ["timestamp","tool","ratio","file","tot","download"]
        ]
        cleanup_tdfs()
        cleanup_docker()
        
        ## TDFS EXPERIMENT

        # Generate 2dfs manifest
        for manifest_n in tqdm(range(len(TDFS_FILES))):
            
            print("\n ##FILE ## \n",str(TDFS_FILES[manifest_n]))

            try:
                os.remove("2dfs.json")
                os.remove("Dockerfile")
            except:
                pass

            max_ratio_col = 1/TDFS_COLS[manifest_n]
            base_manifest_path = TDFS_FILES[manifest_n]
            tmp_manifest = gen_2dfs_manifest_from_files(base_manifest_path, "2dfs.json", max_ratio_col)
            result = build_tdfs()
            print(result)
            result = push_tdfs("")
            print(result)
            cleanup_tdfs()
            
            for ratio in EXPERIMENT_ALLOTMENT_RATIO:
                print("\n ##EXPERIMENT CONFIG ## \n",str(ratio)) 

                print("###Build Docker##")
                cleanup_docker()
                gen_dockerfile_partitioned("2dfs.json",ratio)
                result = build_docker()
                print(result)
                result = push_docker()
                print(result)

                for r in tqdm(range(REPEAT)):
                    print("\n ##REPEAT ## \n",str(r))

                    print("###TDFS EXPERIMENT##")
                    cleanup_docker()
                    time.sleep(COOLDOWN)
                    #print("Tot 2dfs layers...")
                    #print(int(len(tmp_manifest["allotments"])*ratio))
                    partition = "--0.0."+str(int(len(tmp_manifest["allotments"])*ratio))+".0"
                    print("partition:",partition)

                    result = pull_docker(partition,tdfs=True)
                    #print(result)
                    total, download_time, layering_time = parse_docker_output(result)
                    csvoutput.append([round(time.time() * 1000),"tdfs",ratio,base_manifest_path,total,download_time])


                    print("###DOCKER EXPERIMENT##")
                    cleanup_docker()
                    time.sleep(COOLDOWN)
                    result = pull_docker("",tdfs=False)
                    #print(result)
                    total, download_time, layering_time = parse_docker_output(result)
                    csvoutput.append([round(time.time() * 1000),"docker",ratio,base_manifest_path,total,download_time])

                    ##exporting results to csv
                    csvname = "results_fig11.csv"
                    try:     
                        os.remove(csvname)
                    except:
                        pass
                    with open(csvname, "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(csvoutput)
        
        cpumonitor.kill()
        bandwidthmonitor.kill()
        
        # PLOT RESULTS
        gen_fig11()
        gen_fig12()
        gen_fig13()

        print("✅ Experiment completed")
        print("Results saved to results_fig11.csv, bandwidth-result.log and cpumemoryusage.csv")
        print("Figure saved to fig11_reproduced.pdf, fig12_reproduced.pdf and fig13_reproduced.pdf")


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        bandwidthmonitor.kill()
        cpumonitor.kill()