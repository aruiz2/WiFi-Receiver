import numpy as np
'''
Finds the previous state of the current state when given some input
    -state: the current state
    -input: the input given
'''
def find_prev_state_trellis(state, input):
    if state == 0:
        if input == 0: return 0
        return 1

    elif state == 1:
        if input == 0: return 3
        return 2

    elif state == 2:
        if input == 0: return 2
        return 3

    elif state == 3:
        if input == 0: return 1
        return 0

'''
This function deletes the input 0 or 1 depending on which has a max total error path
    -inputs_dict: the dictionary containing the inputs with its path errors
    -min_error: the error threshold value
'''
def delete_max_error_input(inputs_dict, min_error):
    for input in list(inputs_dict.keys()):
        error = inputs_dict[input]
        if (error > min_error):
            del inputs_dict[input]       
    return

'''
This function will traceback through our input tracker and calculate all possible paths.
It will create a dictionary matching each path with its error value.
    -input_tracker: our data structure containing the inputs that lead to less error
'''
def build_path(input_tracker, s, r, path_error, path_bits, paths):
    #TODO: CHECK WE DONT GET EQUAL ERRORED PATHS
    if (r < 1): 
        paths[path_error] = path_bits
        return
    
    input_dict = input_tracker[r][s]
    
    for bit, path_error in input_dict.items():
        #1. Recover the input bit
        curr_error = input_tracker[r][s][bit]
        path_bits.append(bit)
        print(r, path_bits)
        build_path(input_tracker, s, r-1, path_error + curr_error, path_bits.copy(), paths)

        #2. Update for next bit
        path_bits.pop()

    print("\n")
    
'''
This function performs the Viterbi algorithm with the help of helper functions
    -error_array: array that contains the weight of each path
    -n_generator_bits: how many bits we have
'''
def viterbi_solver(error_array, n_generator_bits):

    rows = n_generator_bits
    cols = 4 #number of states
    bits = [0,1]
    input_tracker = np.array([[{} for _ in range(cols)] for _ in range(rows + 1)]) #need extra row for base cases
    for c in range(cols): input_tracker[0][c][""] = 0

    #1. Calculate min paths to each state at the last time
    #r loops through time
    for r in range(1, rows+1):

        #c loops through states
        for c in range(cols):
            min_error_input = float("inf")
            new_paths = []

            for bit in bits:
                prev_r, prev_c = r-1, find_prev_state_trellis(c, bit)  #prev_time, prev_state
                prev_error = list(input_tracker[prev_r][prev_c].values())[0]

                curr_error = error_array[r-1][prev_c][bit]
                cumulative_error = prev_error + curr_error

                input_tracker[r][c][bit] = cumulative_error
                min_error_input = min(min_error_input, cumulative_error)

            #Check if input 0 or 1 leads to less error and delete input with max total error
            if (r == 1): print(input_tracker[1])
            delete_max_error_input(input_tracker[r][c], min_error_input)

    #2. Traceback to get all possible paths with its output error
    #print(input_tracker)
    curr_state, states, paths = 0, [0, 1, 2, 3], {}
    for state in states:
        input_bits, path_error, curr_row = [], 0, rows
        build_path(input_tracker, curr_state, curr_row, path_error, input_bits, paths)
    
    #3. Return the path with the minimum error
    print(paths)
    min_error = min(list(paths.keys()))
    return np.array(paths[min_error])