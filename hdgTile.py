import pygame 
from math import pi

class HdgTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()

        self.size_x = size_x
        self.size_y = size_y

        self.tile_size_x = size_x/2
        self.tile_size_y = size_y*0.4


        self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.image.fill((17, 218, 255))
        self.rect = self.image.get_rect()#(left=size_x/2, top=size_y*0.6)
        self.rect.center = (size_x/2+self.tile_size_x/2, size_y*0.6+self.tile_size_y/2)


        self.hdg_rot = pygame.Surface((self.tile_size_x*3, self.tile_size_y*3))
        self.rect_hdg_rot = self.hdg_rot.get_rect()#(left=size_x/2, top=size_y*0.6)
        self.rect_hdg_rot.center = (int(self.tile_size_x*0.5), int(self.tile_size_y*0.5)) 
        self.hdg_rot.fill((100, 87, 35))
       

        HDG_size = self.rect_hdg_rot.size

        self.BG_IMAGE = pygame.image.load("hdg_bg.png").convert()
        BG_size = self.BG_IMAGE.get_rect().size

        self.BG_IMAGE = self.BG_IMAGE.subsurface((abs(HDG_size[0]/2-BG_size[0]/2),abs(HDG_size[1]/2-BG_size[1]/2),HDG_size[0],HDG_size[1]))

        #self.background_image = pygame.transform.scale(self.background_image, (int(self.tile_size_x*2), int(self.tile_size_y*2)))
        self.hdg_rot.blit(self.BG_IMAGE, [0,0])#[-int(self.tile_size_x/2),-int(self.tile_size_y/2)])
        

        # self.terrain_orig = pygame.Surface((self.tile_size_x*2, self.tile_size_y*2), pygame.SRCALPHA)
        # self.terrain = self.terrain_orig
        # self.rect_terrain = self.terrain.get_rect()
        # self.rect_terrain.midtop = (self.tile_size_x/2, self.tile_size_y/2)
        # self.terrain.fill((133, 87, 35))

        # self.sky_orig = pygame.Surface((self.tile_size_x*2, self.tile_size_y*2), pygame.SRCALPHA)
        # self.sky = self.sky_orig
        # self.rect_sky = self.sky.get_rect()
        # self.rect_sky.midbottom = (self.tile_size_x/2, self.tile_size_y/2)
        # self.sky.fill((200, 218, 255))



        # print(self.rect_terrain)
        # print(self.rect_sky)

        # self.hdg_rot.blit(self.terrain, self.rect_terrain)
        # self.hdg_rot.blit(self.sky, self.rect_sky)
        self.image.blit(self.hdg_rot, self.rect_hdg_rot)



        #self.image_orig = pygame.Surface((self.tile_size_x, self.tile_size_y), pygame.SRCALPHA)
        #self.image_orig.set_colorkey((17, 218, 255))
        #self.image_orig.fill((17, 218, 255))



        #self.background_image = pygame.image.load("hdg_bg.png").convert()
        #self.background_image = pygame.transform.scale(self.background_image, (int(self.tile_size_x*4), int(self.tile_size_y*4)))
        #self.image_orig.blit(self.background_image, [-int(self.tile_size_x*1.5),-int(self.tile_size_y*1.5)])
        
        # self.image = self.image_orig.copy()
        



        # self.rect = self.image.get_rect()#(left=size_x/2, top=size_y*0.6)
        # self.rect.center = (size_x/2+self.tile_size_x/2, size_y*0.6+self.tile_size_y/2)
        # self.canvas = canvas
        #self.canvas.blit(self.image, (0,0))


    def drawTerrain(self, tilt):
        #self.image.fill((17, 218, 255))
        #self.rot_center(tilt)

        # if hasattr(self,'rotated_image'):
        #     self.canvas.blit(self.rotated_image, self.rect)



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

        old_center = self.rect_hdg_rot.center
        self.rotated_image = pygame.transform.rotozoom(self.hdg_rot, angle,1)
        #self.image = rotated_image
        #self.image.set_colorkey((17, 218, 255))
        #print(self.image_orig)
        


        self.rect_hdg_rot = self.rotated_image.get_rect()
        self.rect_hdg_rot.center = old_center
        #self.image.fill((255, 0, 0))
        #self.hdg_rot.blit(self.terrain, self.rect_terrain)
        #self.hdg_rot.blit(self.sky, self.rect_sky)
        self.image.blit(self.rotated_image, self.rect_hdg_rot)
        #self.image.fill((int(255-(angle+1)//9), 0, int(angle//9)))
        #self.image.blit(rotated_image, self.rect)
