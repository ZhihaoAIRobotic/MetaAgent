## FSGAN

## Requirements
- High-end NVIDIA GPUs with at least 11GB of DRAM.
- Either Linux or Windows. We recommend Linux for better performance.
- CUDA Toolkit 10.1+, CUDNN 7.5+, and the latest NVIDIA driver.

## Installation
```Bash
git clone https://github.com/YuvalNirkin/fsgan
cd fsgan
conda env create -f fsgan_env.yml
conda activate fsgan
pip install .    # Alternatively add the root directory of the repository to PYTHONPATH.
```

For accessing FSGAN's pretrained models and auxiliary data, please fill out
[this form](https://docs.google.com/forms/d/e/1FAIpQLScyyNWoFvyaxxfyaPLnCIAxXgdxLEMwR9Sayjh3JpWseuYlOA/viewform?usp=sf_link).
We will then send you a link to FSGAN's shared directory and download script.
```Bash
python download_fsgan_models.py   # From the repository root directory
```

## Inference
- [Face swapping guide](https://github.com/YuvalNirkin/fsgan/wiki/Face-Swapping-Inference)
- [Face swapping Google Colab](fsgan/inference/face_swapping.ipynb)
- [Paper models guide](https://github.com/YuvalNirkin/fsgan/wiki/Paper-Models-Inference)


