import wifitransmitter as wt
import wifireceiver as wr

noise_pad_begin, txsignal, length = wt.WifiTransmitter("h", 4)
print("the noise_pad_begin value is:", noise_pad_begin)
wr.WifiReceiver(txsignal, 4)