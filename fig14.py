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

REPEAT = os.getenv("EXPERIMENT_REPEAT", 1)
COOLDOWN = 3 #SECONDS
EXPERIMENT_ALLOTMENT_RATIO = [0.25,0.5,0.75,1]
TDFS_FILES = [
    "splits/efficientnet_v2L_seperated/field.json",
    "splits/resnet50_seperated/field.json",
    ]
TDFS_COLS = [5,6]
CHANGE_FROM = 'top','bottom'

plt.rcParams['font.size'] = 20
plt.rcParams['axes.linewidth'] = 2
plt.rcParams.update({'figure.autolayout': True})
plt.rcParams.update({'font.size': 20})
plt.rcParams['axes.axisbelow'] = True
plt.rcParams['font.family'] = "sans-serif"
plt.tight_layout()

def gen_figure():

    df = pd.read_csv("results_fig14.csv")
    df['layer'] = df['layering']
    df['tot-nowd'] = df['tot']-df['download']
    df['ratio'] = df['ratio']*100
    df= df[df['ratio'].gt(1)]
    df['ratio'] = df['ratio'].astype(int)
    df['model'] = df['file'].apply(map_name) 
    df['hue'] = df['tool'] + "-" + df['file'].astype(str)
    df['hue-cat'] = df['tool'] + "" + df['model'] + "" + df['from'].astype(str)
        
    ## Fig 14 a
    fig = plt.figure(figsize=[6,5.3])
    colors=sns.color_palette("Paired")
    ax = sns.barplot(data=df[df["from"]=="top"], x="ratio", y="tot-nowd", hue="hue", errorbar="sd", palette=colors, linewidth=1, edgecolor='black')
    ax.bar_label(ax.containers[0], fontsize=15, rotation=90, padding=7)
    ax.bar_label(ax.containers[1], fontsize=15, padding=10)
    ax.bar_label(ax.containers[2], fontsize=15, rotation=90, padding=7)
    ax.bar_label(ax.containers[3], fontsize=15, rotation=90, padding=7)
    sns.barplot(ax=ax, data=df[df["from"]=="top"], x="ratio", y="layering", hue="hue", errorbar="sd", palette=colors, hatch="XX", linewidth=1, edgecolor='black')
    #plt.legend (ncol = 3, loc = "upper right", frameon = True)
    custom_lines = [patches.Patch(facecolor=colors[0],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[1],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[2],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor=colors[3],linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor='white',linewidth=1, edgecolor='black'),
                    patches.Patch(facecolor='white', hatch="XXX",linewidth=1, edgecolor='black')]
    ax.legend(custom_lines, ['Docker Efficientnet (Bottom)','Docker Efficientnet (Top)','Docker Resnet (Bottom)','Docker Resnet (Top)','Compression Time', 'Layer/Allotment Creation'], loc = "upper left", frameon = True, ncol = 2)
    ax.get_legend().remove()
    ax.set_ylabel("Time (s)")
    ax.set_xlabel("\% of Layers/Allotments Updates (Bottom)")
    ax.set_ylim(ymin=0)
    #ax.set_yticks(range(0,130,20),range(0,130,20),fontfamily='sans-serif')
    fig.savefig('fig14_b_reproduced.pdf', bbox_inches='tight')  

    ## Fig 14 b 
    fig = plt.figure(figsize=[6,5.3])
    colors=sns.color_palette("Paired")
    ax = sns.barplot(data=df[df["from"]=="bottom"], x="ratio", y="tot-nowd", hue="hue", errorbar="sd", palette=colors, linewidth=1, edgecolor='black',estimator="median")
    ax.bar_label(ax.containers[0], fontsize=15, rotation=90, padding=7)
    ax.bar_label(ax.containers[1], fontsize=15, rotation=0, padding=10)
    ax.bar_label(ax.containers[2], fontsize=15, rotation=90, padding=7)
    ax.bar_label(ax.containers[3], fontsize=15, rotation=90, padding=7)
    sns.barplot(ax=ax, data=df[df["from"]=="bottom"], x="ratio", y="layering", hue="hue", errorbar="sd", palette=colors, hatch="XX", linewidth=1, edgecolor='black',estimator="mean")
    legend_colors = [[colors[0],colors[1]], 
            [colors[2],colors[3]]]
    categories = ['2DFS/Docker ENv2L', '2DFS/Docker RN50']
    legend_dict=dict(zip(categories,legend_colors))
    custom_lines = []
    for cat, col in legend_dict.items():
        custom_lines.append([mpatches.Patch(facecolor=c, label=cat) for c in col])
    custom_lines.append(patches.Patch(facecolor='white', hatch="XXX",linewidth=1, edgecolor='black'))
    custom_lines.append(patches.Patch(facecolor='white',linewidth=1, edgecolor='black'))
    categories.append('Layer/Allotment Creation')
    categories.append('Compression Time')
    ax.legend(handles=custom_lines,labels=categories,handler_map = {list: HandlerTuple(None)}, loc = "upper left", frameon = False,bbox_to_anchor=(-0.03, 1.04),ncol=1,fontsize='small')
    ax.set_ylabel("Time (s)")
    ax.set_xlabel("\% of Layers/Allotments Updates (Top)")
    #ax.set_yticks(range(0,90,20),range(0,90,20),fontfamily='sans-serif')
    fig.savefig('fig14_a_reproduced.pdf', bbox_inches='tight')
    


if __name__ == "__main__":
    csvoutput = [
        ["timestamp","tool","ratio","from","file","tot","download","layering"]
    ]
    cleanup_tdfs()
    cleanup_docker()
    
    for ratio in tqdm(EXPERIMENT_ALLOTMENT_RATIO):

        print("\n ##EXPERIMENT CONFIG ## \n",str(ratio))

        for r in range(REPEAT):

            print("\n ##REPEAT ## \n",str(r))

            for manifest_n in tqdm(range(len(TDFS_FILES))):

                for from_ in CHANGE_FROM:
                    try:
                        os.remove("2dfs.json")
                        os.remove("Dockerfile")
                        os.mkdir("files")
                    except:
                        pass

                    print("\n ##COOLDOWN## \n")
                    time.sleep(COOLDOWN)

                    print("\n ##EXPERIMENT RUN ",r,"## \n")
                    
                   
                    # Generate 2dfs/Docker manifest and build
                    base_manifest_path = TDFS_FILES[manifest_n]
                    ratio_col = 1/TDFS_COLS[manifest_n]
                    tmp_manifest = gen_2dfs_manifest_from_files(base_manifest_path, "2dfs.json", ratio_col)

                    result = build_tdfs()
                    gen_dockerfile("2dfs.json")
                    result = build_docker()

                    
                    ##perform model update based on change ratio
                    print("Change allotments...")
                    for j in range(int(len(tmp_manifest["allotments"])*ratio)):
                        filename = "files/f"+str(j)
                        try:
                            os.remove(filename)
                        except:
                            pass
                        create_random_file(100, filename)
                        if from_ == 'bottom':
                            tmp_manifest["allotments"][len(tmp_manifest["allotments"])-1-j]["src"] = filename
                            tmp_manifest["allotments"][len(tmp_manifest["allotments"])-1-j]["dst"] = filename
                        if from_ == 'top':
                            tmp_manifest["allotments"][j]["src"] = filename
                            tmp_manifest["allotments"][j]["dst"] = filename
                        filename = "files/f"+str(j)
                        os.remove(filename)
                        create_random_file(20, filename)
                    #overwrite the manifest
                    os.remove("2dfs.json")
                    with open("2dfs.json", "w") as f:
                        json.dump(tmp_manifest, f)

                    ## TDFS EXPERIMENT
                    print("###TDFS EXPERIMENT##")
                    result = build_tdfs()
                    total, download_time, layering_time = parse_tdfs_output(result)
                    print("Total time: ",total, "Download time", download_time, "Layering time", layering_time)
                    csvoutput.append([round(time.time() * 1000),"tdfs",ratio,from_,base_manifest_path,total,download_time,layering_time])
                    cleanup_tdfs()

                    ## DOCKER EXPERIMENT
                    print("###DOCKER EXPERIMENT##")
                    gen_dockerfile("2dfs.json")
                    result = build_docker()
                    total, download_time, layering_time = parse_docker_output(result)
                    print("Total time: ",total, "Download time", download_time, "Layering time", layering_time)
                    csvoutput.append([round(time.time() * 1000),"docker",ratio,from_,base_manifest_path,total,download_time,layering_time])
                    cleanup_docker()


                    ## cleanup files
                    cleanup_dir("./files")

                    ##exporting results to csv
                    csvname = "results_fig14.csv"
                    try:     
                        os.remove(csvname)
                    except:
                        pass
                    with open(csvname, "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(csvoutput)
    
    # PLOT RESULTS
    gen_figure()

    print("✅ Experiment completed")
    print("Results saved to results_fig14.csv")
    print("Figures saved to fig14_a_reproduced.pdf and fig14_b_reproduced.pdf")
