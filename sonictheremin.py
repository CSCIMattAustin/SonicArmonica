from pynput import keyboard
import threading as T
import sys
from math import floor
from time import *
from pythonosc import osc_message_builder
from pythonosc import udp_client
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
isSent = False
tones = ['sine', 'piano', 'pluck']
tone = 'sine'
i = 0
PIN_TRIGGER = 23
PIN_ECHO = 24


def on_press(key):
      try:
            print(key.char)
            
      except AttributeError:
            print(key)
            
def changetone(key):
      global i
      global tones
      global tone
      global isSent
      if key == keyboard.Key.up:
            i += 1
            isSent = False
            tone = tones[i%len(tones)]
            return False
      
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

def dist():     
      GPIO.output(PIN_TRIGGER, GPIO.LOW)
      GPIO.output(PIN_TRIGGER, GPIO.HIGH)
      sleep(0.000001)
      
      GPIO.output(PIN_TRIGGER, GPIO.LOW)
      pulse_start_time = time()
      pulse_end_time = time()
      t = time()
      
      while GPIO.input(PIN_ECHO)==0 and int(time()) -int(t) < .5:
            pulse_start_time = time()
      while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time()

      pulse_duration = pulse_end_time - pulse_start_time
      distance = round(pulse_duration * 17150, 2)
      return distance + 40

count = 0
sender = udp_client.SimpleUDPClient('127.0.0.1',4559)
pitch = 50

count = 0
p = []
def listen():
      while True:
            with keyboard.Listener(on_press=on_press,on_release=changetone) as listener:
                  listener.join()
def sendNotes():
      global tone
      global isSent
      while True:
            try:
                  pitch = min(max(round(dist()), 40), 200)
            except Exception as e:
                  print(e)
            #if pitch > 105:
            #      continue
            #round((dist() % 1500) + 220))
            print(pitch)
            if pitch <105:
                  sender.send_message('/synth',tone)
                  sender.send_message('/play_this', pitch)
                  #if not isSent:
                  
                  #isSent = True
                  sleep(0.05)
                  #count += 1
     
T.Thread(target=listen).start()
T.Thread(target=sendNotes).start()
#sendNotes()
