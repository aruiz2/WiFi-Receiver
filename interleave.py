
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
