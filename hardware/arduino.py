import serial


def main():
    ser = serial.Serial('COM3', 9600)

    while True:
        print(ser.readline())


if __name__ == '__main__':
    main()
