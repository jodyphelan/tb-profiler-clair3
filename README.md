# tb-profiler-clair3

This is a tb-profiler plugin that will enable the use of clair3 as a variant caller in tb-profiler (and more broadly, any tool using (pathogen-profiler)[https://github.com/jodyphelan/pathogen-profiler]). 

> [!WARNING]
> This is plugin is still in active development



## Installation and setup

Run the following code from within the conda environment where you have already installed tb-profiler.

```
mamba install bioconda::clair3
pip install git+https://github.com/jodyphelan/tb-profiler-clair3.git
```

You will now have access to `tb-profiler-clair3` which is a tool you can use to view and download available models to use during variant calling.

To view the list run:

```
tb-profiler-clair3 list 
```

To download a model run:

```
tb-profiler-clair3 download --model r1041_e82_400bps_sup_v500
```

Or if you prefer you can download all models with:

```
tb-profiler-clair3 download --all
```

Now you should be ready to use clair3 in tb-profiler. Youll need to specify `--caller clair3` and the appropriate model, e.g. `--clair3_model r1041_e82_400bps_sup_v500`. Here is an example:

```
tb-profiler profile --platform nanopore --caller clair3 -1 reads.fastq.gz --clair3_model r1041_e82_400bps_sup_v500 -t 8 --prefix my_sample
```