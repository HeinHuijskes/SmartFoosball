from website.flask_website import *
import threading



def website_run(website):
    website.detect(0)

def arduino_run(arduino):
    arduino.detect()

website = Website()
website_run(website)
#
# def thread():
#     website = Website()
#     arduino = website.arduino
#     t1 = threading.Thread(target=arduino_run, args = (arduino,))
#     t2 = threading.Thread(target=website_run, args=(website,))
#
#     t1.start()
#     t2.start()
#     t1.join()
#     t2.join()
#
# thread()