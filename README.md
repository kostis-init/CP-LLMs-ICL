
# Constraint Modelling with LLMs using In-Context Learning

## Overview

This repository contains the code for the paper "Constraint Modelling with LLMs using In-Context Learning". The paper explores the potential of using pre-trained Large Language Models (LLMs) to transform textual combinatorial problem descriptions into concrete and executable Constraint Programming (CP) specifications through retrieval-augmented in-context learning. For more details, please refer to the [paper](#citation).

## Getting Started

### Prerequisites

- Python 3.9 or higher.

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/kostis-init/LLM-CP-Modeling.git
    ```
2. Navigate to the cloned directory and install dependencies (preferably in a virtual environment):
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

Open the [configuration file](llms4cp/in_context_config.py) and set the following:

- **API keys** for LLM platforms (e.g., `OPENAI_API_KEY`).
- **MODEL**: Which LLM to use for generating the CP models (e.g., `gpt-3.5-turbo`).
- **NUM_EXAMPLES**: Number of examples to add to the context (e.g., `4`).
- **EXAMPLES_SELECTOR**: Method for selecting examples (e.g., `static`).

### Usage

Run the program with the following command, specifying the dataset and method:
```sh
python main.py --dataset <dataset> --method <method>
```

For example, to run the program with the `APLAI` dataset and the `CPMPY` method, use the following command:
```sh
python main.py --dataset APLAI --method CPMPY
```

## Citation

If our research is helpful for your work, please consider citing our paper as follows:

    @inproceedings{todo}