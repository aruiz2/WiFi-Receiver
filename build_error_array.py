import numpy as np
import commpy as comm

'''
This function builds an array containing the error values of the output bits we received
    -output_bits: the output_bits we received from the generator polynomial
'''
def build_error_array(output_bits):
    n_output_bits = len(output_bits)
    input_bits = [0,1]
    error_array = np.array([[[-1 for _  in range(2)] for _ in range(4)] for _ in range(n_output_bits)])
    states = [[0,0], [0,1], [1,0], [1,1]]
    number_of_states = 4
    #print("output_bits:\n" , output_bits, "\n")
    for row in range(n_output_bits):
        curr_bits = output_bits[row] #ex, curr_bits = [0, 1]
        for col in range(number_of_states):
            state = states[col]
            for input in input_bits:
                error = comm.utilities.hamming_dist(np.array(curr_bits), np.array(state))
                error_array[row][col][input] = error
    
    return error_array