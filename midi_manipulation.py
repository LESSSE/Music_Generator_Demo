import pretty_midi
import numpy as np


lowerBound = 24
upperBound = 102
span = upperBound-lowerBound


def midiToNoteStateMatrix(midifile, squash=True, span=span):
  midi_data = pretty_midi.PrettyMIDI(midifile)
  
  statematrix = []
  tick = 0

  condition = True

  while condition:
          if tick % (midi_data.resolution / 4) == 0:
              # Crossed a note boundary. Create a new state, defaulting to holding notes
              state = [[0,0] for x in range(span)]
              statematrix.append(state)
          for i in range(len(midi_data.instruments)): #For each track
                  track = midi_data.instruments[i]
                  notes = track.notes 
                  notes = filter(lambda x: x.start <= midi_data.tick_to_time(tick) and x.end >= midi_data.tick_to_time(tick) and x.pitch > lowerBound and x.pitch < upperBound, notes)
                  for n in notes:
                      state[n.pitch-lowerBound] = 1

                  tick += int(midi_data.resolution / 8)

          if midi_data.tick_to_time(tick) > midi_data.get_end_time():
               condition = False
  S = np.array(statematrix)
  statematrix = np.asarray(statematrix).tolist()
  return statematrix


def noteStateMatrixToMidi(statematrix, name="example", span=span):
    statematrix = np.array(statematrix)
    if not len(statematrix.shape) == 3:
        statematrix = np.dstack((statematrix[:, :span], statematrix[:, span:]))
    statematrix = np.asarray(statematrix)
    pattern = midi.Pattern()
    track = midi.Track()
    pattern.append(track)
    
    span = upperBound-lowerBound
    tickscale = 55
    
    lastcmdtime = 0
    prevstate = [[0,0] for x in range(span)]
    for time, state in enumerate(statematrix + [prevstate[:]]):  
        offNotes = []
        onNotes = []
        for i in range(span):
            n = state[i]
            p = prevstate[i]
            if p[0] == 1:
                if n[0] == 0:
                    offNotes.append(i)
                elif n[1] == 1:
                    offNotes.append(i)
                    onNotes.append(i)
            elif n[0] == 1:
                onNotes.append(i)
        for note in offNotes:
            track.append(midi.NoteOffEvent(tick=(time-lastcmdtime)*tickscale, pitch=note+lowerBound))
            lastcmdtime = time
        for note in onNotes:
            track.append(midi.NoteOnEvent(tick=(time-lastcmdtime)*tickscale, velocity=40, pitch=note+lowerBound))
            lastcmdtime = time
            
        prevstate = state
    
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)

    midi.write_midifile("{}.mid".format(name), pattern)
