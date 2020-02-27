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

    video_infos = pygame.display.Info()
    screen_size_x, screen_size_y = video_infos.current_w, video_infos.current_h
    screen = pygame.display.set_mode((screen_size_x, screen_size_y), HWSURFACE|DOUBLEBUF|RESIZABLE)

    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN,HWSURFACE|DOUBLEBUF|RESIZABLE)
    ball_obj = BallTile((0, screen_size_y*0.6), (screen_size_x*0.65, screen_size_y*0.4))
    map_obj = MapTile((0, 0), (screen_size_x, screen_size_y*0.6))
    hdg_obj = HdgTile((screen_size_x*0.65, screen_size_y*0.6), (screen_size_x*0.35, screen_size_y*0.4))

    ball_flag = 1
    map_flag = 1
    hdg_flag = 1

    games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)
    timer = pygame.time.get_ticks()
    while mainloop:

        screen.fill((0,0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:  # or MOUSEBUTTONDOWN depending on what you want.
                
                now = pygame.time.get_ticks()
                if event.button == 2:
                    map_obj.clear_waypoints()
                elif now - last_click <= double_click_duration:
                    map_obj.clear_waypoints()
                else:
                    print(event.pos)
                    map_obj.set_new_waypoint(event.pos)
                last_click = pygame.time.get_ticks()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    map_obj.speed += 1
                elif event.key == pygame.K_s:
                    map_obj.speed -= 1
                elif event.key == pygame.K_a:
                    map_obj.angle_speed = -20
                    tilt = -27
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_d:
                    map_obj.angle_speed = 20
                    tilt = 27
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_UP:
                    tilt += 2.5
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_DOWN:
                    tilt -= 2.5
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_SPACE:
                    map_obj.create_drone()
                elif event.key == pygame.K_ESCAPE:
                    print('button click ESC!!!!')
                    mainloop = False
                elif event.key == pygame.K_p:
                    ball_flag = 1
                    map_flag = 0
                    hdg_flag = 0
                    ball_obj = BallTile((0, 0), (screen_size_x, screen_size_y))
                    games = pygame.sprite.Group(ball_obj)
                elif event.key == pygame.K_o:
                    ball_flag = 0
                    map_flag = 1
                    hdg_flag = 0
                    map_obj = MapTile((0, 0), (screen_size_x, screen_size_y))
                    games = pygame.sprite.Group(map_obj)
                elif event.key == pygame.K_i:
                    ball_flag = 0
                    map_flag = 0
                    hdg_flag = 1
                    hdg_obj = HdgTile((0, 0), (screen_size_x, screen_size_y))
                    games = pygame.sprite.Group(hdg_obj)
                elif event.key == pygame.K_u:
                    ball_flag = 1
                    map_flag = 1
                    hdg_flag = 1
                    ball_obj = BallTile((0, screen_size_y*0.6), (screen_size_x*0.65, screen_size_y*0.4))
                    map_obj = MapTile((0, 0), (screen_size_x, screen_size_y*0.6))
                    hdg_obj = HdgTile((screen_size_x*0.65, screen_size_y*0.6), (screen_size_x*0.35, screen_size_y*0.4))
                    games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    map_obj.angle_speed = 0
                    tilt = 0
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_d:
                    map_obj.angle_speed = 0 
                    tilt = 0
                    hdg_obj.rot_center(tilt)           
            elif event.type==VIDEORESIZE:
                print('here')
                screen=pygame.display.set_mode(event.dict['size'],HWSURFACE|DOUBLEBUF|RESIZABLE)
                screen_size_x, screen_size_y = screen.get_size()
                ball_obj = BallTile((0, screen_size_y*0.6), (screen_size_x*0.65, screen_size_y*0.4))
                map_obj = MapTile((0, 0), (screen_size_x, screen_size_y*0.6))
                hdg_obj = HdgTile((screen_size_x*0.65, screen_size_y*0.6), (screen_size_x*0.35, screen_size_y*0.4))
                games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)
        clock = pygame.time.Clock()

        
        new_pos = np.random.rand()*2 - 1

        if ball_flag:
            ball_obj.drawBallHistory(new_pos)
            ball_obj.drawThresholdLines()
        
        if hdg_flag:
            hdg_obj.rot_center(new_pos*27)
        
        if map_flag:
            map_obj.angle_speed = new_pos*20

        games.update()        
        games.draw(screen)
        pygame.display.flip()

        clock.tick(40)
        timer = pygame.time.get_ticks()


if __name__ == '__main__':
    main()