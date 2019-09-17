import pretty_midi
import numpy as np
from math import ceil


lowerBound = 24
upperBound = 102
span = upperBound-lowerBound


def midiToNoteStateMatrix(midifile, squash=True, span=span):
  midi_data = pretty_midi.PrettyMIDI(midifile)
  final = ceil(midi_data.get_end_time() / midi_data.tick_to_time(int(midi_data.resolution / 4)))*midi_data.resolution / 4 - 1
  statematrix = []
  tick = 0

  condition = True
  while condition:
          if tick % (midi_data.resolution / 4) == 0:
              # Crossed a note boundary. Create a new state, defaulting to holding notes
              state = [0 for x in range(span)]
              statematrix.append(state)
          for i in range(len(midi_data.instruments)): #For each track
                  track = midi_data.instruments[i]
                  notes = track.notes 
                  notes = filter(lambda x: x.start <= midi_data.tick_to_time(tick) and x.end > midi_data.tick_to_time(tick) and x.pitch > lowerBound and x.pitch < upperBound, notes)
                  for n in notes:
                      state[n.pitch-lowerBound] = 1

          tick += 1
                  
          if tick > final:
               condition = False
  S = np.array(statematrix)
  statematrix = np.asarray(statematrix).tolist()
  return statematrix


def noteStateMatrixToMidi(statematrix, span=span):
    statematrix = np.array(statematrix)
    tatematrix = np.asarray(statematrix)
    midi_data = pretty_midi.PrettyMIDI()
    track = pretty_midi.Instrument(0)
    midi_data.instruments.append(track)
    
    span = upperBound-lowerBound
    tickscale = 64
    
    prevstate = [0 for x in range(span)]

    onNotes = {}

    for time, state in enumerate(statematrix + [prevstate[:]]): 
        offNotes = {}  
        for i in range(span):
            if i in onNotes and i not in list(state.nonzero()[0]):
                offNotes[i] = (onNotes[i],time*tickscale)
                onNotes.pop(i,None)
        for i in state.nonzero()[0]:
            if i not in onNotes:
                onNotes[i] = time*tickscale

        for note in offNotes:
            track.notes.append(pretty_midi.Note(start=midi_data.tick_to_time(offNotes[note][0]), end=midi_data.tick_to_time(offNotes[note][1]), pitch=note+lowerBound, velocity=120))
    
    sorted(track.notes,key=lambda x: x.start)
    
    return midi_data
  
  
  
def join_midi_list(samples):
  midi_data = samples[0]
  time = 0
  for m in samples[1:]:
      final = midi_data.tick_to_time(int(ceil(midi_data.get_end_time() / midi_data.tick_to_time(int(midi_data.resolution / 4)))*midi_data.resolution / 4)) 
      def alter_time(x):
          x.start += final
          x.end += final
          return x
      new_notes = map(alter_time, m.instruments[0].notes)
      midi_data.instruments[0].notes += list(new_notes)
  return midi_data
