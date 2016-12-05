import sys
import tty
import termios


# init(). Initialises GPIO pins, switches motors and LEDs Off, etc
def init():
    global p, q, a, b, pwm, pcfADC, PGType
    PGType = PGFull
    # Initialise the PCA9685 PWM device using the default address
    try:
        pwm = PWM(0x40, debug = False)
        pwm.setPWMFreq(60)  # Set frequency to 60 Hz
    except:
        PGType = PGLite # No PCA9685 so set to Pi2Go-Lite

    #use physical pin numbering
    GPIO.setmode(GPIO.BOARD)

    #use pwm on inputs so motors don't go too fast
    GPIO.setup(L1, GPIO.OUT)
    p = GPIO.PWM(L1, 20)
    p.start(0)

    GPIO.setup(L2, GPIO.OUT)
    q = GPIO.PWM(L2, 20)
    q.start(0)

    GPIO.setup(R1, GPIO.OUT)
    a = GPIO.PWM(R1, 20)
    a.start(0)

    GPIO.setup(R2, GPIO.OUT)
    b = GPIO.PWM(R2, 20)
    b.start(0)

    # Initalise the ADC
    pcfADC = None # ADC object
    try:
        pcfADC = sgh_PCF8591P(1) #i2c, 0x48)
    except:
        PGType = PGLite


# Pins 24, 26 Left Motor
# Pins 19, 21 Right Motor
L1 = 26
L2 = 24
R1 = 19
R2 = 21


UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

# taken from a youtube tutorial on how to read input from keyboad, including arrows and AWSD pad
def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
        raise KeyboardInterrupt
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return ord(c3) - 65  # 0=Up, 1=Down, 2=Right, 3=Left arrows

speed = 30

# stop(): Stops both motors
def stop():
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(0)
    
# forward(speed): Sets both motors to move forward at speed. 0 <= speed <= 100
def forward(speed):
    p.ChangeDutyCycle(speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(speed)
    b.ChangeDutyCycle(0)
    p.ChangeFrequency(speed + 5)
    a.ChangeFrequency(speed + 5)
    
# reverse(speed): Sets both motors to reverse at speed. 0 <= speed <= 100
def reverse(speed):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(speed)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(speed)
    q.ChangeFrequency(speed + 5)
    b.ChangeFrequency(speed + 5)

# spinLeft(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spinLeft(speed):
    p.ChangeDutyCycle(0)
    q.ChangeDutyCycle(speed)
    a.ChangeDutyCycle(speed)
    b.ChangeDutyCycle(0)
    q.ChangeFrequency(speed + 5)
    a.ChangeFrequency(speed + 5)
    
# spinRight(speed): Sets motors to turn opposite directions at speed. 0 <= speed <= 100
def spinRight(speed):
    p.ChangeDutyCycle(speed)
    q.ChangeDutyCycle(0)
    a.ChangeDutyCycle(0)
    b.ChangeDutyCycle(speed)
    p.ChangeFrequency(speed + 5)
    b.ChangeFrequency(speed + 5)
    

# cleanup(). Sets all motors and LEDs off and sets GPIO to standard values
def cleanup():
    stop()
    setAllLEDs(0, 0, 0)
    stopServod()
    time.sleep(1)
    GPIO.cleanup()


init()

# Main body of code - this detects your key press and changes direction depending on it
try:
    while True:
        keyp = readkey()
        if keyp == 'w' or keyp == UP:
            pi2go.forward(speed)
        elif keyp == 's' or keyp == DOWN:
            pi2go.reverse(speed)
        elif keyp == 'd' or keyp == RIGHT:
            pi2go.spinRight(speed)
        elif keyp == 'a' or keyp == LEFT:
            pi2go.spinLeft(speed)
        elif keyp == ' ':
            pi2go.stop()
            print 'Stop'
        elif ord(keyp) == 3:
            break

# When you want to exit - press ctrl+c and it will generate a keyboard interrupt - this is handled nicely here!
except KeyboardInterrupt:
    GPIO.cleanup()
