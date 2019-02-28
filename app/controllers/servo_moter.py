import RPi.GPIO as GPIO
import time
import atexit


class SG90:
  """
  サーボモータ（sg90）の操作のためのクラス
  """
  def __init__(self, pin, direction):
    """
    初期化する。
    :param pin: GPIOのピン番号。PWMが使えること。
    :param direction: 初期の向き。 -100(一番左) から 100(一番右)までの場所を整数値で指定する
    :return: 
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    self.pin = int(pin)
    self.direction = int(direction)
    self.servo = GPIO.PWM(self.pin, 50)
    self.servo.start(0.0)
    atexit.register(self.cleanup)

  def cleanup(self):
    """
    最後は正面に戻して終了する
    :param self:
    :return:
    """
    self.servo.ChangeDutyCycle(self.henkan(0))
    time.sleep(0.3)
    self.servo.stop()
    GPIO.cleanup()

  def currentdirection(self):
    """
    現在のSG90の向きを返す。
    """
    return self.direction

  def henkan(self, value):
    """
    ChangeDutyCycleに渡すための値を計算する。
    -100から100のfloat値を入力して、2から12の値を返す。
    ChangeDutyCycleに渡す値は 0.0 <= dc <= 100.0
    ……のはずだが、なぜか2から12の間で動作している。
    """
    return 0.05 * value + 7.0

  def setdirection(self, direction, speed):
    """
    SG90の向きを変える。
    direction : -100 - 100 の整数値
    speed     : 変化量
    """
    for d in range(self.direction, direction, int(speed)):
      self.servo.ChangeDutyCycle(self.henkan(d))
      self.direction = d
      time.sleep(0.1)
    self.servo.ChangeDutyCycle(self.henkan(direction))
    self.direction = direction


if __name__ == '__main__':
    servo = SG90(4, 50)
    servo.setdirection(-50, 80)
    time.sleep(0.5)
    servo.cleanup()