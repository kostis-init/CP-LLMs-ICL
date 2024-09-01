
# Constraint Modelling with LLMs using In-Context Learning

## Overview

This repository contains the code for the paper "Constraint Modelling with LLMs using In-Context Learning". The paper explores the potential of using pre-trained Large Language Models (LLMs) to transform textual combinatorial problem descriptions into concrete and executable Constraint Programming (CP) specifications through retrieval-augmented in-context learning. For more details, please refer to the [paper](#citation).

## Structure

The repository is structured as follows:

- `llms4cp/`: Contains the code for the pipeline presented in the paper.
- `data/`: Contains the datasets used (for more details check [there](data/README.md)).
- `results/`: Contains results from the experiments.

## Getting Started

### Prerequisites

- Python 3.9

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
    - Only one key is required, depending on the LLM used. For example, for OpenAI's models fill only `OPENAI_API_KEY`.
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

    @InProceedings{michailidis_et_al:LIPIcs.CP.2024.20,
      author =	{Michailidis, Kostis and Tsouros, Dimos and Guns, Tias},
      title =	{{Constraint Modelling with LLMs Using In-Context Learning}},
      booktitle =	{30th International Conference on Principles and Practice of Constraint Programming (CP 2024)},
      pages =	{20:1--20:27},
      series =	{Leibniz International Proceedings in Informatics (LIPIcs)},
      ISBN =	{978-3-95977-336-2},
      ISSN =	{1868-8969},
      year =	{2024},
      volume =	{307},
      editor =	{Shaw, Paul},
      publisher =	{Schloss Dagstuhl -- Leibniz-Zentrum f{\"u}r Informatik},
      address =	{Dagstuhl, Germany},
      URL =		{https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2024.20},
      URN =		{urn:nbn:de:0030-drops-207053},
      doi =		{10.4230/LIPIcs.CP.2024.20},
      annote =	{Keywords: Constraint Modelling, Constraint Acquisition, Constraint Programming, Large Language Models, In-Context Learning, Natural Language Processing, Named Entity Recognition, Retrieval-Augmented Generation, Optimisation}
    }
