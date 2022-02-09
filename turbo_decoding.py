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