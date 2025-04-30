# 2DFS Artifacts Evaluation

This repository is to be intentended for the sole purpose of evaluating the 2DFS artifacts presented in the ATC 2025 Paper. 

The code is not intended for production use and is not supported. The code is provided "as-is" without any warranty of any kind, either express or implied, including but not limited to the implied warranties of merchantability and fitness for a particular purpose. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of or in connection with the code or the use or other dealings in the code.

# 2DFS Artifacts Evaluation

## Requirements
- Any Linux/Darwin machine. This code has been tested on Ubuntu 22.04. 
- Docker (please follow [this guide](https://docs.docker.com/engine/install/) )
- Python 3.8 or higher installed. You can check your Python version by running:
    ```bash
    python3 --version
    ```

## Overview

How to evaluate the 2DFS artifacts presented in the ATC 2025 Paper. The evaluation is based on the following steps:

1. **Setup the environment**: The evaluation is based on the following steps:
    - Install the latest `tdfs`CLI utility: 
        ```bash
        curl -sfL 2dfs.github.io/install-tdfs.sh | sh - 
        ```
    - Clone this repository and navigate its root directory:
        ```bash
        git clone https://github.com/2DFS/artifacts-evaluation ATC25-2dfs-artifacts-evaluation && cd ATC25-2dfs-artifacts-evaluation
        ```
    - Download and extract the evaluation dataset:
        ```bash
        curl -L https://github.com/2DFS/artifacts-evaluation/releases/download/models/splits.zip -o splits.tar.gz
        tar -xvf splits.tar.gz
        rm -rf splits.tar.gz
        ```
    - Install the required Python packages:
        ```bash
        pip3 install -r requirements.txt
        ```


2. **Run the evaluation**: We include a script to run the evaluation for each of the figures in our paper. The scripts assume that both docker and `tdfs` are installed and the `splits/` folder containing the models and splits is in the same directory as the evaluation scripts, so **make sure you completed the the steps above**. The scripts to be used to reproduce each figure are listed below. 


## Evaluation Scripts 

These artifacts evaluation scripts reproduces all the results presented in the Evaluation section of the paper, specifically from Fig.8 to Fig. 14. 

>N.b. To reduce the time overhead of this evaluation, **by default** each experiment is executed only once. To repeat each experiment multple times, it is possible to export the `EXPERIMENT_REPEAT` environment variable to the number of times you want to repeat each experiment. For example, to repeat each experiment 2 times, run:
>```bash
>export EXPERIMENT_REPEAT=2
>```

### Figure 8
    
![image](figs/fig-8.png)

- To run the evaluation for Figure 9, run the following command:
```bash
    python3 evaluate_fig9.py
```

### Figure 9

![image](figs/fig-9.png)

- To run the evaluation for Figure 9, run the following command:
    ```bash
    python3 evaluate_fig9.py
  ```

### Figure 10  

<img src="figs/fig-10.png" alt="image" width="300"/>

- To run the evaluation for Figure 10, run the following command:
    ```bash
    python3 evaluate_fig10.py
    ```

### Figure 11

<img src="figs/fig-11.png" alt="image" width="300"/>

- To run the evaluation for Figure 11, run the following command:
    ```bash
    python3 evaluate_fig11.py
    ```

### Figure 12

<img src="figs/fig-12.png" alt="image" width="300"/>

- To run the evaluation for Figure 12, run the following command:
    ```bash
    python3 evaluate_fig12.py
    ```

### Figure 13

<img src="figs/fig-13.png" alt="image" width="300"/>

- To run the evaluation for Figure 13, run the following command:
    ```bash
    python3 evaluate_fig13.py
    ```

### Figure 14

<img src="figs/fig-14-1.png" alt="image" width="300"/>
<img src="figs/fig-14-2.png" alt="image" width="300"/>

- To run the evaluation for Figure 14, run the following command:
```bash
python3 evaluate_fig14.py
```