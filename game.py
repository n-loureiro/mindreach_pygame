import pygame
from pygame.locals import *
import serial
import numpy as np
from ballTile import *
from hdgTile import *


pygame.init()

# class ball_tile(pygame.sprite.Sprite):
#     def __init__(self, canvas, size_x, size_y):
#         super().__init__()
#         self.tile_size_x = size_x/2
#         self.tile_size_y = size_y*0.4

#         self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
#         self.image.fill((90, 30, 30))
#         self.rect = self.image.get_rect(left= 0, top=size_y*0.6)
#         self.canvas = canvas
#         #self.canvas.blit(self.image, (size_x/2,size_y*0.6))

#     ###Draw Ball and last 5 positions as history
#     def drawBallHistory(self, posx, posy):
#         self.image.fill((90, 30, 30))
#         #Draw history and ball
#         for i in range(6): 
#             pygame.draw.line(self.image, (0,0,255), [self.tile_size_x*posx[i]/100, self.tile_size_y*posy[i]/100], [self.tile_size_x*posx[i+1]/100, self.tile_size_y*posy[i+1]/100], 3)
#         pygame.draw.circle(self.image, (255,0,0), (int(self.tile_size_x*posx[6]/100), int(self.tile_size_y*posy[6]/100)), 20)



class MapTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()
        self.tile_size_x = size_x
        self.tile_size_y = size_y*0.6

        self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.image = pygame.Surface((size_x, size_y*0.6))
        self.image.fill((90, 90, 30))
        self.rect = self.image.get_rect(left=0)
        self.canvas = canvas
        #self.canvas.blit(self.image, (0,size_y*0.6))



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

    screen_size_x = 1200
    screen_size_y = 800

    screen = pygame.display.set_mode((1200, 800),HWSURFACE|DOUBLEBUF|RESIZABLE)
    ball_obj = BallTile(screen, size_x=screen_size_x, size_y= screen_size_y)
    hdg_obj = HdgTile(screen, size_x=screen_size_x, size_y= screen_size_y)
    map_obj = MapTile(screen, size_x=screen_size_x, size_y= screen_size_y)

    games = pygame.sprite.Group(ball_obj, hdg_obj, map_obj)

    while mainloop:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    print('button click ESC!!!!')
                    mainloop = False
        clock = pygame.time.Clock()



        
        ball_obj.drawBallHistory([0,10,20,30,40,50,60], [20,10,20,10,20,30,30*np.random.rand()])
        ball_obj.drawThresholdLines()

        hdg_obj.drawTerrain(0)        

        games.update()
        games.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()