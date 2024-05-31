from RpiMotorLib import RpiMotorLib

motor = RpiMotorLib.BYJMotor("motoror", "28BYJ")


def drive_motor():
    # keep looping reallly quickly
    while True:
        try:
            motor.motor_run(
                [24, 23, 6, 5], 0.001, 512, False, False, "half", 0.05
            )
        except KeyboardInterrupt:
            print("killing motor")
            motor.motor_stop()
            break


if __name__ == "__main__":
    drive_motor()
