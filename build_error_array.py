import numpy as np
import commpy as comm
import commpy.utilities as c_util
import wifireceiver as wr
from viterbi import find_prev_state_trellis
'''
This function builds an array containing the error values of the output bits we received
    -output_bits: the output_bits we received from the generator polynomial

Explanation: 
    We have n pairs of output of two bits, we have 4 states and 4 possible prev_states.
    Therefore we can build a nx4x4 array, where 
        - There are a total of 'n' 4x4 arrays
            - 4 rows is the number of rows (representing the different states)
                - 4 cols is the number of possible prev_states in the lists. 
                   We will assign an error of inf to non valid previous states.
'''

def build_error_array(output_bits):
    states = [[0,0], [0,1], [1,0], [1,1]]
    bit_width = 2
    number_of_states = len(states)
    n_output_bits = len(output_bits)
    input_bits = [0,1]
    
    error_array = np.array([[[float("inf") for _  in range(number_of_states)] for _ in range(number_of_states)] for _ in range(n_output_bits)])

    for row in range(n_output_bits):
        curr_bits = np.array(output_bits[row]) #ex, curr_bits = [0, 1]

        for col in range(number_of_states):
            state_bits = states[col]
            state_decimal = c_util.bitarray2dec(state_bits)

            for prev_state in find_prev_state_trellis(state_decimal):
                possible_output_bits = c_util.dec2bitarray(wr.trellis_array[state_decimal][prev_state], bit_width)
                error = comm.utilities.hamming_dist(curr_bits, possible_output_bits)
                error_array[row][col][prev_state] = error 
    print(error_array)
    return error_array