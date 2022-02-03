import numpy as np
import commpy as comm
import commpy.utilities as c_util
import wifireceiver as wr
'''
This function builds an array containing the error values of the output bits we received
    -output_bits: the output_bits we received from the generator polynomial

Explanation: 
    We have n pairs of output of two bits, we have 4 states and 2 possible inputs.
    Therefore we can build a nx4x2 array, where 
        - There are a total of 'n' 4x2 arrays
            - 4 is the number of rows (representing the different states)
                - 2 is the number of cols in the lists (representing the inputs 0,1)
                    (fist number is error when input is 0, second number is error when input is 1)
'''

def build_error_array(output_bits):
    n_output_bits = len(output_bits)
    input_bits = [0,1]
    error_array = np.array([[[-1 for _  in range(2)] for _ in range(4)] for _ in range(n_output_bits)])
    states = [[0,0], [0,1], [1,0], [1,1]]
    bit_width = 2
    number_of_states = len(states)

    for row in range(n_output_bits):
        curr_bits = np.array(output_bits[row]) #ex, curr_bits = [0, 1]

        for col in range(number_of_states):
            state_bits = states[col]
            state_decimal = c_util.bitarray2dec(state_bits)

            for input in input_bits:
                possible_output_bits = c_util.dec2bitarray(wr.trellis_array[input][state_decimal], bit_width)
                error = comm.utilities.hamming_dist(curr_bits, possible_output_bits)
                error_array[row][col][input] = error

    return error_array