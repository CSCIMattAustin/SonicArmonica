# Matthew Austin, Lucian Freeze, Brett Whitson
# sonicpisynth.rb
# A live_loop-based, sliding pitch generator for
#   different sustained tones in Sonic Pi.
  
# initialize pitch variable
t = ""

# initialize tone type
orig = [""]
live_loop :listen do
  
  # get pitches and synth tones over UDP
  pitch = sync "/osc/play_this"
  SYNTH = sync "/osc/synth"
  
  # change tone based on input
  if (SYNTH == ["sine"])
    use_synth :sine
  end
  if (SYNTH == ["tb303"])
    use_synth :tb303
  end
  if (SYNTH == ["mod_saw"])
    use_synth :mod_saw
  end
  if (SYNTH == ["zawa"])
    use_synth :zawa
  end
  if (SYNTH == ["square"])
    use_synth :square
  end
  if (SYNTH == ["blade"])
    use_synth :blade
  end
  
  if SYNTH != orig
    # mute previous tone's signal
    control t, amp: 0, release: 1, note_slide: 0
    
    # clear pitch variable
    t = ""
    
    # play new sustained, slideable pitch (starting at 20)
    t = play 20, sustain: 1000, note_slide: 0.1
    
    # set new tone to orig to check for next change
    orig = SYNTH
  end
  
  # change the note of the current playing sound
  control t, note: pitch[0]
end