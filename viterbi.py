import numpy as np

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
            input_tracker[0][c][prev_c] = 0
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
This function deletes the prev_state path depending on which has a greater error, or none if equal
    -inputs_dict: the dictionary containing the prev_states with its path errors
    -min_error: the error threshold value
'''
def delete_max_error_input(inputs_dict, min_error):
    for prev_state, error in inputs_dict.items():
        if (error > min_error):
            del inputs_dict[prev_state]       
    return

'''
This function will traceback through our input tracker and calculate all possible paths.
It will create a dictionary matching each path with its error value.
    -input_tracker: our data structure containing the inputs that lead to less error
'''
def build_path(input_tracker, s, r, path_error, path_bits, paths):
    if (r < 1): 
        paths[path_error] = np.flip(np.array(path_bits))
        return
    
    input_dict = input_tracker[r][s]
    
    for prev_state, path_error in input_dict.items():
        #1. Recover the input bit
        curr_error = input_tracker[r][s][prev_state]
        if (r == 2): print(prev_state)
        bit = find_input_bit_based_on_state(prev_state)
        path_bits.append(bit)
        build_path(input_tracker, prev_state, r-1, path_error + curr_error, path_bits.copy(), paths)

        #2. Update for next bit
        path_bits.pop()
    
'''
This function performs the Viterbi algorithm with the help of helper functions
    -error_array: array that contains the weight of each path
    -n_generator_bits: how many bits we have
'''
def viterbi_solver(error_array, n_generator_bits):

    rows = n_generator_bits
    cols = 4 #number of states
    bits = [0,1]

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

                curr_error = error_array[r-1][c][prev_c]
                cumulative_error = prev_error + curr_error

                if cumulative_error < min_error_input:
                    min_error_input = cumulative_error
                    min_error_prev_state_list = [prev_c]
                
                elif cumulative_error == min_error_input:
                    min_error_prev_state_list.append(prev_c)
            
            for min_error_prev_state in min_error_prev_state_list:
                input_tracker[r][c][min_error_prev_state] = int(min_error_input)
            
            #Check if input 0 or 1 leads to less error and delete input with max total error
            delete_max_error_input(input_tracker[r][c], min_error_input)
    
    print(input_tracker)
    #2. Traceback to get all possible paths with its output error
    curr_state, states, paths = 0, [0, 1, 2, 3], {}
    print("\noutput for build path begins now\n")
    for state in states:
        input_bits, path_error, curr_row = [], 0, rows
        build_path(input_tracker, curr_state, curr_row, path_error, input_bits, paths)

    print(paths)
    #3. Return the path with the minimum error
    min_error = min(list(paths.keys()))
    min_path = paths[min_error]
    return min_path