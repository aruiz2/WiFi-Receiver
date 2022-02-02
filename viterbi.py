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
This function returns a list of dictionaries containing new paths with their previous error
    -prev_sequence: array containing strings of previous paths
    -bit: the bit to add to each sequence in prev_sequences
'''
def build_new_path(prev_sequence, bit):
    n_prev_sequence = len(prev_sequence)
    new_paths_list = []

    #print("prev_sequence:", prev_sequence)
    for i in range(n_prev_sequence):
        path_dict = prev_sequence[i]
        new_path_dict = {}
        for path_string in path_dict.keys():
            #print("path_string:"+ path_string)
            new_path_dict[path_string + str(bit)] = path_dict[path_string]
            new_paths_list.append(new_path_dict)
    
    #print("new_paths_list: ", new_paths_list)
    #print("\n")
    return new_paths_list

'''
This function returns a list with a dict of previous paths and errors
    -paths_tracker: our data structure where we store all the paths
    -r: current time we are at
    -c: current state we are at
'''
def get_prev_sequence(paths_tracker, r, c, input):
    '''c_prev0 is the state prior to current backtracking with input of 0'''

    #Get the paths
    c_prev0 = find_prev_state_trellis(c, input)
    c_prev1 = find_prev_state_trellis(c, input)
    prev_path0 = paths_tracker[r-1][c_prev0]
    prev_path1 = paths_tracker[r-1][c_prev1] #= [{'PATH1': error}, {'PATH1': error}]
    
    paths = []
    min_error = float("infinity")
    
    #add all the paths with their error to our list 'paths'
    for prev_path in [prev_path0, prev_path1]:
        for path, error in prev_path.items():
            path_dict = {path: error}
            min_error = min(min_error, error)
            paths.append(path_dict)
    
    #delete the paths with error > min_path
    n_paths = len(paths)
    for i in range(n_paths):
        path_dict = paths[i]
        for path, error in path_dict.items():
            if error > min_error:
                paths.pop(i)
        
    return paths

'''
This function deletes any paths being stored that have a total error greater than the min_error
    -paths_dict: the dictionary containing the paths with its erros
    -min_error: the error threshold value
'''
def delete_paths(paths_dict, min_error):
    for path in list(paths_dict.keys()):
        error = paths_dict[path]
        if (error > min_error):
            del paths_dict[path]
        
    return
'''

This function performs the Viterbi algorithm with the help of helper functions
    -error_array: array that contains the weight of each path
'''
def viterbi_solver(error_array):
    
    rows = len(error_array)
    cols = 4 #number of states
    bits = [0,1]
    paths_tracker = np.array([[{} for _ in range(cols)] for _ in range(rows + 1)]) #need extra row for base cases
    for c in range(cols): paths_tracker[0][c][""] = 0
    
    #r loops through time
    for r in range(1, rows+1):
        #c loops through states
        for c in range(cols):
            #print(r, c)
            min_error_path = float("inf")

            for bit in bits:
                prev_sequence = get_prev_sequence(paths_tracker, r, c, bit)
                curr_error = error_array[r-1][c][bit]
                new_paths = build_new_path(prev_sequence, bit)
                #print("new_paths: ", new_paths, "\n\n")

                #Add the new paths to our tracker with their new error value
                for path_dict in new_paths:
                    for path, error in path_dict.items():
                        new_error = curr_error + error
                        paths_tracker[r][c][path] = new_error
                        min_error_path = min(min_error_path, new_error)

            #Delete any path that has bigger errors than min_error path
            delete_paths(paths_tracker[r][c], min_error_path)
    print("paths_tracker_last_row: \n", paths_tracker[r][c])

    '''
    Still need to implement the part to calculate min distance
    '''
    