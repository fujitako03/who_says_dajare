import RPi.GPIO as GPIO


# SG92Rをコントロールするための
class SG90_92R_Class:
    # コンストラクタ
    def __init__(self, pin, zero_offset_duty):
        self.mPin = pin
        self.m_ZeroOffsetDuty = zero_offset_duty

        # GPIOをPWMモードにする
        GPIO.setup(self.mPin, GPIO.OUT)
        self.mPwm = GPIO.PWM(self.mPin, 50) # set 20ms / 50 Hz

    # 位置セット
    def SetPos(self, pos):
        # Duty ratio = 2.5%〜12.0% : 0.5ms〜2.4ms : 0 ～ 180deg
        duty = (12-2.5)/180*pos+2.5 + self.m_ZeroOffsetDuty
        self.mPwm.start(duty)

    # 終了処理
    def Cleanup(self):
        # サーボを10degにセットしてから、インプットモードにしておく
        self.SetPos(90)
        time.sleep(1)
        GPIO.setup(self.mPin, GPIO.IN)