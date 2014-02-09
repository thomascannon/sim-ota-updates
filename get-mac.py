#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pySim.commands import SimCardCommands
from pySim.utils import swap_nibbles
try:
    import argparse
except Exception, err:
    print "Missing argparse -- try apt-get install python-argparse"

def hex_ber_length(data):
  dataLen = len(data) / 2
  if dataLen < 0x80:
    return '%02x' % dataLen
  dataLen = '%x' % dataLen
  lenDataLen = len(dataLen)
  if lenDataLen % 2:
    dataLen = '0' + dataLen
    lenDataLen = lenDataLen + 1
  return ('%02x' % (0x80 + (lenDataLen / 2))) + dataLen

class MessageCommands(object):
  def __init__(self, transport):
    self._tp = transport
    self._apduCounter = 1;

  def send_read_data(self, length):
    return self._tp.send_apdu_checksw('A0C00000' + ('%02x' % length)) 
  
  def send_terminal_profile(self):
    #return self._tp.send_apdu_checksw('A010000011FFFF000000000000000000000000000000')
    return self._tp.send_apdu_checksw('A010000010FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
#    return self._tp.send_apdu_checksw('A0100000050b61ff7700')

  def send_ota_sms(self, data):
    # Wrap data inside an SMS-PP APDU 

    # Command Header Length (0d)
    # Command Header:
    #   SPI: No RC/CC/DS, No Enc, PoR with CC required (1009)
    #   KiC: Algorithm known, DES in CBC, Key 1 (10)
    #   KiD: Algorithm known, DES in CBC, Key 1 (10)
    #   TAR: Remote App Management (000000)
    #   CNTR: Counter (00000000XX)
    #   PCNTR: Padding Counter (00)
    # Data (data param)
    envelopeData = '0d1009101000000000000000' + ('%02x' % (self._apduCounter & 0xff)) + '00'
    envelopeData += data

    self._apduCounter += 1 

    # User Data Header (027000)
    envelopeData = '027000' + ('%04x' % (len(envelopeData) / 2)) + envelopeData

    # SMS-TDPU header: MS-Delivery, no more messages, TP-UD header, no reply path (40)
    # TP-OA (08) = TON/NPI (81) 8 digits (55667788)
    # TP-PID = SIM Download (7f), TP-DCS (f6), TP-SCTS (00112912000004)
    envelopeData = '400881556677887ff600112912000004' + ('%02x' % (len(envelopeData) / 2)) + envelopeData

    # Device Identities (82), Network (83) to USIM (81)
    # SMS-TPDU (8b)
    envelopeData = '820283818b' + hex_ber_length(envelopeData) + envelopeData
    
    # APDU Data (d1)
    envelopeData = 'd1' + hex_ber_length(envelopeData) + envelopeData

    # APDU command for SMS-PP Download (a0c20000)
    envelopeData = 'a0c20000' + ('%02x' % (len(envelopeData) / 2)) + envelopeData

    # Send complete APDU
    response = self._tp.send_apdu_checksw(envelopeData)

    return response


parser = argparse.ArgumentParser(description='Tries to get a DES MAC from OTA response')
parser.add_argument('-s', '--serialport')
parser.add_argument('-p', '--pcsc', nargs='?', const=0, type=int)

args = parser.parse_args()

if args.pcsc is not None:
  from pySim.transport.pcsc import PcscSimLink
  sl = PcscSimLink(args.pcsc)
elif args.serialport is not None:
  from pySim.transport.serial import SerialSimLink
  sl = SerialSimLink(device=args.serialport, baudrate=9600)
else:
  raise RuntimeError("Need to specify either --serialport or --pcsc")

sc = SimCardCommands(sl)
ac = MessageCommands(sl)

sl.wait_for_card(0)

print "ICCID:        " + swap_nibbles(sc.read_binary(['3f00', '2fe2'])[0])
ac.send_terminal_profile()

# Send OTA SMS-PP Download messages (with incrementing CNTR)
for x in range(0,1):
  # Send following binary data
  # a0a40000023f00 = Select master file 3f00
  (data, status) = ac.send_ota_sms('a0a40000023f00')
  print "Status Code:  " + status
  # If it succeeds a response of length 0x18 is waiting, so read it
  data = ac.send_read_data(0x18)
  print "OTA Response: " + data[0]
