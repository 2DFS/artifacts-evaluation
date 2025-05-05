# 2DFS Artifacts Evaluation

This repository is to be intentended for the sole purpose of evaluating the 2DFS artifacts presented in the ATC 2025 Paper. 

The code is not intended for production use and is not supported. The code is provided "as-is" without any warranty of any kind, either express or implied, including but not limited to the implied warranties of merchantability and fitness for a particular purpose. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of or in connection with the code or the use or other dealings in the code.

# 2DFS Artifacts Evaluation

## Requirements
- Ubuntu 22.04 or newer. This code has been tested on Ubuntu 22.04. 
- Docker installation (please follow [this guide](https://docs.docker.com/engine/install/) )
- Rootless Docker installation. This is required to run the evaluation scripts without `sudo`. To do this, you need to add your user to the `docker` group. You can do this by running the following this [Docker Rootless documentation](https://docs.docker.com/engine/install/linux-postinstall/).
- Python 3.8 or higher installed. You can check your Python version by running:
    ```bash
    python3 --version
    ```
- Install `ifstat`. You can do this by running:
    ```bash
        sudo apt-get install ifstat 
    ```

## Overview

How to evaluate the 2DFS artifacts presented in the ATC 2025 Paper. The evaluation is based on the following steps:

1. **Setup the environment**: Setup the environment of the machine where you want to run the evaluation scripts be following the steps below:
    - (1.1) Install the latest `tdfs`CLI utility: 
        ```bash
        curl -sfL 2dfs.github.io/install-tdfs.sh | sh - 
        ```
    - (1.2) Clone this repository and navigate its root directory:
        ```bash
        git clone https://github.com/2DFS/artifacts-evaluation ATC25-2dfs-artifacts-evaluation && cd ATC25-2dfs-artifacts-evaluation
        ```
    - (1.3) Download and extract the evaluation dataset:
        ```bash
        curl -L https://github.com/2DFS/artifacts-evaluation/releases/download/models/splits.tar.gz -o splits.tar.gz
        tar -xvf splits.tar.gz
        rm -rf splits.tar.gz
        ```
    - (1.4) Install the required Python packages:
        ```bash
        pip3 install -r requirements.txt
        ```


2. **Run the evaluation**: For each of the figures in our paper, we include a script to run its evaluation. The scripts assume that both docker and `tdfs` are installed and the `splits/` folder containing the models and splits is in the same directory as the evaluation scripts, so **make sure you completed the the steps above**. The scripts to be used to reproduce each figure are listed below. 

## Evaluation Scripts 

These artifacts evaluation scripts reproduce all the results presented in the Evaluation section of the paper, specifically from Fig.8 to Fig. 14. 

>N.b. To reduce the time overhead of this evaluation, **by default** each experiment is executed only once. To repeat each experiment multple times, it is possible to export the `EXPERIMENT_REPEAT` environment variable to the number of times you want to repeat each experiment. For example, to repeat each experiment 2 times, run:
>```bash
>export EXPERIMENT_REPEAT=2
>```

### Figure 8

- **Script setup time:** <1 minute
- **Script execution time:** ~10 minutes
    
![image](figs/fig-8.png)

- To run the evaluation for Figure 8, run the following command:
```bash
   python3 fig8.py
```
#### Expected behaviour:
During the experiment, for each experiment configuration, the script will print massages like the following:
```bash
###TDFS EXPERIMENT##
Total time:  5.92 Download time 4.336642265319824 Layering time 0.3461027145385742
###DOCKER EXPERIMENT##
Total time:  12.2 Download time 1.4 Layering time 7.099999999999991
```
Highlighting the Total build time, download time (from Dockerub) and container layering time for each experiment configuration. These results already give the user an idea of the performance of TDFS vs Docker. 

#### Results:
At the end of the execution, the script will save the results in a file called `results_fig8.csv` in the current directory. The script will also generate a plot of the results and save it in a file called `fig8_reproduced.pdf` in the current directory. The plot will be saved in the same format as the one presented in the paper.

### Figure 9

- **Script setup time:** <1 minute
- **Script execution time:** ~15 minutes

![image](figs/fig-9.png)

- To run the evaluation for Figure 9, run the following command:
```bash
   python3 fig9.py
```
#### Expected behaviour:
During the experiment, for each experiment configuration, the script will print massages like the following:
```bash
###TDFS EXPERIMENT##
Total time:  5.92 Download time 4.336642265319824 Layering time 0.3461027145385742
###DOCKER EXPERIMENT##
Total time:  12.2 Download time 1.4 Layering time 7.099999999999991
```
Highlighting the Total build time, download time (from Dockerub) and container layering time for each experiment configuration. These results already give the user an idea of the performance of TDFS vs Docker. 

#### Results:
At the end of the execution, the script will save the results in a file called `results_fig9.csv` in the current directory. The script will also generate a plot of the results and save it in a file called `fig9_reproduced.pdf` in the current directory.

### Figure 10  

- **Script setup time:** <1 minute
- **Script execution time:** ~5 minutes

<img src="figs/fig-10.png" alt="image" width="300"/>

- To run the evaluation for Figure 10, run the following command:
```bash
   python3 fig10.py
```
#### Expected behaviour:
During the experiment, for each experiment configuration, the script will print massages like the following:
```bash
###TDFS EXPERIMENT##
Total time:  5.92 Download time 4.336642265319824 Layering time 0.3461027145385742
###DOCKER EXPERIMENT##
Total time:  12.2 Download time 1.4 Layering time 7.099999999999991
```
Highlighting the Total build time, download time (from Dockerub) and container layering time for each experiment configuration. These results already give the user an idea of the performance of TDFS vs Docker. 

#### Results:
At the end of the execution, the script will save the results in a file called `results_fig10.csv` and `cpumemoryusage.csv` in the current directory. The former contains the build output like for fig 8 and 9, while the latter the CPU an Memory consumptions measurements during the experiments. The script will also generate a plot of the results and save it in a file called `fig10_reproduced.pdf` in the current directory. 

**Disclaimer:** CPU and Memory measurements fluctuate based on real time usage of the machine. Please consider this when interpreting the results. Additionally, due to high fluctuations the standard deviation of the measurements can be high, this effect is mitigated by running the experiment multiple times.

### Figure 11, 12 and 13

- **Script setup time:** ~5 minutes
- **Script execution time:** ~10 minutes


<img src="figs/fig-11.png" alt="image" width="300"/>
<img src="figs/fig-12.png" alt="image" width="300"/>
<img src="figs/fig-13.png" alt="image" width="300"/>

Figures 11, 12 and 13 are generated together as part of the same experiment. 
To run the evaluation for Figure 11, 12 and 13 follow these steps:

- First, authorize the `2DFS+OCI` compliat registry to run locally. This is required to run the evaluation scripts. Edit the `/etc/docker/daemon.json` file and either replace its content with the following lines or simply add the primitive: 
```json
{
    "insecure-registries" : ["0.0.0.0:10500"]
}
```
- Then restart the Docker daemon by running:
```bash
    sudo systemctl restart docker
```
- Now you can run the 2DFS+OCI compliant registry locally using: 
```bash
docker run -d -p 10500:5000 --restart=always --name 2dfs-registry ghcr.io/2dfs/2dfs-registry:edge
```
- Then run the evaluation script:
```bash
    python3 fig11-13.py
```
- After the experiment is finished you can shut down the registry by running:
```bash
    docker stop 2dfs-registry
```

#### Expected behaviour:
The script should run multiple Docker and TDFS builds, each one with a different configuration. At the end of each built it pushes the artifacts to the local registry. Then, it performs different pulls for each image partition. 

#### Results:
At the end of the execution, the script will save the results in files called `results_fig11.csv`, `cpumemoryusage.csv` and `bandwidth-result.log` in the current directory. The first contains the build output results, the second contains the CPU an Memory consumptions measurements during the experiments and the third containts the bandwidth measurements. The script will also generate the plots of the results and save them respectively in the files:  `fig11_reproduced.pdf`,`fig12_reproduced.pdf` and `fig13_reproduced.pdf` in the current directory.

**Disclaimer:** CPU, Memory and bandwidth measurements fluctuate based on real time usage of the machine. In this script the registry is running locally with the builder. So expect additional background noise compared to the paper. Please consider this when interpreting the results. Additionally, due to high fluctuations the standard deviation of the measurements can be high, this effect is mitigated by running the experiment multiple times.
