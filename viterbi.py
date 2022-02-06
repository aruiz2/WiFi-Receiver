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
    if (r < 1): 
        path_bits = np.flip(np.array(path_bits))
        store_path["input_bits"] = path_bits
        return
    
    input_dict = input_tracker[r][s] #{prev_state: error}
    
    for prev_state, path_error in input_dict.items():
        bit = find_input_bit_based_on_state(s)
        path_bits.append(bit)
        build_path(input_tracker, prev_state, r-1, path_bits, store_path )
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
                if (r == 13 and c == 1 and prev_c == 2): print(prev_error, curr_error)
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