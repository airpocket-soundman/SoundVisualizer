#v204 The comments were translated into English.
#v203 Corrected comment. 
#v202 Changed heap mem size.
#v201 Qiita version
#v200 The magnification rate of the sound pressure map was changed with the lens change.

from Maix import MIC_ARRAY as mic
from Maix import FPIOA
from fpioa_manager import fm
import lcd
import sensor
import gc

from Maix import utils      #For checking and setting heap mem usage
utils.gc_heap_size(2500000) #Heap mem heap setting. Increased volume is required to process soundmap images stretched to 480*480.

lcd.init()
lcd.direction(lcd.YX_LRDU)   #Used in combination with hmirror and vflip to align soundmap and camera image orientation.
sensor.reset()
sensor.set_auto_gain(1)             #Automatic gain should enabled.
sensor.set_auto_whitebal(1)         #Auto WB should also be enabled.
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(3)
sensor.set_vflip(0)
sensor.run(1)

mic.init()
Fpioa = FPIOA()
LEDdir = (100,100,100)            #LED indicator display on the microphone array module, with RGB brightness set from 0-255. Not needed because of glare.

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

    img = sensor.snapshot()                         #Get camera image.

    soundmap = mic.get_map()                        #Estimated position of the sound source from the microphone array in 16*16pixel grayscale.
    sounddir = mic.get_dir(soundmap)                #Find sound source direction from soundmap.
    mic.set_led(sounddir,(LEDdir))                  #Light up the LEDs on the microphone array module.
    soundmap = soundmap.copy((2,4,12,8))            #Cut out the center 8*6 pixcel to match the picture scale of the sound map to the camera.
    soundmap = soundmap.resize(320,240)             #Enlarge sound map to 320*240pixel to match camera image
    maskmap = soundmap.copy()                       #Create mask-like image when combining soundmap and camera image
    maskmap = maskmap.binary([(1,255)])             #Binarize maskmap to mask.
    soundmap = soundmap.to_rainbow(1)               #Change soudnmap to rainbow color.
    img.blend(soundmap,alpha = 150,mask = maskmap)  #By using a mask, only the sound detection portion of the sound map can be overlaid on the camera image. 
                                                    #The higher the alpha value, the fainter the sound is displayed.
    lcd.display(img)

mic.deinit()
