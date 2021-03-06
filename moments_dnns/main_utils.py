from tensorflow.keras.datasets import cifar10, mnist
import tensorflow.keras.backend as K

import numpy as np


def make_asserts(architecture, kernel_size, total_depth, num_computations,
                 num_channels, boundary, dataset, batch_size):
    """ make_asserts
    Assert that experiment constants are valid

    # Conditions
        - kernel_size, num_channels, total_depth, batch_size must be integers
        - architecture must be 'vanilla' or 'bn_ff' or 'bn_res'
        - dataset must be 'cifar10' or 'mnist'
        - boundary must be  'periodic' or 'symmetric' or 'zero_padding'
        - 'symmetric' boundary only compatible with odd kernel size
        - total depth must be a multiple of the number of moment computations
        - data format must be 'channels_last'
        - Keras backend must be 'tensorflow' or 'theano'
    """
    assert (type(kernel_size) is int) and (type(num_channels) is int) and \
        (type(total_depth) is int) and (type(batch_size) is int), \
        "kernel_size, num_channels, total_depth, batch_size must be integers"

    assert (architecture in ['vanilla', 'bn_ff', 'bn_res']), \
        "architecture must be 'vanilla' or 'bn_ff' or 'bn_res'"

    assert (dataset in ['cifar10', 'mnist']), \
        "dataset must be 'cifar10' or 'mnist'"

    assert (boundary in ['periodic', 'symmetric', 'zero_padding']), \
        "boundary must be 'periodic' or 'symmetric' or 'zero_padding'"

    assert not ((boundary == 'symmetric') and (kernel_size % 2 == 0)), \
        "'symmetric' boundary only compatible with odd kernel size"

    assert (total_depth % num_computations == 0), \
        "total depth must be a multiple of the number of moment computations"

    assert (K.image_data_format() == 'channels_last'), \
        "data format must be 'channels_last'"

    assert (K.backend() == 'tensorflow') or (K.backend() == 'theano'), \
        "keras backend must be 'tensorflow' or 'theano'"


def get_submodel_constants(original_size, original_strides, total_depth,
                           num_computations):
    """ get_submodel_constants
      Compute constants for submodel

      # Arguments
        original_size (int): spatial extent of original images
        original_strides (int): strides of first downsampling conv layer
        total_depth (int): total depth of the experiment
        num_computations (int): total number of moment computations

      # Returns
        spatial_size (int): spatial size of images in submodel
        num_submodels (int): number of submodels subdividing the total depth
            - each time the same Keras model is reused as submodel
            - each time it is randomly reinitialized
            - this leads to exactly the same behaviour as a randomly
                initialized model of depth equal to total_depth
            - but it requires less memory
        sub_depth (int): submodel depth
        delta_moments (int): interval between computation of moments
    """
    # num_submodels = 10 if 10 divides both num_computations and total_depth,
    # otherwise num_submodels = num_computations
    num_submodels = 10 if ((num_computations % 10 == 0) and (
        total_depth % 10 == 0)) else num_computations

    spatial_size = original_size // original_strides
    sub_depth = total_depth // num_submodels
    delta_moments = total_depth // num_computations

    return spatial_size, num_submodels, sub_depth, delta_moments


def get_name_moments(architecture, compute_reff_signal, compute_reff_noise):
    """ make_name_moments
      Create lists of raw moments to be computed
      Create list of locs, depending on the architecture
        - vanilla: ['loc1', 'loc2', 'loc3']
        - bn_ff:   ['loc1', 'loc2', 'loc3', 'loc4']
        - bn_res:  ['loc1', 'loc2', 'loc3', 'loc4', 'loc5']

      # Arguments
        architecture (str): 'vanilla' or 'bn_ff' or 'bn_res'
        compute_reff_signal (bool): whether reff is computed for signal
        compute_reff_noise (bool): whether reff is computed for noise

      # Returns
        name_moments_raw (list): names of raw (i.e. without locs) moments
        locs (list): locs
        num_moments_raw (int): number of raw moments
        num_moments (int): total number of moments
            (equals number of raw moments * number of locs)
    """
    name_moments_raw = ['nu1_abs_signal', 'nu2_signal', 'mu2_signal',
                        'mu4_signal', 'mu2_noise']
    if compute_reff_signal:
        name_moments_raw += ['reff_signal']
    if compute_reff_noise:
        name_moments_raw += ['reff_noise']
    num_moments_raw = len(name_moments_raw)

    # locs
    num_locs = 3 if (architecture == 'vanilla') else (
        4 if (architecture == 'bn_ff') else 5)
    locs = ['loc' + str(iloc) for iloc in range(1, num_locs + 1)]
    num_moments = num_locs * num_moments_raw

    return name_moments_raw, locs, (num_moments_raw, num_moments)


def load_dataset(dataset, kernel_size):
    """ load_dataset
    cifar images are 32 x 32 x 3
    mnist images are 28 x 28, and thus must be reshaped to 28 x 28 x 1
    When kernel_size = 1, images are flattened to have spatial size n = 1
        (fully-connected case)

     # Arguments
        dataset (str): 'cifar1O' or 'mnist'
        kernel_size (int): used to treat the fully-connected case

     # Returns
        signal_original (numpy array): suitably reshaped original images
        original_strides (int): strides of first downsampling conv layer
            (= 2 except in the fully-connected case)
        original_num (int): number of original images
        original_spatial (int): spatial size of original images
        original_channels (int): number of channels in original images
    """
    if dataset == 'cifar10':
        (signal_original, _), (_, _) = cifar10.load_data()
    elif dataset == 'mnist':
        (signal_original, _), (_, _) = mnist.load_data()
        signal_original = np.expand_dims(signal_original, -1)
    else:
        raise NotImplementedError()

    # number of original images
    original_num = signal_original.shape[0]

    # if kernel_size = 1, fully-connected case -> we flatten inputs
    if kernel_size == 1:
        signal_original = signal_original.reshape((original_num, 1, 1, -1))

    original_spatial = signal_original.shape[1]  # original spatial extent
    original_channels = signal_original.shape[-1]  # original num channels
    original_strides = 2 if (kernel_size > 1) else 1  # strides of first conv
    return signal_original, (original_strides,
                             original_num,
                             original_spatial,
                             original_channels)
