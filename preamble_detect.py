from operator import index
import numpy as np
import commpy as comm

preamble = np.array([1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1,1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1])
mod = comm.modulation.QAMModem(4)
preamble_complex = np.fft.ifft(mod.modulate(preamble.astype(bool)))
n_preamble_complex = preamble_complex.size
 

def find_preamble(output, n_output):
    max_correlation, max_correlation_index = np.NINF, -1
    for i in range(n_output - n_preamble_complex):
        curr_correlation_coeff_arr = np.correlate(output[i:i+n_preamble_complex], preamble_complex)
        curr_correlation_coeff_arr_magnitude = np.abs(curr_correlation_coeff_arr)[0]
        if curr_correlation_coeff_arr_magnitude > max_correlation:
            max_correlation = curr_correlation_coeff_arr_magnitude
            max_correlation_index = i

    return max_correlation_index
'''
This function returns the index with the highest probability of matching the preamble.
    -output: our bits
    -n_output: how many bits there are in 'output'
'''
def find_preamble_other(output, n_output):
    index_preamble = 0
    best_match = -1
    current_match = -1

    for i in range(n_output - n_preamble_complex):
        current_match = calculate_preamble_match(output, i)
        if current_match > best_match:
            if current_match == n_preamble_complex: return i, n_preamble_complex
            best_match= current_match
            index_preamble = i
    return index_preamble, n_preamble_complex
 
'''
This function calculates the percentage of how many bits match the preamble bits in a subarray of our bits
    -output: our bits
    -i: the starting index of the subarray
'''
def calculate_preamble_match(output, i):
    i_preamble = 0
    matched = 0

    for i_output in range(i, i + n_preamble_complex):
        if output[i_output] == preamble_complex[i_preamble]: matched += 1
        i_preamble += 1

    return matched