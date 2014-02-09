OTA SIM Update
===============

The idea of this script is to request a response from a SIM card signed with a DES key. Once in possession of the MAC you can go about cracking the key used to generate it and then be able to sign and load your own apps onto the SIM.

In reality DES hasn't been used in most SIMs in *years*. I was only able to elicit the appropriate response from one SIM from the Philippines, and that couldn't be cracked.

However, researcher Karsten Nohl has had [real success](https://srlabs.de/rooting-sim-cards/) with certain SIM cards and has presented great research on the topic.

This was a quick hack, using various sources, doesn't include documentation and I expect won't do anything for you. It might be useful in related work however, so take it for what it is.
