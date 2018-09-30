# Matthew Austin, Lucian Freeze, Brett Whitson
# sonictheremin.py
# A program utilizing GPIO-connected ultrasonic sensors to
#   capture and send pitch values and adjust volume levels,
#   along with capturing a keypress for tone change.

from subprocess import call # for volume control
from pynput import keyboard # for keypresses
import threading as T
from time import * # for sleep
from pythonosc import osc_message_builder # messages to Sonic Pi
from pythonosc import udp_client # communication to Sonic Pi
import RPi.GPIO as GPIO

# initialize GPIO
GPIO.setmode(GPIO.BOARD)

# globals
tones = ['sine', 'zawa', 'square', 'blade', 'tb303', 'mod_saw']
tone = 'sine' # initialize tone type to sine
i = 0 # to cycle through tones

# GPIO Pins
PITCH_TRIGGER = 15
PITCH_ECHO = 13
VOL_TRIGGER = 7
VOL_ECHO = 11

# capture key press
def on_press(key):
      try:
            print(key.char)
            
      except AttributeError:
            print(key)

# capture key release
def changetone(key):
      global i
      global tones
      global tone
      if key == keyboard.Key.up:
            i += 1
            tone = tones[i%len(tones)]
            return False

GPIO.setup(PITCH_TRIGGER, GPIO.OUT)
GPIO.setup(PITCH_ECHO, GPIO.IN)

# calculate distance for pitch using sensor data
def dist():     
      GPIO.output(PITCH_TRIGGER, GPIO.LOW)
      GPIO.output(PITCH_TRIGGER, GPIO.HIGH)
      sleep(0.000001)
      
      GPIO.output(PITCH_TRIGGER, GPIO.LOW)
      pulse_start_time = time()
      pulse_end_time = time()
      t = time()
      
      while GPIO.input(PITCH_ECHO)==0 and int(time()) -int(t) < .5:
            pulse_start_time = time()
      while GPIO.input(PITCH_ECHO)==1:
            pulse_end_time = time()

      pulse_duration = pulse_end_time - pulse_start_time
      distance = round(pulse_duration * 17150, 2) # scaling
      return distance + 40 # offset

GPIO.setup(VOL_TRIGGER, GPIO.OUT)
GPIO.setup(VOL_ECHO, GPIO.IN)

# calculate distance for volume using sensor data
def volDist():     
      GPIO.output(VOL_TRIGGER, GPIO.LOW)
      GPIO.output(VOL_TRIGGER, GPIO.HIGH)
      sleep(0.000001)
      
      GPIO.output(VOL_TRIGGER, GPIO.LOW)
      pulse_start_time = time()
      pulse_end_time = time()
      t = time()
      
      while GPIO.input(VOL_ECHO)==0 and int(time()) -int(t) < .5:
            pulse_start_time = time()
      while GPIO.input(VOL_ECHO)==1:
            pulse_end_time = time()

      pulse_duration = pulse_end_time - pulse_start_time
      distance = round(pulse_duration * 18500, 2) # scaling
      return distance + 45 # offset

sender = udp_client.SimpleUDPClient('127.0.0.1',4559) # send to Sonic Pi
pitch = 50 # initial pitch value
volume = 50 # initial volume level

# threaded, listen for key press/release
def listen():
      while True:
            with keyboard.Listener(on_press=on_press,
                                   on_release=changetone) as listener:
                  listener.join()

# send pitches and volume data to Sonic Pi
def sendNotes():
      global tone 
      while True: # send until interrupt             
            
            try:
                  # convert volume's distance to min-maxed volume value
                  volume = min(max(round(volDist()), 20), 100)

                  # convert pitch's distance to min-maxed pitch value
                  pitch = min(max(round(dist()), 30),  200)

            # catch
            except Exception as e:
                  print(e)
                  
            print("Pitch value:", pitch)

            # no pitches send over value of 110
            if pitch < 110:

                  # send tone to Sonic Pi
                  sender.send_message('/synth',tone)

                  # send pitch value to Sonic Pi
                  sender.send_message('/play_this', pitch) 
                  sleep(0.05) # sensor rest
            
            # change system volume
            call(["amixer",'sset', 'PCM', str(volume)+ "%"])

# keypress thread start
T.Thread(target=listen).start()

# pitch/volume/tone sending thread start
T.Thread(target=sendNotes).start()
