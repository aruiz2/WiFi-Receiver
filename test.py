import wifitransmitter as wt
import wifireceiver as wr

#Level4 test
noise_pad_begin, txsignal, length = wt.WifiTransmitter("hello", 4)
print("the noise_pad_begin value is:", noise_pad_begin)
wr.WifiReceiver(txsignal, 4)

#Level3 test
# txsignal = wt.WifiTransmitter("hello world", 3)
# wr.WifiReceiver(txsignal, 3)