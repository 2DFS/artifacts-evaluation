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
import psutil

REPEAT = os.getenv("EXPERIMENT_REPEAT", 1)
COOLDOWN = 3 #SECONDS
EXPERIMENT_ALLOTMENT_RATIO = [0,0.25,0.5,0.75,1]
TDFS_FILES = [
    "splits/yolov3_seperated/field.json",
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

    
def gen_figure():

    df_xtended = pd.read_csv("results_fig10.csv")
    df_xtended['layer'] = df_xtended['layering']
    df_xtended['tot-nowd'] = df_xtended['tot']-df_xtended['download']
    df_xtended['ratio'] = df_xtended['ratio']*100
    df_xtended['ratio'] = df_xtended['ratio'].astype(int)
    df_xtended['model'] = df_xtended['file'].apply(map_name)
    df_xtended['hue'] = df_xtended['tool'] + "-" + df_xtended['model'].astype(str) 
    
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

    fig = plt.figure(figsize=[6,5.3])
    colors=sns.color_palette("Paired")

    docker_data = [["ratio","type","data","tool"]]
    tdfs_data = [["ratio","type","data","tool"]]
    for index, row in df_xtended.iterrows():
        #increase the time window to 1 second to take into account time it takes to reveal CPU spikes
        cpuvals = cpu_df[cpu_df["time"].between(row["timestamp"]-(row["tot"]*1000)-1000,row["timestamp"]+1000)][cpu_df["type"]=="CPU"]["amount"].values
        for v in cpuvals:
            if row["tool"]=="docker":
                docker_data.append([row["ratio"],"cpu",v,"docker"])
            else:
                tdfs_data.append([row["ratio"],"cpu",v,"tdfs"])

        memvals= cpu_df[cpu_df["time"].between(row["timestamp"]-(row["tot"]*1000)-1000,row["timestamp"]+1000)][cpu_df["type"]=="MEM"]["amount"].values
        for v in memvals:
            if row["tool"]=="docker":
                docker_data.append([row["ratio"],"mem",v,"docker"])
            else:
                tdfs_data.append([row["ratio"],"mem",v,"tdfs"])

    tdfs_df = pd.DataFrame(tdfs_data[1:],columns=tdfs_data[0])
    docker_df = pd.DataFrame(docker_data[1:],columns=docker_data[0])
    combined_df = pd.concat([tdfs_df,docker_df])
    
    combined_df['hue'] = combined_df['tool'] + "-" + combined_df['type']
    ax = sns.barplot(data=combined_df, x="ratio", y="data", hue="hue", errorbar="sd", palette=colors, linewidth=1, edgecolor='black',estimator="mean",hue_order=["tdfs-cpu","docker-cpu","tdfs-mem","docker-mem"])

    custom_lines = [patches.Patch(facecolor=colors[0],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[1],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[2],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[3],linewidth=1, edgecolor='black')]

    legend_colors = [[colors[0],colors[1]], 
            [colors[2],colors[3]]]
    categories = ['2DFS/Docker CPU', '2DFS/Docker Memory']
    legend_dict=dict(zip(categories,legend_colors))
    custom_lines = []
    for cat, col in legend_dict.items():
        custom_lines.append([mpatches.Patch(facecolor=c, label=cat) for c in col])
    ax.legend(handles=custom_lines,labels=categories,handler_map = {list: HandlerTuple(None)}, loc = "upper left", frameon = False,bbox_to_anchor=(-0.03, 1.04),ncol=1,fontsize='small')

    ax.set_ylim(ymin=0)

    ax.set_xlabel("Model Split Capacity (\%)")
    ax.set_ylabel("Resource Usage (\%)")

    fig.savefig('fig10_reproduced.pdf', bbox_inches='tight') 

if __name__ == "__main__":
    
    cpumonitor = None

    try:
        cpumonitor = start_cpu_monitoring()
        
        csvoutput = [
        ["timestamp","tool","ratio","file","tot","download","layering"]
        ]
        cleanup_tdfs()
        cleanup_docker()
        
        for ratio in tqdm(EXPERIMENT_ALLOTMENT_RATIO):

            print("\n ##EXPERIMENT CONFIG ## \n",str(ratio))

            for r in range(REPEAT):

                print("\n ##REPEAT ## \n",str(r))

                for manifest_n in tqdm(range(len(TDFS_FILES))):

                    print("\n ##FILE ## ",str(TDFS_FILES[manifest_n]))

                    try:
                        os.remove("2dfs.json")
                        os.remove("Dockerfile")
                    except:
                        pass

                    print("\n ##COOLDOWN## \n")
                    time.sleep(COOLDOWN)

                    #print("\n ##EXPERIMENT RUN ",r,"## \n")
                    
                    ## TDFS EXPERIMENT
                    # Generate 2dfs manifest
                    print("###TDFS EXPERIMENT##")
                    base_manifest_path = TDFS_FILES[manifest_n]
                    ratio_col = ratio
                    if ratio > 0:
                        ratio_col = ratio/TDFS_COLS[manifest_n]
                    tmp_manifest = gen_2dfs_manifest_from_files(base_manifest_path, "2dfs.json", ratio_col)

                    result = build_tdfs()
                    total, download_time, layering_time = parse_tdfs_output(result)
                    print("Total time: ",total, "Download time", download_time, "Layering time", layering_time)
                    csvoutput.append([round(time.time() * 1000),"tdfs",ratio,base_manifest_path,total,download_time,layering_time])
                    cleanup_tdfs()

                    ## DOCKER EXPERIMENT
                    print("###DOCKER EXPERIMENT##")
                    gen_dockerfile("2dfs.json")
                    result = build_docker()
                    total, download_time, layering_time = parse_docker_output(result)
                    print("Total time: ",total, "Download time", download_time, "Layering time", layering_time)
                    csvoutput.append([round(time.time() * 1000),"docker",ratio,base_manifest_path,total,download_time,layering_time])
                    cleanup_docker()


                    ## cleanup files
                    cleanup_dir("./files")

                    ##exporting results to csv
                    csvname = "results_fig10.csv"
                    try:     
                        os.remove(csvname)
                    except:
                        pass
                    with open(csvname, "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(csvoutput)
        
        cpumonitor.kill()
        
        # PLOT RESULTS
        gen_figure()

        print("✅ Experiment completed")
        print("Results saved to results_fig10.csv and cpumemoryusage.csv")
        print("Figure saved to fig10_reproduced.pdf")


    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if cpumonitor and cpumonitor.poll() is None:
            cpumonitor.terminate()
            try:
                cpumonitor.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cpumonitor.kill()