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
    "splits/efficientnet_v2B1_seperated/field.json",
    "splits/efficientnet_v2L_seperated/field.json",
    "splits/resnet50_seperated/field.json",
    "splits/deeplab_v3_seperated/field.json",
    "splits/mobilenet_v2_14_seperated/field.json",
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

def gen_figure():

    df_xtended = pd.read_csv("results_fig9.csv")
    df_xtended['layer'] = df_xtended['layering']
    df_xtended['tot-nowd'] = df_xtended['tot']-df_xtended['download']
    df_xtended['ratio'] = df_xtended['ratio']*100
    df_xtended['ratio'] = df_xtended['ratio'].astype(int)
    df_xtended['model'] = df_xtended['file'].apply(map_name)
    df_xtended['hue'] = df_xtended['tool'] + "-" + df_xtended['model'].astype(str) 

    colors = sns.color_palette(cc.glasbey_light, n_colors=15)

    filter_array = ["RN50","MNv2L","DLv3","ENv2B1","YOLOv3","ENv2L"]
    df_filtered = df_xtended[df_xtended["model"].isin(filter_array)]
        
    ax = sns.catplot(
        data=df_filtered, x="ratio", y="tot-nowd", hue="tool", col="model",
        capsize=.2, palette=colors, errorbar="sd",
        kind="point", height=3, markers=["s", "x"], sharex=True,sharey=False, col_wrap=6,aspect=1.2,estimator=np.median,
        col_order=filter_array
    )

    i=0
    for item, a in ax.axes_dict.items():
        a.grid(False, axis='x')
        a.set_title(filter_array[i])
        i+=1

    ax.legend.remove()
    custom_lines = [Line2D([0], [0], color=colors[0], linewidth=2, linestyle='-', marker='s'),
                    Line2D([0], [0], color=colors[1], linewidth=2, linestyle='-', marker='x')]
    plt.legend(custom_lines,["2DFS","Docker"], ncol = 2, loc = "lower left", frameon = False, bbox_to_anchor=(-6.8, 1.2), fontsize="small")


    ax.set_ylabels("Time (s)")

    for i,a in  enumerate(ax.axes.flatten()):
        if i==0:
            a.set_xlabel("Model Split Capacity (\%)")
        else:
            a.set_xlabel("")
        ymin, ymax = a.get_ylim()
        step = int(int(ymax/4)/10)*10
        if step==0:
            step = 10
        new_ymax = int(ymax/step)*step
        a.set_yticks(range(0,int(ymax)+step,step),labels=range(0,int(ymax)+step,step),fontfamily='sans-serif')
        a.set_ylim(ymax=new_ymax+10)
        
        ax.savefig('fig9_reproduced.pdf', bbox_inches='tight')     


if __name__ == "__main__":
    csvoutput = [
        ["timestamp","tool","ratio","file","tot","download","layering"]
    ]
    cleanup_tdfs()
    cleanup_docker()
    
    for ratio in tqdm(EXPERIMENT_ALLOTMENT_RATIO):

        #print("\n ##EXPERIMENT CONFIG ## \n",str(ratio))

        for r in tqdm(range(REPEAT)):

            #print("\n ##REPEAT ## \n",str(r))

            for manifest_n in tqdm(range(len(TDFS_FILES))):

                print("\n ##FILE ## \n",str(TDFS_FILES[manifest_n]))

                try:
                    os.remove("2dfs.json")
                    os.remove("Dockerfile")
                except:
                    pass

                print("\n ##COOLDOWN## \n")
                time.sleep(COOLDOWN)

                print("\n ##EXPERIMENT RUN ",r,"## \n")
                
                ## TDFS EXPERIMENT
                # Generate 2dfs manifest
                print("###TDFS EXPERIMENT##")
                base_manifest_path = TDFS_FILES[manifest_n]
                ratio_col = ratio
                if ratio > 0:
                    ratio_col = 1/TDFS_COLS[manifest_n]
                tmp_manifest = gen_2dfs_manifest_from_files(base_manifest_path, "2dfs.json", ratio_col)

                result = build_tdfs()
                total, download_time, layering_time = parse_tdfs_output(result)
                print("Total time: ",total, "Download time", download_time, "Layering time", layering_time)
                csvoutput.append([round(time.time() * 1000),"tdfs",ratio,base_manifest_path,total,download_time,layering_time])
                cleanup_tdfs()

                ## DOCKER EXPERIMENT
                print("###DOCKER EXPERIMENT##")
                times = len(tmp_manifest["allotments"])*ratio
                batchsize = int(len(tmp_manifest["allotments"]) / times)
                total, download_time, layering_time = 0,0,0
                for m in range(0,int(times)):
                    #print("###DOCKER EXPERIMENT - Build Image ",m,"/",times," Splits batchsize: ",batchsize,"##")
                    gen_dockerfile_partitioned("2dfs.json",1,startfrom=m*batchsize,batchsize=batchsize)
                    result = build_docker()
                    batch_total, batch_download_time, batch_layering_time = parse_docker_output(result)
                    total += batch_total
                    download_time += batch_download_time
                    layering_time += batch_layering_time
                    os.remove("Dockerfile")
                print("Total time: ",total, "Download time", download_time, "Layering time", layering_time)
                csvoutput.append([round(time.time() * 1000),"docker",ratio,base_manifest_path,total,download_time,layering_time])
                cleanup_docker()


                ## cleanup files
                cleanup_dir("./files")

                ##exporting results to csv
                csvname = "results_fig9.csv"
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
    print("Results saved to results_fig9.csv")
    print("Figure saved to fig9_reproduced.pdf")
