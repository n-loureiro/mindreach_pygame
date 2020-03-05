import pygame
from pygame.locals import *
import serial
import numpy as np
from ballTile import *
from hdgTile import *
from mapTile import *
import struct
import copy

import pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import pylab
import scipy.io

import re
import os

from EEGsignals import *

import faulthandler; faulthandler.enable()

###########################################################################
########################### get new decoder data ##########################
###########################################################################
def get_data(ser,s2):
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
                # if(writeVal == 1):
                #     dataBuffer1 = s.unpack(data)
                #     writeVal = 2
                # else:
                #     dataBuffer2 = s.unpack(data)
                #     writeVal = 1
                # #unpacked_data = s.unpack(data)
                # chanCounter = channel
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


###########################################################################
def normalize_all_thresholds(thrsh_real):
    range_real = thrsh_real['upRange'] - thrsh_real['downRange']
    scaling_factor = 2/range_real
    thrsh_norm = copy.deepcopy(thrsh_real)
    
    for i in thrsh_norm:
        thrsh_norm[i] = 1 - (thrsh_real[i] - thrsh_real['downRange'])*scaling_factor
    return(thrsh_norm, scaling_factor)

###########################################################################



def main_game(username):



    print(username)


    pygame.init()

    list_of_pos_real = []

    mainloop = 1
    double_click_duration = 150
    last_click = pygame.time.get_ticks()

    ##################################################################################
    ############################# configure BLUETOOTH  ###############################
    ser = serial.Serial()

    ser.baudrate = 115200
    ser.port = str('/dev/tty.mindreachBTv4-Bluetooth')
    ser.rtscts = 1

    ser.open()
     
    print("Ready to receive packets!\r\n")

    s = struct.Struct('f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f f')
    s2 = struct.Struct('f')

    dataSend = bytes([0x77, 0x61])
    ser.write(dataSend)
    #################################################################################
    #################################################################################

    #################################################################################
    ############################## GET THRESHOLDS ###################################
    subj = username

    
    try:
        pathData = '/Users/nunoloureiro/mindreach/software_eeg/mindreach_demo/data/'
        pathUser = pathData+'subj_' + subj+ "/"
        g = open( pathUser +'thresholds.txt', 'r')
        thresholds_real = eval(g.read())
        thresholds_norm, scaling_factor = normalize_all_thresholds(thresholds_real)
    except:
        print("USER  ->  " + str(username) + " <- does not exist")
        mainloop = False  
        return 0

    ##################################################################################
    ##################################################################################

    screen_size_x = 1200
    screen_size_y = 800
    last_screen_size_x = screen_size_x
    last_screen_size_y = screen_size_y

    video_infos = pygame.display.Info()
    screen_size_x, screen_size_y = video_infos.current_w, video_infos.current_h
    screen = pygame.display.set_mode((screen_size_x, screen_size_y), HWSURFACE|DOUBLEBUF|RESIZABLE)

    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN,HWSURFACE|DOUBLEBUF|RESIZABLE)
    ball_obj = BallTile((0, screen_size_y*0.6), (screen_size_x*0.65, screen_size_y*0.4),thresholds_norm)
    map_obj = MapTile((0, 0), (screen_size_x, screen_size_y*0.6))
    hdg_obj = HdgTile((screen_size_x*0.65, screen_size_y*0.6), (screen_size_x*0.35, screen_size_y*0.4))

    ball_flag = 1
    map_flag = 1
    hdg_flag = 1

    tilt = 0

    games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)
    timer = pygame.time.get_ticks()

    while mainloop:

        screen.fill((0,0,0))

        clock = pygame.time.Clock()

        #new_pos_real = np.random.rand()*2 - 1
        new_pos_real = float(get_data(ser,s2))
        new_pos_norm = -1 + (new_pos_real - thresholds_real['downRange'])*scaling_factor

        list_of_pos_real.append(new_pos_real)

        if ball_flag:
            ball_obj.drawBallHistory(new_pos_norm)
            ball_obj.drawThresholdLines()
        
        if hdg_flag:
            hdg_obj.rot_center(new_pos_norm*27)
        
        if map_flag:
            map_obj.angle_speed = new_pos_norm*20
            #print(map_obj.angle_speed)

        games.update()        
        games.draw(screen)
        pygame.display.flip()
        #print(pygame.time.get_ticks() - timer)

        clock.tick(60)
        timer = pygame.time.get_ticks()


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
                    map_obj.angle_speed = -10
                    tilt = -27
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_d:
                    map_obj.angle_speed = 10
                    tilt = 27
                    hdg_obj.rot_center(tilt)
                elif event.key == pygame.K_UP:
                    tilt += 2.5
                    map_obj.BMI_help += 0.05
                    if map_obj.BMI_help > 1:
                        map_obj.BMI_help =1
                elif event.key == pygame.K_DOWN:
                    #tilt -= 2.5
                    map_obj.BMI_help -= 0.05
                    if map_obj.BMI_help < 0:
                        map_obj.BMI_help =0
                elif event.key == pygame.K_SPACE:
                    map_obj.create_drone()
                elif event.key == pygame.K_p:
                    ball_flag = 1
                    map_flag = 0
                    hdg_flag = 0
                    ball_obj = BallTile((0, 0), (screen_size_x, screen_size_y),thresholds_norm)
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
                    ball_obj = BallTile((0, screen_size_y*0.6), (screen_size_x*0.65, screen_size_y*0.4),thresholds_norm)
                    map_obj = MapTile((0, 0), (screen_size_x, screen_size_y*0.6))
                    hdg_obj = HdgTile((screen_size_x*0.65, screen_size_y*0.6), (screen_size_x*0.35, screen_size_y*0.4))
                    games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)
                elif event.key == pygame.K_m:
                    pygame.quit()
                    all_files = [f for f in os.listdir(pathUser) if f.startswith('positions')]
                    all_files.sort(key=lambda f: int(re.sub('\D', '', f)))
                    last_file = all_files[-1]
                    idx_last = last_file.split('_')[1].split('.')[0]
                    with open(pathUser + "positions_" + str(int(idx_last)+1)+ ".txt", "wb") as filehandle:
                        # store the data as binary data stream
                        pickle.dump(list_of_pos_real, filehandle)
                    return 2
                elif event.key == pygame.K_ESCAPE:
                    print('button click ESC!!!!')
                    pygame.quit()
                    all_files = [f for f in os.listdir(pathUser) if f.startswith('positions')]
                    all_files.sort(key=lambda f: int(re.sub('\D', '', f)))
                    last_file = all_files[-1]
                    idx_last = last_file.split('_')[1].split('.')[0]
                    with open(pathUser + "positions_" + str(int(idx_last)+1)+ ".txt", "wb") as filehandle:
                        # store the data as binary data stream
                        pickle.dump(list_of_pos_real, filehandle)
                    mainloop = False  
                    return 0   
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
                ball_obj = BallTile((0, screen_size_y*0.6), (screen_size_x*0.65, screen_size_y*0.4),thresholds_norm)
                map_obj = MapTile((0, 0), (screen_size_x, screen_size_y*0.6))
                hdg_obj = HdgTile((screen_size_x*0.65, screen_size_y*0.6), (screen_size_x*0.35, screen_size_y*0.4))
                games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)

def main():
    mainloop = True
    app_n = 2
    first = 1
    username = "nuno"
    while mainloop:   
        if app_n == 1:
            ret = main_game(username)
            #mainloop = False
            app_n = ret
        elif app_n == 2:
            if first:
                app = QtGui.QApplication(sys.argv)
                ex = tabdemo()
                ex.show()
                app.exec_()
                app_n = ex.app_after_exit
                username = ex.usernameGame
                first = 0
            else:
                ex.show()
                app.exec_()
                app_n = ex.app_after_exit
                username = ex.usernameGame
            #sys.exit(app.exec_())
            #app_n = 3
        else:
             mainloop = False   

if __name__ == '__main__':
    main()