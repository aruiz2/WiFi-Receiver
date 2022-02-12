import wifitransmitter as wt
import numpy as np
import submit.wifireceiver as wr

s = "789456123�������"

#Level4 test
noise_pad_begin, txsignal, length = wt.WifiTransmitter(s, 4, 6)
print("\nnoise_pad_begin value:", noise_pad_begin)
wr.WifiReceiver(txsignal, 4); print("\n")

#Level3 test
txsignal = wt.WifiTransmitter(s, 3)
wr.WifiReceiver(txsignal, 3)

#Level2 test
txsignal = wt.WifiTransmitter(s, 2)
wr.WifiReceiver(txsignal, 2)

#Level1 test
txsignal = wt.WifiTransmitter(s, 1)
wr.WifiReceiver(txsignal, 1)
'''
30 or less test for snr
'''