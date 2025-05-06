import os
from random import getrandbits
import subprocess
import json
from datetime import datetime
import csv
import time


def create_random_file(file_size_mb, filename):
    """
    Creates a file of specified size (in MB) filled with random bytes.

    Args:
        file_size_mb: The desired size of the file in megabytes.
        filename: The name of the file to create.
    """
    file_size_bytes = file_size_mb * 1024 * 1024

    with open(filename, "wb") as f:
        while file_size_bytes > 0:
            # Generate random bytes (chunk size of 1 MB)
            random_bytes = getrandbits(8 * 1024 * 1024)  # 1 MB
            # Write the random bytes to the file
            f.write(random_bytes.to_bytes(1024 * 1024, byteorder='big'))
            # Update remaining bytes
            file_size_bytes -= 1024 * 1024

def allotment_map_elem_to_list(dst_list,map_selector):
    def labda_closure(data):
        x = data[map_selector]
        if isinstance(x, list):
            dst_list.extend(x)
        else:
            dst_list.append(x)
    return labda_closure

def gen_2dfs_manifest_from_files(src_manifest, dst_manifest, allotment_ratio):
    new_manifest = {
        "allotments":[]
    }
    with open(src_manifest) as f:
        manifest = json.load(f)
        tot_allotments = 1
        if allotment_ratio > 0:
            tot_allotments = int(len(manifest["allotments"]) * allotment_ratio)
        skip_pace = int(len(manifest["allotments"]) / tot_allotments)
        row=0
        for i in range(0, len(manifest["allotments"]), skip_pace):
            src_file_list = []
            dst_file_list = []
            batchSize = int(i + (skip_pace))
            list(map(allotment_map_elem_to_list(src_file_list,"src"),manifest["allotments"][i:batchSize]))
            list(map(allotment_map_elem_to_list(dst_file_list,"dst"),manifest["allotments"][i:batchSize]))
            new_manifest["allotments"].append({
                "src": src_file_list,
                "dst": dst_file_list,
                "row": row,
                "col": 0
            })
            row+=1
    with open(dst_manifest, "w") as f:
        json.dump(new_manifest, f)
    return new_manifest

def gen_2dfs_manifest_configs(src_manifest):
    new_manifest = {
        "allotments":[]
    }
    with open(src_manifest) as f:
        manifest = json.load(f)
        tot_allotments = 1
        if allotment_ratio > 0:
            tot_allotments = int(len(manifest["allotments"]) * allotment_ratio)
        skip_pace = int(len(manifest["allotments"]) / tot_allotments)
        row=0
        for i in range(0, len(manifest["allotments"]), skip_pace):
            src_file_list = []
            dst_file_list = []
            batchSize = int(i + (skip_pace))
            list(map(allotment_map_elem_to_list(src_file_list,"src"),manifest["allotments"][i:batchSize]))
            list(map(allotment_map_elem_to_list(dst_file_list,"dst"),manifest["allotments"][i:batchSize]))
            new_manifest["allotments"].append({
                "src": src_file_list,
                "dst": dst_file_list,
                "row": row,
                "col": 0
            })
            row+=1


def create_split_allotments_configs(manifest_dir,allotment_ratio,tmp_dir):
    tot_allotments = 1
    with open(manifest_dir) as f:
        manifest = json.load(f)
        tot_allotments = int(len(manifest["allotments"]))

        configs = []
        for i in range(0, len(manifest["allotments"])):
            for j in range(0, len(manifest["allotments"]), step=i):
                new_manifest = {
                    "allotments":[]
                }
                configs.append([i,j])

        skip_pace = int(len(manifest["allotments"])/tot_allotments)
        for i in range(0,len(manifest["allotments"]),skip_pace):
            file_list.append(glue_files(manifest["allotments"][i:i+(skip_pace-1)]["src"],tmp_dir+"/f"+str(i)))


def gen_2dfs_manifest(files_list):
    manifest = {
        "allotments":[]
    }
    i = 0
    for f in files_list:
        manifest["allotments"].append({
            "src":f,
            "dst":"/file"+str(i),
            "row":i,
            "col":i
        })
        i += 1

    #delete 2dfs.json file if it exists
    if os.path.exists("2dfs.json"):
        os.remove("2dfs.json")

    #write manifest to 2dfs.json file
    with open("2dfs.json", "w") as f:
        json.dump(manifest, f)

def gen_dockerfile(manifest_path):
    with open(manifest_path) as f:
        manifest = json.load(f)

    dockerfile = "FROM 0.0.0.0:10500/2dfs/ubuntu:22.04\n"
    i = 0

    for allotment in manifest["allotments"]:
        files_list = allotment["src"]
        if isinstance(allotment["src"],list):
            files_list = ""
            for f in allotment["src"]:
                files_list += " " + f
        dockerfile += "COPY "+files_list+" / \n"
        i += 1

    #delete Dockerfile if it exists
    if os.path.exists("Dockerfile"):
        os.remove("Dockerfile")

    #write Dockerfile file
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)

def gen_dockerfile_partitioned(manifest_path,ratio,startfrom=0,batchsize=0):
    with open(manifest_path) as f:
        manifest = json.load(f)

    dockerfile = "FROM 0.0.0.0:10500/2dfs/ubuntu:22.04\n"
    i = 0

    tot_allotments = int(len(manifest["allotments"])*ratio)
    to = len(manifest["allotments"])
    if batchsize > 0:
        to = startfrom+batchsize

    for allotment in manifest["allotments"][startfrom:to]:
        if tot_allotments < 0:
            break
        files_list = allotment["src"]
        if isinstance(allotment["src"],list):
            files_list = ""
            for f in allotment["src"]:
                files_list += " " + f
        dockerfile += "COPY "+files_list+" / \n"
        i += 1
        tot_allotments -= 1

    #delete Dockerfile if it exists
    if os.path.exists("Dockerfile"):
        os.remove("Dockerfile")

    #write Dockerfile file
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)

def cleanup_dir(dir):
    try:
        for file in os.listdir(dir):
            os.remove(os.path.join(dir, file))
    except:
        pass

def build_tdfs(tag=""):
    cmd = ["time","tdfs", "build", "0.0.0.0:10500/2dfs/ubuntu:22.04","0.0.0.0:10500/test/testtdfs:v1"+tag,"--platforms", "linux/amd64","--force-http"]
    return exec_command(cmd)

def export_tdfs(partition,expname):
   cmd = ["time","tdfs", "image", "export","0.0.0.0:10500/test/testtdfs:v1"+str(partition),"--platform", "linux/amd64","files/"+expname+".tar.gz"]
   return exec_command(cmd)

def push_tdfs(partition):
   cmd = ["tdfs", "image", "push","0.0.0.0:10500/test/testtdfs:v1"+str(partition),"--force-http",]
   return exec_command(cmd)

def build_docker(tag=""):
    cmd = ["time","docker", "build", "-t","0.0.0.0:10500/test/test:v1"+tag,"."]
    return exec_command(cmd)

def export_docker(expname):
    cmd = ["time","docker","save","-o","files/"+expname+".tar.gz","0.0.0.0:10500/test/test:v1"]
    return exec_command(cmd)

def push_docker(tag=""):
    cmd = ["docker","push","0.0.0.0:10500/test/test:v1"+tag]
    return exec_command(cmd)

def pull_docker(partition,tdfs=False):
    name = "test"
    if tdfs:
        name = "testtdfs"
    cmd = ["time","docker","pull","0.0.0.0:10500/test/"+name+":v1"+str(partition)]
    return exec_command(cmd)

def exec_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True)
        #decode to utf8
        output = (result.stdout + result.stderr).decode("utf-8")
        return output
    except subprocess.CalledProcessError as error:
        print(f"Error executing command: {error}")
    return ""

def execute_with_live_output(cmd):
    """
    Executes a command and prints its output line by line as it becomes available.

    Args:
        cmd: The command to execute as a list of arguments.
    """
    # Open a pipe for stdout
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

    # Iterate over the output lines
    for line in iter(process.stdout.readline, ""):
        print(line, end="")  # Print without newline

    # Wait for the process to finish and close the pipe
    process.stdout.close()
    process.wait()

def cleanup_tdfs():
    cmd = ["tdfs", "image", "rm","-a"]
    exec_command(cmd)

def cleanup_docker():
    cmd = ["docker", "system", "prune","-a","-f"]
    exec_command(cmd)
    cmd = ["docker", "image", "prune","-a","-f"]
    exec_command(cmd)

def parse_tdfs_export(output):
    total = 0
    begin_time = 0
    partitioning = 0
    for line in output.split("\n"):
        linearr = line.split(" ")
        for i,token in enumerate(linearr):
            # extract total time
            if "elapsed" in token:
                #remove elapsed from token
                token = token.replace("elapsed","")
                total = parse_time_output(token)
            # extract experiment begin time
            if "Retrieving" in token:
                begin_time = parse_time_to_millis(linearr[i-1])
            if "Exporting" in token:
                partitioning = parse_time_to_millis(linearr[i-1])-begin_time

    return total, partitioning

def parse_tdfs_output(output):
    total = 0
    begin_time = 0
    download_time = 0
    layering_time = 0
    for line in output.split("\n"):
        linearr = line.split(" ")
        for i,token in enumerate(linearr):
            # extract total time
            if "elapsed" in token:
                #remove elapsed from token
                token = token.replace("elapsed","")
                total = parse_time_output(token)
            # extract experiment begin time
            if "Parsing" in token:
                begin_time = parse_time_to_millis(linearr[1])
            # extract download finished time
            if "retrieved" in token:
                download_time = parse_time_to_millis(linearr[1])-begin_time
            # extract copy time time
            if "[COPY]" in token:
                layering_time = (parse_time_to_millis(linearr[1])-begin_time)-download_time
    return total, download_time, layering_time

def parse_docker_output(output):
    total = 0
    begin_time = 0
    download_time = 0
    layering_time = 0
    tempsum = 0.0 
    for line in output.split("\n"):
        linearr = line.split(" ")
        if "#5" in line:
            download_time += tempsum
            tempsum = 0.0
        if "exporting to image" in line:
            layering_time += tempsum
            tempsum = 0.0
            continue
        for i,token in enumerate(linearr):
            # extract total time
            if "elapsed" in token:
                #remove elapsed from token
                token = token.replace("elapsed","")
                total = parse_time_output(token)
            # extract experiment begin time
            if "DONE" in token:
                tempsum+=float(linearr[i+1].replace("s",""))
    return total, download_time, layering_time

def parse_time_to_millis(time_str):
  try:
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
  except ValueError:
    raise ValueError(f"Invalid time format: {time_str}")

  return time_obj.timestamp()

def parse_time_output(time_str):
    timeplit = time_str.split(":")
    minutes = int(timeplit[0])
    seconds = float(timeplit[1])
    return float(minutes*60)+seconds

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