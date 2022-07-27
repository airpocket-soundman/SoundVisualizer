#v203 コメント修正 
#v202 heap mem
#v201 Qiitaアップ版
#v200 soundmap 拡大率調整版

from Maix import MIC_ARRAY as mic
from Maix import FPIOA
from fpioa_manager import fm
import lcd
import sensor
import gc

from Maix import utils      #heap mem使用量確認及び設定用
utils.gc_heap_size(2500000) #Heap mem山盛り設定　soundmap画像を480*480に引き伸ばし処理するため増量必要。

lcd.init()
lcd.direction(lcd.YX_LRDU)   #soundmapとcameraイメージの向き合わせのため、hmirrorとvflipと組み合わて使用。
sensor.reset()
sensor.set_auto_gain(1)             #自動ゲインは入れましょう。
sensor.set_auto_whitebal(1)         #自動WBも入れましょう
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(3)
sensor.set_vflip(0)
sensor.run(1)

mic.init()
Fpioa = FPIOA()
LEDdir = (100,100,100)            #マイクアレイモジュールのLEDインジケーター表示。RGBの輝度を0-255で設定。まぶしいのでいらない。

#Maxi Bit用のピン設定。
Fpioa.set_function(23, fm.fpioa.I2S0_IN_D0);
Fpioa.set_function(22, fm.fpioa.I2S0_IN_D1);
Fpioa.set_function(21, fm.fpioa.I2S0_IN_D2);
Fpioa.set_function(20, fm.fpioa.I2S0_IN_D3);
Fpioa.set_function(19, fm.fpioa.I2S0_WS);
Fpioa.set_function(18, fm.fpioa.I2S0_SCLK);
Fpioa.set_function(17, fm.fpioa.GPIOHS28);
Fpioa.set_function(15, fm.fpioa.GPIOHS27);

while True:

    img = sensor.snapshot()                         #カメラ画像取得

    soundmap = mic.get_map()                        #マイクアレイから音源の推定位置を16*16pixelのgrayscaleで求める。
    sounddir = mic.get_dir(soundmap)                #soundmapから音源方向を求める？
    mic.set_led(sounddir,(LEDdir))                  #マイクアレイモジュールのLEDを光らせる。
    soundmap = soundmap.copy((2,4,12,8))            #サウンドマップの画格をカメラに合わせるため、中央8*6pixcelを切り出す
    soundmap = soundmap.resize(320,240)             #サウンドマップをカメラ画像に合わせるため320*240pixelに拡大
    maskmap = soundmap.copy()                       #soundmapとカメラ画像を合成する際のマスク様画像を作成
    maskmap = maskmap.binary([(1,255)])             #maskmapを二値化してマスクにする。
    soundmap = soundmap.to_rainbow(1)               #soudnmapをレインボーカラーに変更
#    img = img.copy((30,0,240,240))                 #合成する前にカメラ画像をsoundmapとサイズ合わせる。
    img.blend(soundmap,alpha = 150,mask = maskmap)  #マスクを使い、soundmapの音検出部分のみをカメラ画像に重ね合わせる。alpha値が大きいほど音の表示が薄くなる。
    lcd.display(img)

mic.deinit()
