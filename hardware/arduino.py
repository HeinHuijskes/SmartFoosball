import serial

serialConnection = None
goals_red = 0

def setup():
    global serialConnection
    serialConnection = serial.Serial('COM3', 9600)

def main():
    global serialConnection, goals_red
    while True:
        line = getLine()
        # print(line)
        if line == ('Goal red\r\n'):
            goals_red += 1
            print('Red goals:', goals_red)

def getLine():
    line = serialConnection.readline()
    line = line.decode('ascii')
    return line

if __name__ == '__main__':
    setup()
    main()
