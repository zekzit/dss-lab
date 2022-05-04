#[CAL-01] การคำนวณค่า Normalized Weight ของวิธีการที่เลือกใช้
import numpy as np


def calculate_weight_rating(weight):
    summation = np.sum(weight)
    percentage_fn = __percentage_fn(summation)
    normalized_weight = list(map(percentage_fn, weight))
    return normalized_weight


# https://towardsdatascience.com/deep-dive-into-analytical-hierarchy-process-using-python-140385fabaa1
def calculate_weight_ahp(matrix):
    n = len(matrix)
    eig_val = np.linalg.eig(matrix)[0].max()
    eig_vec = np.linalg.eig(matrix)[1][:, 0]
    p = eig_vec / eig_vec.sum()
    ci = (eig_val - n) / (n - 1)
    ri = [0, 0, 0.52, 0.89, 1.12, 1.26, 1.36, 1.41, 1.46, 1.49, 1.52, 1.54, 1.56, 1.58, 1.59]
    cr = ci / ri[n - 1]
    if cr > 0.1:
        raise ValueError("CR > 0.10; So this matrix is invalid.")
    return p.real


# -- Helper functions
def __percentage_fn(summation):
    return lambda w: w / summation
