# Maintaining Knowledge Beyond Rules: A Provenance-Aware Reference Architecture for Knowledge Engineering (Supplementary Material)

## Shortened Journal Abstract

__Problem.__ Knowledge bases often become difficult to understand, validate, and maintain because the context, rationale, assumptions, and provenance behind knowledge acquisition and formalization are lost over time, particularly when contributors or expertise change.

__Proposed solution.__ The paper introduces a provenance-aware reference architecture for maintainable knowledge engineering that combines Web Annotations, PROV-O, and Semantic Web technologies. The architecture preserves the complete lifecycle of knowledge by explicitly capturing claims, evidence, revisions, interpretations, assessments, competency questions, and contributor information as traceable artifacts, linking source material to executable knowledge representations.

__Demonstration examples.__ The architecture is illustrated through five domain-oriented use cases. These examples demonstrate how provenance, alternative interpretations, revision histories, and supporting evidence can be preserved while maintaining traceability between knowledge sources and formalized rules.

**Status**: Journal article in review

## Repository Overview

This repository contains five interactive domain examples which are briefly described in the following:
* __Socrates__ is the running and minimal example illustrating each segment of the reference architecture starting with the well-known example _"All men are mortal"_. It demonstrates how knowledge bases with a different formalism can be linked and interrelated to the source data. The example uses the First-Order Logic and [ProbLog language](https://dtai.cs.kuleuven.be/problog/) to formally represent rules. 

* __Healthcare__ takes the CHILD network as basis to generate a Problog knowledge base. The example illustrates how provenance information is used to filter and partition knowledge based on the social network of domain experts. The example uses the [ProbLog language](https://dtai.cs.kuleuven.be/problog/) to formally represent rules.

* __Cultural Heritage__ describes the prevailing problem of diverging interpretations from the same source in the cultural heritage domain. The example illustrates how the reference architecture keeps track of interpretation sequences for preventing a claim's original meaning from mutating. The example uses [Notation3 and the EYE reasoner](https://eyereasoner.github.io/eye/) to process rules.

* __Legal__ is based on a public dataset which contains AI generated and evaluated GDPR scenarios with the goal of providing training material to legal students. The example demonstrates how the architecture naturally supports the retrieval of knowledge bases based on weighting mechanisms throughout the segments. The example uses [PYTHEN](https://arxiv.org/abs/2603.15317) to formally represent rules.
  
* __Manufacturing__ describes the provision of decision-support for tuning parameters of a PID controller. The example illustrates how the architecture can be used to implement (semi-)automatic conflict resolvement mechanisms to support knowledge engineers in compiling a knowledge base. The example uses the [FO(·) language](https://idp-z3.be/) to formally represent rules.
  
  
Each of the examples contains a Jupyter notebook which the reader can follow step-by-step from elicited domain data to an interactive knowledge-based system:

1. _claimGenerationNetwork.xlsx_ contains the elicited data from the social network of domain experts. _claimFormalizationNetwork.xlsx_ contains the elicited data from the social network of knowledge engineers. The files are intended for readers who are familiar with spreadsheet software to easily understand (and modify if desired) the data and its structure. In the first step, the spreadsheet contained data is just exported to the _csv folder_. Those who prefer to edit csv files directly, this step can be skipped completely.
   
2. Using _\[example\].yarrrml.yml_, we generate _\[example\]\_rules.rml.ttl_ to map and translate the csv data to an RDF graph. Within the notebook, the resulting RDF graph can be explored using [yFiles Graphs for Jupyter](https://www.yworks.com/products/yfiles-graphs-for-jupyter). For advanced exploration, please export the RDF graph and use RDF-tailored software. Edits to the yarrrml specification are only necessary if the reader decides to modify the csv data structure (out of personal interest). In that case, we recommend that readers test their specification with [Matey](https://rml.io/yarrrml/matey/) to validate its behavior.
   
3. Rules are retrieved from the resulting RDF graph and used to generate a knowledge-based system. The reader can directly interact with the system within the notebook using ipywidgets. Some examples are provided to explain the capabilities of each system.

Please refer to the journal article for a thorough description of the examples.

## Installation (Windows)
We provide explicit installation guidance for Windows users because in our experience Linux users are already familiar with the installation steps or are capable of inferring them.

1. Clone the GitHub repository using a tool like PowerShell:
```shell
git clone [nameOfThisRepository]
cd [nameOfThisRepository]
```

2. Create a virtual environment in the project folder and install required packages:

```shell
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
```

3. Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), open the terminal in Docker Desktop, and pull the official [YARRRML parser image](https://hub.docker.com/r/rmlio/yarrrml-parser) from Docker Hub. Make sure that you have a running container of YARRRML parser before working with one of the examples.

_Remark_: There are [other ways to run YARRRML parser](https://rml.io/yarrrml/tutorial/getting-started/), but using a Docker container is the cleanest and easiest way. 

```shell
docker pull rmlio/yarrrml-parser
```

4. The project set-up is completed and you are ready to start any of the examples. We recommend using JupyterLab to work with the examples:
```shell
jupyter-lab
```

Your computer should open the JupyterLab interface in your default browser. If not, typically the application is accessed via http://localhost:8888/lab. In case, you miss the access token or the port is incorrect, please read through the terminal output to find the necessary information.

We recommend starting with _socrates.ipynb_.

## Troubleshooting
In case you encounter unforeseen complications or elements are unclear, please create an issue in the Issue tab on GitHub. The most common issues are listed below:
* (Windows Only) The docker service is only available on Windows when docker desktop is opened.

## License
MIT
