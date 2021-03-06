# Moments-DNNs

Code for the paper “Characterizing Well-behaved vs. Pathological Deep Neural Networks” published in 36th International Conference on Machine Learning (ICML 2019): https://arxiv.org/abs/1811.03087

## Setup
This package has been tested with python 2.7, python 3.5 and python 3.7. 

For installing all necessary python dependencies:
```sh
cd moments-dnns
sudo pip install -r requirements.txt   # optionally: sudo pip3 install -r requirements.txt
```

## Description

The package is built on top of TensorFlow Keras. At the core of the package, four types of custom layers perform the simultaneous propagation of signal and noise:
* Convolutional layers
* Batch normalization layers
* Activation layers
* Addition layers to merge residual and skip-connection branches for resnets

Custom layers are also introduced for the computation of the moments of signal and noise. Performing these computations inside the model rather than outside is much more effective both in terms of speed and memory usage.

The entry-point of the package is `run_experiments.py`. This file contains the function `run_experiment()` which runs an experiment with fixed parameters for a given number of realizations. The results of the experiment are saved as numpy arrays in the folder `npy/name_experiment/` with the parameter `name_experiment` set at the invocation of `run_experiment()`.

For an experiment with 1,000 realizations, `.npy` files typically occupy a space of a few MB. This space can be optionally reduced by calling the function `prune_experiment()` in the file `manage_experiments.py`. This function enables to only retain the moments relevant for a specific type of plot.


The file `plots.py` provides function to plot the results of the experiments in situations equivalent to Fig. 2, 3, 4, 5 of the paper.


## Notebooks

Notebooks provide a easy way of familiarizing with the package. The main notebook [Reproducing Fig. 2, 3, 4, 5.ipynb](https://github.com/alabatie/moments-dnns/blob/master/Reproducing%20Fig.%202%2C%203%2C%204%2C%205.ipynb) shows the function calls to reproduce the results from Fig. 2, 3, 4, 5 from the paper.

There are two complementary notebooks 

- [Complements on width, boundary conditions, dataset, epsilon.ipynb](https://github.com/alabatie/moments-dnns/blob/master/Complements%20on%20width%2C%20boundary%20conditions%2C%20dataset%2C%20epsilon.ipynb) discusses the effect of changing the width, boundary conditions of convolutional layers, input dataset and batch normalization fuzz factor

- [Complements on fully-connected networks.ipynb](https://github.com/alabatie/moments-dnns/blob/master/Complements%20on%20fully-connected%20networks.ipynb) discusses experiments equivalent to Fig. 2, 3, 4, 5 for fully-connected networks

These complementary notebooks confirm the results of the paper and provide additional insights and examples of usage of the function `run_experiment()`.

