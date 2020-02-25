import pygame 


class BallTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()
        self.tile_size_x = size_x/2
        self.tile_size_y = size_y*0.4

        self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect(left= 0, top=size_y*0.6)
        self.canvas = canvas
        #self.canvas.blit(self.image, (size_x/2,size_y*0.6))

    ###Draw Ball and last 5 positions as history
    def drawBallHistory(self, posx, posy):
        self.image.fill((200, 200, 200))
        #Draw history and ball
        for i in range(6): 
            pygame.draw.line(self.image, (0,0,255), [self.tile_size_x*posx[i]/100, self.tile_size_y*posy[i]/100], [self.tile_size_x*posx[i+1]/100, self.tile_size_y*posy[i+1]/100], 3)
        pygame.draw.circle(self.image, (255,0,0), (int(self.tile_size_x*posx[6]/100), int(self.tile_size_y*posy[6]/100)), 20)

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
        self.drawDashedLine(0, self.tile_size_y*0.1, self.tile_size_x+20,4,20,28, (92, 92, 92),False)
        self.drawDashedLine(0, self.tile_size_y*0.9, self.tile_size_x+20,4,20,28, (92, 92, 92),False)
        self.drawDashedLine(0, self.tile_size_y*0.3, self.tile_size_x+20,2,20,40, (120,120,130),True)
        self.drawDashedLine(0, self.tile_size_y*0.6, self.tile_size_x+20,2,20,40, (120,120,130),True)


    def chooseArrow():
        a=[0]*101
        i=1;
        a[0] = random.choice(['1','2'])
        while i < 100:
            a[i]=random.choice(['1','11','111'])
            a[i+1]=random.choice(['2','22','222'])
            i+=2
        arrowList = "".join(a)

# #background image
# #background_grey= pygame.image.load(codePath+"/python/saturn.jpg").convert()
# background_grey= pygame.image.load("/Users/nunoloureiro/mindreach/software_eeg/cursor_control/codeDir/python/background.png").convert()


# #Graphic Values:
# TriangleBase = 50
# TriangleHeight = 60

# #divide resx position into 12 intervals
# posx = [x*resx/10 for x in range(0,11)]
# posx = [int(i) for i in posx] #get their int because draw.circle function only accepts int


# #posy will be read from TiD but initially it is in the center resy/2
# posy = [resy/2 for x in range(0,7)]

# #Define colours
# BLACK = (  0,   0,   0)
# WHITE = (255, 255, 255)
# BLUE =  (  0,   0, 255)
# GREEN = (  0, 255,   0)
# RED =   (255,   0,   0)
# dGREY = (92, 92, 92)
# lGREY = (120,120,130)
