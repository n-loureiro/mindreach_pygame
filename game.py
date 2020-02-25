import pygame
from pygame.locals import *
import serial
import numpy as np
from ballTile import *
from hdgTile import *
from mapTile import *


pygame.init()

###########################################################################
########################### get new decoder data ##########################
###########################################################################
def get_data():
    global writeVal
    data = ser.read(1)
    log = 1
    #if(data == 255):
    if(ord(data) == 255):
        data = ser.read(3)
        if(data[0] == 255 and data[1] == 0):
            #channel = data[2]
            channel = data[2]
            if(channel == 6):
                data = ser.read(4)
                log = s2.unpack(data)
                return(log[0])
            elif(channel > 0) and (channel < 6):
                data = ser.read(500)
                if(writeVal == 1):
                    dataBuffer1 = s.unpack(data)
                    writeVal = 2
                else:
                    dataBuffer2 = s.unpack(data)
                    writeVal = 1
                #unpacked_data = s.unpack(data)
                chanCounter = channel
                #newSample.emit(channel,writeVal)
        else:
            ser.flush()
            return(log)
    elif(data[0] == 5):
        #elif(data[0] == 5):
        #if not serialEnabled : 
        #    serialConn.emit(serialEnabled)
        enabled = 1
        print("Raw signals enabled!")
        return(log)
    else:
        return(log)
        ser.flush()
    return(log)
###########################################################################                  
###########################################################################


def main():
    mainloop = 1
    double_click_duration = 250
    last_click = pygame.time.get_ticks()
    tilt = 0

    screen_size_x = 1200
    screen_size_y = 800
    last_screen_size_x = screen_size_x
    last_screen_size_y = screen_size_y

    screen = pygame.display.set_mode((1200, 800),HWSURFACE|DOUBLEBUF|RESIZABLE)
    ball_obj = BallTile(screen, size_x=screen_size_x, size_y= screen_size_y)
    #map_obj = MapTile(screen, size_x=screen_size_x, size_y= screen_size_y)
    hdg_obj = HdgTile(screen, size_x=screen_size_x, size_y= screen_size_y)

    games = pygame.sprite.Group(ball_obj, hdg_obj)
    #games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)

    while mainloop:

        screen.fill((0,0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:  # or MOUSEBUTTONDOWN depending on what you want.
                now = pygame.time.get_ticks()
                if now - last_click <= double_click_duration:
                    map_obj.clear_waypoints()
                else:
                    print(event.pos)
                    map_obj.set_new_waypoint(event.pos)
                last_click = pygame.time.get_ticks()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print('button click ESC!!!!')
                    mainloop = False
                elif event.key == pygame.K_UP:
                    tilt += 45
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_DOWN:
                    tilt -= 45
                    hdg_obj.rot_center(tilt)
            elif event.type==VIDEORESIZE:
                print('here')
                screen=pygame.display.set_mode(event.dict['size'],HWSURFACE|DOUBLEBUF|RESIZABLE)
                screen_size_x, screen_size_y = screen.get_size()
                #ball_obj = BallTile(screen, size_x=screen_size_x, size_y= screen_size_y)
                #map_obj = MapTile(screen, size_x=screen_size_x, size_y= screen_size_y)
                hdg_obj = HdgTile(screen, size_x=screen_size_x, size_y= screen_size_y)
                games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)
        clock = pygame.time.Clock()

        
        #ball_obj.drawBallHistory([0,10,20,30,40,50,60], [20+20,10+20,20+20,10+20,20+20,30+20,20*np.random.rand()+20])
        #ball_obj.drawThresholdLines()

        hdg_obj.drawTerrain(tilt)    

        games.update()        
        #games.draw(screen)
        pygame.display.flip()
        clock.tick(8)


if __name__ == '__main__':
    main()