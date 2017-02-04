#!/usr/bin/env python2.7
##                            _ _      
##                           | | |     
##      _   _  __ _ _ __   __| | | ___ 
##     | | | |/ _` | '_ \ / _` | |/ _ \
##     | |_| | (_| | | | | (_| | |  __/
##      \__, |\__,_|_| |_|\__,_|_|\___|
##       __/ |                    (2015)     
##      |___/
##
##      Monitor a PIR sensor for motion during a set time of day
##      and play a sound at your target - if motion persists then
##      send an alert via Google Hangouts.
##
##      Note:   Your device will require its own Gmail account to send
##              messages from. You will also need to alter the settings
##              on its account to allow 3rd party software interactions.
##              The reason we go to all the trouble of setting this up is:
##             [!] Gmail considers this practice to be very insecure. [!]
##              Once its setup however, it can send Hangouts messages, as
##              well as text messages to various cell carriers.

import RPi.GPIO as GPIO
import datetime, xmpp, pygame
from random import randint
from time import sleep

############################################################################################
#### Settings ##############################################################################

# Set GPIO pin on RPI to PIR sensor
sensor = 4

## Change this value to your Gmail address to receive notifications via Google Hangouts
contact_email = 'your@email.address'

## Change this value to your raspberry pi's gmail address for sending notifications
rasp_email = 'rasp@email.address'

## Change this value to your raspberry pi's gmail password
rasp_auth = '<password>'

############################################################################################
############################################################################################

# Setup GPIO / default sensor states
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)


# Function to send a message via Google Hangouts
def hangouts_message(email):
    dateStr = datetime.datetime.now().strftime("(%m/%d/%y - %I:%M:%S:%p)")
    # Warning message to send
    message = ("Motion in the designated zone has exceeded the threshold [%s]" % (dateStr))
    jid = xmpp.protocol.JID(rasp_email)  # Senders Email Address
    cl = xmpp.Client(jid.getDomain(), debug=[])
    cl.connect()
    cl.auth(jid.getNode(), rasp_auth)  # Senders authentication credentials
    cl.send(xmpp.protocol.Message(email, message, typ='chat'))


# Allow for audio / Hangouts alerts to be disabled or enabled during certain times of day.
class time_of_day():
    # Times are in 24 hour format (1930 would be equal to 7:30pm)
    # 24h: (01) (02) (03) (04) (05) (06) (07) (08) (09) (10) (11) (12) (13) (14) (15) (16) (17) (18) (19) (20) (21) (22) (23) (24)
    # 12h: (01) (02) (03) (04) (05) (06) (07) (08) (09) (10) (11) (12) (01) (02) (03) (04) (05) (06) (07) (08) (09) (10) (11) (12)
    def audio(self):
        start_time = 1900  # 1930 - 7:30 PM
        stop_time = 810  # 0730 - 7:30 AM
        current_hour = datetime.datetime.now().strftime("%H%M")
        if int(current_hour) >= int(start_time) or int(current_hour) <= int(stop_time):
            return True
        else:
            return False

    def hangouts(self):
        start_time = 1900  # 1930 - 7:30 PM
        stop_time = 810  # 730 - 7:30 AM
        current_hour = datetime.datetime.now().strftime("%H%M")
        if int(current_hour) >= int(start_time) or int(current_hour) <= int(stop_time):
            return True
        else:
            return False


# Handle audio events
class audio_event():
    # instantiate the pygame mixer
    pygame.mixer.init()

    def active_a(self):
        rand_file = randint(1, 4)
        path = 'audio/active/'
        file = str(rand_file) + ".wav"  # Select a random file from the folder
        audio = path + file
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def error_a(self):
        rand_file = randint(1, 5)
        path = 'audio/error/'
        file = str(rand_file) + ".wav"  # Select a random file from the folder
        audio = path + file
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def found_a(self):
        rand_file = randint(1, 8)
        path = 'audio/found/'
        file = str(rand_file) + ".wav"  # Select a random file from the folder
        audio = path + file
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def idle_a(self):
        path = 'audio/idle/'
        file = "ping.wav"
        audio = path + file
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def lost_a(self):
        rand_file = randint(1, 11)
        path = 'audio/lost/'
        file = str(rand_file) + ".wav"  # Select a random file from the folder
        audio = path + file
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def shutdown_a(self):
        rand_file = randint(1, 12)
        path = 'audio/shutdown/'
        file = str(rand_file) + '.wav'  # Select a random file from the folder
        audio = path + file
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue


def main_loop():
    play_found = True
    play_lost = True
    previous_state = False
    current_state = False
    audio = audio_event()
    tod = time_of_day()
    try:
        play_audio = tod.audio()
        if play_audio == True:
            audio.active_a()
        tick_high = 2  # Number of ticks to wait before triggering an audio event when motion is detected
        tick_low = 10  # Number of ticks to wait before triggering an audio event when no motion is detected
        hangouts_alarm = 3  # Number of motion events triggered before triggering a Hangouts alert.

        while True:
            # sleep(0.1)
            play_audio = tod.audio()
            send_hangouts = tod.hangouts()
            dateStr = datetime.datetime.now().strftime("(%m/%d/%y - %I:%M:%S:%p)")
            previous_state = current_state
            current_state = GPIO.input(sensor)

            # Some evaluations to restrict audio from playing constantly
            if tick_high == 0:
                play_found = True
            else:
                tick_high = tick_high - 1

            if tick_low == 7 or tick_low == 3:
                play_lost = True
            else:
                play_lost = False

            if current_state == True:
                new_state = "HIGH"
                hangouts_alarm = hangouts_alarm - 1  # Start counting motion events to trigger a Hangouts alert
                if play_found == True:
                    print("GPIO pin %s is %s - %s" % (sensor, new_state, dateStr))
                    if play_audio == True:
                        audio.found_a()
                    tick_high = 2
                    tick_low = 10
                    play_found = False
                sleep(1)

            else:
                new_state = "LOW"
                tick_low = tick_low - 1
                if hangouts_alarm <= 10:  # Combat motion events to delay triggering a Hangouts alert and cut back on spam.
                    hangouts_alarm = hangouts_alarm + 1
                # print hangouts_alarm
                if play_lost == True:
                    print("GPIO pin %s is %s - %s" % (sensor, new_state, dateStr))
                    if play_audio == True:
                        audio.lost_a()
                    tick_high = 0
                    play_lost = False
                sleep(1)

            if hangouts_alarm <= 0 and send_hangouts == True:  # Only trigger Hangouts alerts during pre-set times
                # Who to send warning message to
                hangouts_message(contact_email)
                hangouts_alarm = 3  # Reset the Hangouts alarm trigger


    except KeyboardInterrupt:
        play_audio = tod.audio()
        if play_audio == True:
            audio.shutdown_a()
        print "\n...Quit.\n"
        GPIO.cleanup()


main_loop()
