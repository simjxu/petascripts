import pyshark

capture = pyshark.LiveCapture(interface='eth0')
capture.sniff(timeout=50)

capture

for packet in capture.sniff_continuous(packet_count=5):
	print('Just arrived:', packet)