from RpiMotorLib import RpiMotorLib

motor = RpiMotorLib.BYJMotor("motoror", "28BYJ")


def drive_motor():
    motor.motor_run([37, 35, 33, 29], 0.01, 100, False, False, "half", 0.05)


if __name__ == "__main__":
    drive_motor()
