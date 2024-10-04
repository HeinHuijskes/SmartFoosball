from website.flask_website import *
import threading



def website_run(website):
    website.run(0)

def arduino_run(arduino):
    arduino.run()

website = Website()
website_run(website)

#TODO : - speed on website (check), -webcam working (check), -left=red , -laggy delay on website, -information page
#TODO : - start a new game on site - when goal scored https://html-shark.com/HTML/Marquee.htm


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