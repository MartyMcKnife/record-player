from RpiMotorLib import RpiMotorLib

motor = RpiMotorLib.BYJMotor("motoror", "28BYJ")


def drive_motor():
    motor.motor_run([24, 23, 6, 5], 0.01, 100, False, False, "half", 0.05)


if __name__ == "__main__":
    drive_motor()
