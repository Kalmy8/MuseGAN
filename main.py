from music21 import *

def list_instruments(midi):
    partStream = midi.parts.stream()
    print("List of instruments found on MIDI file:")
    for p in partStream:
        print (p.partName)

piece = converter.parse('autumn5[1].mid')
list_instruments(piece)
