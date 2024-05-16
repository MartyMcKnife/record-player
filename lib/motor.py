from RpiMotorLib import RpiMotorLib

motor = RpiMotorLib.BYJMotor("1", "28BYJ")


def drive_motor():
    while True:
        motor.motor_run([39, 33, 31, 29], wait=0.005)


if __name__ == "__main__":
    while True:
        drive_motor()
