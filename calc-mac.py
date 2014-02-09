#!/usr/bin/python
import sys, string, binascii
from Crypto.Cipher import DES

if len(sys.argv) != 3:
  sys.exit("Usage:   ./calc-mac.py <OTA response> <key>\nExample: ./calc-mac.py 02710000131200000000000000010002 0123456789ABCDEF")

response = binascii.unhexlify(sys.argv[1])
key =  binascii.unhexlify(sys.argv[2])

iv = "\x00\x00\x00\x00\x00\x00\x00\x00"

cipher=DES.new(key,DES.MODE_CBC,iv)
ciphertext=cipher.encrypt(response)

mac = ciphertext[-8:]

print "MAC:", binascii.hexlify(mac)
