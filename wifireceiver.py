from copy import error
from distutils.command.build import build
from email import generator
import numpy as np
import sys
import commpy as comm
import commpy.channelcoding.convcode as check
import time
import viterbi
import turbo_decoding as tb
import build_error_array as berror
from wifitransmitter import print_array
from wifitransmitter import WifiTransmitter
from preamble_detect import find_preamble
from interleave import de_interleave as de_interleave
from interleave import restore_ascii_values as restore_ascii_values
from interleave import convert_ascii_values_to_message as convert_ascii_values_to_message

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

def check_viterbi_works(output, reference_output):
    if (np.array_equal(output, reference_output) != True): 
            print("\nOur viterbi does not match commpy")
            # print("\nreference_output\n", reference_output)
            # print("\noutput we got\n", output)
    else:
        print("Our viterbi got the right solution!")

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
        length = tb.get_length_of_message(output)
        output = output[128:] #since len_binary is length of 128 bits

        '''Remove the final padding since we know the length of the message'''
        message_bits = length*8 #b/c one character is 8 bits
        padded_zeros_to_message = 2*nfft-message_bits%(2*nfft)
        padding_zero_end_index = (message_bits + padded_zeros_to_message)*2 #because right now we have the output bits
        output = output[:padding_zero_end_index]

        '''Get output generator bits'''
        n_output = output.size
        l, r = 0, 1
        generator_bits, n_generator_bits = tb.get_output_generator_bits(output, n_output, generator_bits)
        

        '''Decode the input array'''
        error_array = berror.build_error_array(generator_bits)
        input_bits = viterbi.viterbi_solver(error_array, n_generator_bits)

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
            length = tb.get_length_of_message(output)
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
        message = convert_ascii_values_to_message(ascii_values, message)

    print(begin_zero_padding , "," + message + ",", length)
    
    return begin_zero_padding, message, length

if __name__ == '__main__':
    start_time = time.time()
    WifiReceiver(sys.argv[1], sys.argv[2])