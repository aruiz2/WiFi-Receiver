from copy import error
from distutils.command.build import build
from email import generator
import numpy as np
import sys
import commpy as comm
import commpy.channelcoding.convcode as check
import time
import commpy.utilities as c_util
from operator import index

''''
The trellis arrray is made of 4 rows and 4 cols.
    - The rows indicate the current state 
    - The cols refer to the previous states.
    - The elements of the array represent the output given current state and prev_state input
'''
na = -1         
trellis_array = np.array([ [[0], [na], [3], [na]],
                            [[3], [na], [0], [na]],
                            [[na], [2], [na], [1]],
                            [[na], [1], [na], [2]]])

preamble = np.array([1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1,1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1])
mod_preamble = comm.modulation.QAMModem(4)
preamble_complex = np.fft.ifft(mod_preamble.modulate(preamble.astype(bool)))
n_preamble_complex = preamble_complex.size
 

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
                possible_output_bits = c_util.dec2bitarray(trellis_array[state_decimal][prev_state], bit_width)
                error = comm.utilities.hamming_dist(curr_bits, possible_output_bits)
                error_array[row][col][prev_state] = error 
    return error_array

'''
This function undoes the interleaving in an array output and stores it in input
    -rows: integer representing number of rows
    -cols: inegers representing number of cols
    -Interleave_arr: the Interleave array we used to perform interleaving
    -input: the resulting array from doing the interleaving
    -output: the array where we will store our answer
    -row_length: number of elements per row
'''
def de_interleave(rows, cols, Interleave_arr, input, output, row_length):
    for r in range(rows):
        for c in range(cols):
            row_index = Interleave_arr[c]
            output[r*row_length + row_index] = input[r*row_length + c]
    return output

'''
This function loops through an array of bits and 
returns back an array containing the representation of ascii values
    -n_bits: the number of bits we have
    -bits_per_num: how many bits our ascii characters contain
    -bits: our input array of bits
    -ascii_values: the array we will store the ascii_values
'''
def restore_ascii_values(n_bits, bits_per_num, bits, ascii_values):
    for start in range(0, n_bits, bits_per_num):
        num = 0
        for i in range(bits_per_num):

            bit = bits[start + i]
            if (bit == 1):
                exp =  (bits_per_num - 1) - (i % bits_per_num)
                num += int(2**(exp))

        ascii_values[start//bits_per_num] = num
    return ascii_values

'''
Converts a bunch of ascii values in a list to its ascii character representation
    -ascii_values: the input array of ascii_values
    -message: the message returned
'''
def convert_ascii_values_to_message(ascii_values, message):
    for num in ascii_values:
        message += chr(num)
        
    return message


def check_viterbi_works(output, reference_output):
    if (np.array_equal(output, reference_output) != True): 
            print("\nOur viterbi does not match commpy")
            # print("\nreference_output\n", reference_output)
            # print("\noutput we got\n", output)
    else:
        print("Our viterbi got the right solution!")

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

'''
This function gets the output generator bits from the array 'output'.
It returns them in an array of arrays where each array contains a pair of two output bits.
    -output: our output bits
    -n_output: length of output
    -generator_bits: our empty array that we will append all the pairs of bits to
'''
def get_output_generator_bits(output, n_output, generator_bits):
    l, r = 0, 1
    n_generator_bits = 0
    while r < n_output:
        i = output[l]
        generator_bits.append([output[l], output[r]])
        l += 2
        r += 2
        n_generator_bits += 1
    
    return generator_bits, n_generator_bits

'''
This function gets the length of the message in an output array (representing a message)
    -output: our output bits
'''
def get_length_of_message(output):
    length = 0
    start_length_bit = 113
    n_row = start_length_bit + 15 #because upper bound is not inclusive
    for i in range(start_length_bit, n_row):
        bit = output[i]
        if bit == 1:
            binary_index = n_row - (i + 1)
            length += 2**(binary_index)
    return length

'''
This function initializes our input_tracker which is where we keep track of the least errror input in each state per time
    -rows: time taken
    -cols: the number of states (in this case it should be 4)
'''
def initialize_input_tracker(rows, cols):
    input_tracker = np.array([[{} for _ in range(cols)] for _ in range(rows + 1)])
    for c in range(cols): 
        prev_c_list = find_prev_state_trellis(c)
        for prev_c in prev_c_list:
            if c == 0: input_tracker[0][c][prev_c] = 0
            else: input_tracker[0][c][prev_c] = float("inf")
    return input_tracker

'''
Finds the previous state of the current state when given some input
    -state: the current state
    -input: the input given
'''
def find_prev_state_trellis(state):
    if state == 0: return [0,2]

    elif state == 1: return [0, 2]

    elif state == 2: return [1, 3]

    elif state == 3: return [1, 3]
    return []
'''
Finds the next possible states of the current state
    -state: the current state
'''
def find_next_state_trellis(state):
    if state == 0: return [0, 1]
    elif state == 1: return [2, 3]
    elif state == 2: return [0, 1]
    elif state == 3: return [2, 3]
    return []

'''
Finds the input bit based on the state we are at
    -state: the state we are at
'''
def find_input_bit_based_on_state(state):
    if state == 0 or state == 2: return 0
    else: return 1

'''
This function will traceback through our input tracker and calculate all possible paths.
It will create a dictionary matching each path with its error value.
    -input_tracker: our data structure containing the inputs that lead to less error
'''
def build_path(input_tracker, s, r, path_bits, store_path):
    stack = [[input_tracker, s, r, path_bits, store_path]] 
    while stack:
        input_tracker , s, r, path_bits, store_path = stack.pop()
        if (r < 1):
            path_bits = np.flip(np.array(path_bits))
            store_path["input_bits"] = path_bits
            return
        
        input_dict = input_tracker[r][s]
        for prev_state, path_error in input_dict.items():
            bit = find_input_bit_based_on_state(s)
            path_bits.append(bit)
            stack.append([input_tracker, prev_state, r-1, path_bits, store_path])
'''
This function gets the minimum error from all the possible paths
    -paths: list containing dictionaries where it tells us the prev state matched to the path error
    -states: an array containing the possible states
'''
def get_state_with_min_path(paths, states):
    #get min_error
    min_error = float("infinity")
    for state in states:
        min_error = min(min_error, list(paths[state].values())[0])

    n_states = len(states)
    state = -1

    #find state with min_error
    for state_dict in paths:
        state += 1
        for prev_state, error in state_dict.items():
            if error == min_error:
                return state
    return -1
'''
This function performs the Viterbi algorithm with the help of helper functions
    -error_array: array that contains the weight of each path
    -n_generator_bits: how many bits we have
'''
def viterbi_solver(error_array, n_generator_bits):

    rows = n_generator_bits
    cols = 4 #number of states
    bits = [0,1]
    states = [0, 1, 2, 3]

    #Initialize input_tracker
    input_tracker = initialize_input_tracker(rows, cols)
    #1. Calculate min paths to each state at the last time
    #r loops through time
    for r in range(1, rows+1):

        #c loops through states
        for c in range(cols):
            min_error_input, min_error_prev_state_list = float("inf"), []
            new_paths = []
            prev_r, prev_c_list = r-1, find_prev_state_trellis(c)  #prev_time, prev_state
            #loop through previous states
            for prev_c in prev_c_list:
                prev_error = list(input_tracker[prev_r][prev_c].values())[0]
                curr_error = int(error_array[r-1][c][prev_c])
                cumulative_error = prev_error + curr_error

                if cumulative_error <= min_error_input:
                    min_error_input = cumulative_error
                    min_error_prev_state_list = [prev_c]
            
            for min_error_prev_state in min_error_prev_state_list:
                input_tracker[r][c][min_error_prev_state] = int(min_error_input) if min_error_input != float("inf") else min_error_input

    #Get min_error_path value
    state_with_min_path = get_state_with_min_path(input_tracker[rows], states)
    store_path = {}
    input_bits = build_path(input_tracker, state_with_min_path, rows, [], store_path)
    return store_path["input_bits"]

def WifiReceiver(*args):
    output = args[0]
    level = int(args[1])
    length = 0
    message = ""
    begin_zero_padding = 0      
    nfft = 64
    cc1 = check.Trellis(np.array([3]),np.array([[0o7,0o5]]))
    preamble = np.array([1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1,1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1])
    n_preamble = preamble.size

    #Preamble Detection
    if level >= 4:
        n_output = len(output)
        i_preamble = find_preamble(output, n_output)
        begin_zero_padding = i_preamble

        '''Remove initial zero padding'''
        output = output[i_preamble:]

    #OFDM Demod
    if level >= 3:
        nsym = int(output.size/nfft)
        for i in range(nsym):
            symbol = output[i*nfft:(i+1)*nfft]
            output[i*nfft:(i+1)*nfft] = np.fft.fft(symbol)

    #Turbo Decoding
    if level >= 2:
    
        '''Convert complex to bits'''
        mod = comm.modulation.QAMModem(4)
        output = mod.demodulate(output, "hard")
        generator_bits, n_generator_bits = [], 0

        '''Remove the preamble'''
        output = output[n_preamble:]

        'Get length of message and remove len_binary array'
        length = get_length_of_message(output)
        output = output[128:] #since len_binary is length of 128 bits

        '''Remove the final padding since we know the length of the message'''
        message_bits = length*8 #b/c one character is 8 bits
        padded_zeros_to_message = 2*nfft-message_bits%(2*nfft)
        padding_zero_end_index = (message_bits + padded_zeros_to_message)*2 #because right now we have the output bits
        output = output[:padding_zero_end_index]

        '''Get output generator bits'''
        n_output = output.size
        l, r = 0, 1
        generator_bits, n_generator_bits = get_output_generator_bits(output, n_output, generator_bits)
        

        '''Decode the input array'''
        error_array = build_error_array(generator_bits)
        input_bits = viterbi_solver(error_array, n_generator_bits)

    #De-interleaving
    if level >= 1:
        '''
        Intially the bits are going to be padding of0s.
        len_binary :128 bits
            first last 14 bits of len_binary represent the length of the message, because the message cannot be greater than 1000 bytes
            bits: [113, 127]
        '''
        Interleave = np.reshape(np.transpose(np.reshape(np.arange(1, 2*nfft+1, 1),[-1,4])),[-1,])
        
        #Get length if entered level is 1
        if level == 1:
            length = get_length_of_message(output)
            input_bits = output
            input_bits = input_bits[128:] #since len_binary is length of 128 bits
        
        n = input_bits.size
        bits = np.zeros(n) #input bits = length array - length of len_binary

        '1. get the message'
        encoded_message = input_bits
        n_encoded = encoded_message.size 
        n_interleave = Interleave.size
        nsym = int(len(bits)/(2*nfft))
        row_length = 2*nfft
        #undo the interleaving
        bits = de_interleave(nsym, n_interleave, Interleave - 1, input_bits, bits, row_length)

        '2. decode the message'
        n_bits = len(bits)
        bits_per_num = 8
        ascii_values = np.zeros((n_bits//bits_per_num,), dtype = int)
        ascii_values = restore_ascii_values(n_bits, bits_per_num, bits, ascii_values)
        message = convert_ascii_values_to_message(ascii_values, message)[:length]

        '3. remove the \x00 characters from our string'

    print(begin_zero_padding , "," + message + ",", length)
    
    return begin_zero_padding, message, length

if __name__ == '__main__':
    start_time = time.time()
    WifiReceiver(sys.argv[1], sys.argv[2])