# ----------------------------------------- #
#
# _movement_detection_f01_
#
# dep.:
# pygame | numpy | espeak (for voice, optional)
#
# list cam.:
# $ ls -ltrh /dev/video*
#
# ----------------------------------------- #

import pygame
import pygame.camera
from pygame.locals import *
import numpy as np
# import time
import os

# ----------------------------------------- #

DEVICE = "/dev/video0"
SIZE = (640, 480)
FILENAME = "capture.png"
NOISE = 30000   # sensitivity treshold
PATH = "./img/"
SAVE = False
VOICE = False   # linux

# ----------------------------------------- #

def camstream():    
    pygame.init()
    pygame.camera.init()
    display = pygame.display.set_mode(SIZE, 0)
    pygame.display.set_caption("_motion_detection_")
    camera = pygame.camera.Camera(DEVICE, SIZE)
    camera.start()
    screen = pygame.surface.Surface(SIZE, 0, display)
    capture = True
    count = 0
    
    # get 3 first frames
    # minus
    screen = camera.get_image(screen)
    arr0 = np.array(pygame.surfarray.array3d(screen), dtype='int16')
    # normal
    screen = camera.get_image(screen)        
    arr1 = np.array(pygame.surfarray.array3d(screen), dtype='int16')
    # plus
    screen = camera.get_image(screen)        
    arr2 = np.array(pygame.surfarray.array3d(screen), dtype='int16')

    while capture:
        # debug delay
        # time.sleep(1)
        
        d1 = np.clip(np.absolute(arr2 - arr1) * 10, 0, 255)
        d2 = np.clip(np.absolute(arr1 - arr0) * 10, 0, 255)
        d = np.clip(np.bitwise_and(d1, d2), 0, 255)
        # print d.shape
        
        # experiments
        # print np.max(d[:, :, 0] + d[:, :, 1] + d[:, :, 2]) / 3
        d = (((d[:, :, 0] + d[:, :, 1] + d[:, :, 2]) / 3) > (np.ones(SIZE) * 190)) * 255
        d = np.clip(np.rollaxis(np.tile(d, (3,1,1)), 0, 3), 0, 255)
        
        sumd = np.sum(d)
        print sumd   # ---> NOISE 
        
        if sumd - NOISE > 0:
            print "-------------", (sumd - NOISE) / 10e5, "move", count
            if SAVE:
                pygame.image.save(screen, PATH + str(count) + "_i.png")
            if VOICE and sumd - 1e3 * NOISE > 0:
                os.system('espeak -s 210 "please step away from the vehicle"')                
            count += 1
        
        screen = pygame.surfarray.make_surface(np.array(d, dtype='uint8'))
        
        display.blit(screen, (0, 0))
        pygame.display.flip()
        
        # frame update
        arr0 = arr1
        arr1 = arr2
        screen = camera.get_image(screen)        
        arr2 = np.array(pygame.surfarray.array3d(screen), dtype='int16')
        
        for event in pygame.event.get():
            if event.type == QUIT:
                capture = False
            elif event.type == KEYDOWN and event.key == K_s:
                pygame.image.save(screen, FILENAME)
    
    camera.stop()
    pygame.quit()
    return

if __name__ == '__main__':
    camstream()

# ----------------------------------------- #
