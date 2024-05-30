from RpiMotorLib import RpiMotorLib

motor = RpiMotorLib.BYJMotor("motoror", "28BYJ")


def drive_motor():
    # keep looping reallly quickly
    while True:
        try:
            motor.motor_run(
                [24, 23, 6, 5], 0.0005, 512000, False, False, "half", 0.05
            )
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    drive_motor()
