import pygame 
from math import pi

class HdgTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()

        print('here')
        self.size_x = size_x
        self.size_y = size_y

        self.tile_size_x = size_x/2
        self.tile_size_y = size_y*0.4


        # self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        # self.image.fill((17, 218, 255))


        # self.terrain = pygame.Surface((self.tile_size_x*2, self.tile_size_y*2), pygame.SRCALPHA)




        self.image_orig = pygame.Surface((self.tile_size_x, self.tile_size_y), pygame.SRCALPHA)
        #self.image_orig.set_colorkey((17, 218, 255))
        self.image_orig.fill((17, 218, 255))



        #self.background_image = pygame.image.load("hdg_bg.png").convert()
        #self.background_image = pygame.transform.scale(self.background_image, (int(self.tile_size_x*4), int(self.tile_size_y*4)))
        #self.image_orig.blit(self.background_image, [-int(self.tile_size_x*1.5),-int(self.tile_size_y*1.5)])
        
        self.image = self.image_orig.copy()
        



        self.rect = self.image.get_rect()#(left=size_x/2, top=size_y*0.6)
        self.rect.center = (size_x/2+self.tile_size_x/2, size_y*0.6+self.tile_size_y/2)
        self.canvas = canvas
        #self.canvas.blit(self.image, (0,0))


    def drawTerrain(self, tilt):

        if hasattr(self,'rotated_image'):
            self.canvas.blit(self.rotated_image, self.rect)



        #self.canvas.blit(self.image, self.rect)
        #self.image.fill((255, 0, 0))
        #wrect = pygame.Rect(0, self.tile_size_y/2, self.tile_size_x, self.tile_size_y/2)
        #pygame.draw.rect(self.image, (133, 87, 35), wrect)


        # for line_i in range(5):
        #     wrect = pygame.Rect(self.tile_size_x*0.35, self.tile_size_y*0.2+(line_i)*self.tile_size_y*0.15, self.tile_size_x*0.3, self.tile_size_y/150)
        #     pygame.draw.rect(self.image, (255,255,255), wrect)
        # for line_i in range(5):
        #     wrect = pygame.Rect(self.tile_size_x*0.4, self.tile_size_y*0.275+(line_i)*self.tile_size_y*0.15, self.tile_size_x*0.2, self.tile_size_y/150)
        #     pygame.draw.rect(self.image, (255,255,255), wrect)

        # arc = pygame.Surface((int(self.tile_size_x*0.4), int(self.tile_size_y*0.4)))
        # pygame.draw.arc(self.image, (255,255,255), (arc.get_rect().move(self.tile_size_x*0.3,self.tile_size_y/10)), 0, pi, int(self.tile_size_y/80))
        pass

    def rot_center(self, angle):

        old_center = self.rect.center
        self.rotated_image = pygame.transform.rotate(self.image_orig, angle)
        #self.image = rotated_image
        #self.image.set_colorkey((17, 218, 255))
        #print(self.image_orig)
        


        self.rect = self.rotated_image.get_rect()
        self.rect.center = old_center
        #self.image.fill((255, 0, 0))
        self.canvas.blit(self.rotated_image, self.rect)
        #self.image.fill((int(255-(angle+1)//9), 0, int(angle//9)))
        #self.image.blit(rotated_image, self.rect)
