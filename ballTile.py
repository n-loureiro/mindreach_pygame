import pygame 
import numpy as np


class BallTile(pygame.sprite.Sprite):
    def __init__(self, pos_in_screen, tile_size):
        super().__init__()

        pos_in_screen_x = pos_in_screen[0]
        pos_in_screen_y = pos_in_screen[1]
        self.tile_size_x = tile_size[0]
        self.tile_size_y = tile_size[1]

        self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect()
        self.rect.center = ((pos_in_screen_x)+self.tile_size_x/2, 
                            (pos_in_screen_y)+self.tile_size_y/2)

        self.pos_hist_x = [0,10,20,30,
                          40,50,60,70] #in prct of tile_size_x

        self.pos_hist_y = [self.tile_size_y/2]*8

        self.upRange = 1
        self.downRange = -1
        self.upReward = 0.75
        self.downReward = -0.75
        self.upBase = 0.25
        self.downBase = -0.25

    ###Draw Ball and last 5 positions as history
    def drawBallHistory(self, new_pos):
        self.image.fill((200, 200, 200))

        self.pos_hist_y = np.roll(self.pos_hist_y,-1)
        self.pos_hist_y[-1] = self.eeg2pixels(new_pos)

        #Draw history and ball
        for i in range(len(self.pos_hist_x)-1): 

            #convert value of position to pixel in y axis
            pygame.draw.line(self.image, (0,0,255), 
                [self.tile_size_x*self.pos_hist_x[i]/100, self.pos_hist_y[i]], 
                [self.tile_size_x*self.pos_hist_x[i+1]/100, self.pos_hist_y[i+1]], 
                3)
        pygame.draw.circle(self.image, (255,0,0), 
                (int(self.tile_size_x*self.pos_hist_x[-1]/100), int(self.pos_hist_y[-1])), 20)


    def eeg2pixels(self,pos_y):
        return self.tile_size_y/2 - (pos_y * self.tile_size_y ) / (self.upRange - self.downRange)

    ###Draws dashed lines across for thresholds and baseline
    def drawDashedLine(self, left, top, length, width, ink, blank, color, dot):
        wrect = pygame.Rect(left, top, ink, width)
        for i in range(int(length / blank)):
            pygame.draw.rect(self.image, color, wrect)
            wrect.left = wrect.left + blank
        if dot:
            wrect2 = pygame.Rect(left+ink+blank/5, top, ink/6, width)
            for i in range(int(length / blank)):
                pygame.draw.rect(self.image, color, wrect2)
                wrect2.left = wrect2.left + blank

    ###Draws patches when the position is crossed
    def drawPatches(self, y_pos_prcnt, color, alpha, height_prcnt):
        patch = pygame.Surface((self.tile_size_x, height_prcnt))  # the size of your rect
        patch.set_alpha(alpha)                # alpha level
        patch.fill(color)           # this fills the entire surface
        self.image.blit(patch, (0,y_pos_prcnt))    # (0,0) are the top-left coordinates


    ###Draws triangles
    def drawTriangle(self, direction):
        if direction == 'UP':
            #pygame.draw.polygon(screen, BLUE, [[posx[7],pixelThresholds['upReward']-(pixelThresholds['upReward']-pixelThresholds['upRange'])/4], [posx[7] + TriangleBase/2, pixelThresholds['upReward']-(pixelThresholds['upReward']-pixelThresholds['upRange'])/4], [posx[7]+ TriangleBase/2, pixelThresholds['upReward']-(pixelThresholds['upReward']-pixelThresholds['upRange'])/4-TriangleHeight + inity], 0)
            pygame.draw.polygon(screen, RED, [[posx[7], pixelThresholds['upReward']-(pixelThresholds['upReward']-pixelThresholds['upRange'])/10], [posx[7]+TriangleBase, pixelThresholds['upReward']-(pixelThresholds['upReward']-pixelThresholds['upRange'])/10], [posx[7]+TriangleBase/2, pixelThresholds['upReward']-(pixelThresholds['upReward']-pixelThresholds['upRange'])/10-TriangleHeight]], 0)
            #pygame.draw.polygon(screen, RED, [[posx[7], pixelThresholds['upReward']], [posx[7]+TriangleBase, pixelThresholds['upReward']], [posx[7]+TriangleBase/2, pixelThresholds['upReward']-TriangleHeight]], 0)
        elif direction == 'DOWN':
            #pygame.draw.polygon(screen, BLUE, [[posx[7], pixelThresholds['downReward'] + (pixelThresholds['downRange']-pixelThresholds['downReward'])/4], [ posx[7]+ TriangleBase/2, pixelThresholds['downReward'] + (pixelThresholds['downRange']-pixelThresholds['downReward'])/4 + inity], [posx[7] + TriangleBase, pixelThresholds['downReward'] + (pixelThresholds['downRange']-pixelThresholds['downReward'])/4+TriangleHeight + inity]], 0)
            pygame.draw.polygon(screen, BLUE, [[posx[7], pixelThresholds['downReward'] + (pixelThresholds['downRange']-pixelThresholds['downReward'])/10], [posx[7]+TriangleBase, pixelThresholds['downReward'] + (pixelThresholds['downRange']-pixelThresholds['downReward'])/10], [posx[7]+TriangleBase/2, pixelThresholds['downReward'] + (pixelThresholds['downRange']-pixelThresholds['downReward'])/10+TriangleHeight]], 0)

    ###Draw Threshold Lines
    def drawThresholdLines(self):
        self.drawDashedLine(0, self.eeg2pixels(self.downReward), self.tile_size_x+20,4,20,28, (92, 92, 92),False)
        self.drawDashedLine(0, self.eeg2pixels(self.upReward), self.tile_size_x+20,4,20,28, (92, 92, 92),False)
        self.drawDashedLine(0, self.eeg2pixels(self.upBase), self.tile_size_x+20,2,20,40, (120,120,130),True)
        self.drawDashedLine(0, self.eeg2pixels(self.downBase), self.tile_size_x+20,2,20,40, (120,120,130),True)


    def chooseArrow():
        a=[0]*101
        i=1;
        a[0] = random.choice(['1','2'])
        while i < 100:
            a[i]=random.choice(['1','11','111'])
            a[i+1]=random.choice(['2','22','222'])
            i+=2
        arrowList = "".join(a)
