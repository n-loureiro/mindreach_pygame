import pygame 
from math import pi

class HdgTile(pygame.sprite.Sprite):
    def __init__(self, pos_in_screen, tile_size):
        super().__init__()

        pos_in_screen_x = pos_in_screen[0]
        pos_in_screen_y = pos_in_screen[1]
        tile_size_x = tile_size[0]
        tile_size_y = tile_size[1]
        self.tile_size_x = tile_size[0]
        self.tile_size_y = tile_size[1]



        self.image = pygame.Surface((tile_size_x, tile_size_y))
        self.image.fill((17, 218, 255))
        self.rect = self.image.get_rect()#(left=size_x/2, top=size_y*0.6)
        self.rect.center = ((pos_in_screen_x)+tile_size_x/2, 
                            (pos_in_screen_y)+tile_size_y/2)

        self.hdg_rot = pygame.Surface((tile_size_x*3, tile_size_y*3))
        self.rect_hdg_rot = self.hdg_rot.get_rect()#(left=size_x/2, top=size_y*0.6)
        self.rect_hdg_rot.center = (int(tile_size_x*0.5), int(tile_size_y*0.5)) 
        self.hdg_rot.fill((100, 87, 35))
       
        HDG_size = self.rect_hdg_rot.size

        self.BG_IMAGE = pygame.image.load("images/hdg_bg2.png").convert_alpha()
        BG_size = self.BG_IMAGE.get_rect().size

        self.BG_IMAGE = self.BG_IMAGE.subsurface((abs(HDG_size[0]/2-BG_size[0]/2),abs(HDG_size[1]/2-BG_size[1]/2),HDG_size[0],HDG_size[1]))

        self.hdg_rot.blit(self.BG_IMAGE, [0,0])
        self.image.blit(self.hdg_rot, self.rect_hdg_rot)



    def drawTerrain(self, tilt):
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
        self.rotated_image = pygame.transform.rotate(self.hdg_rot, angle)

        self.rect_hdg_rot = self.rotated_image.get_rect()
        self.rect_hdg_rot.center = old_center
        self.image.blit(self.rotated_image, self.rect_hdg_rot)
        pygame.draw.polygon(self.image, (255,0,0), [[self.tile_size_x*0.48, self.tile_size_y*0.13], 
                                                [self.tile_size_x*0.52, self.tile_size_y*0.13],
                                                [self.tile_size_x*0.5, self.tile_size_y*0.16]], 0)
        pygame.draw.polygon(self.image, (255,0,0), [[self.tile_size_x*0.48, self.tile_size_y*0.23], 
                                                [self.tile_size_x*0.52, self.tile_size_y*0.23],
                                                [self.tile_size_x*0.5, self.tile_size_y*0.2]], 0)
