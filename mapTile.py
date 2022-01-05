import pygame 
import math
import os
import numpy as np

class MapTile(pygame.sprite.Sprite):
    def __init__(self, pos_in_screen, tile_size):
        super().__init__()
        pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
        self.myfont = pygame.font.SysFont('Impact', 30)        

        pos_in_screen_x = pos_in_screen[0]
        pos_in_screen_y = pos_in_screen[1]
        self.tile_size_x = tile_size[0]
        self.tile_size_y = tile_size[1]

        self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.background_image = pygame.image.load("images/champ.png").convert()
        # self.background_image = self.background_image.subsurface((0, 0, int(self.tile_size_x), int(self.tile_size_y)))

        self.background_image = pygame.transform.scale(self.background_image, 
                                                 (int(self.tile_size_x), int(self.tile_size_y)))
        self.blit_map()
        self.rect = self.image.get_rect()
        self.rect.center = ((pos_in_screen_x)+self.tile_size_x/2, 
                            (pos_in_screen_y)+self.tile_size_y/2)

        self.waypoint_list = []
        
        self.drone_flag = 0
        
        self.position = pygame.Vector2(self.tile_size_x/2, self.tile_size_y/2)
        self.direction = pygame.Vector2(0,0)
        self.speed = 0#math.sqrt(math.pow(self.tile_size_x,2) + math.pow(self.tile_size_y,2))/30
        self.angle = (180/math.pi) * math.atan2(self.direction.x, self.direction.y)

        self.angle_speed = 0

        self.angle_speed_intensity = 20


        self.BMI_help = 0

        self.next_target = pygame.Vector2(0,0)
        self.next_target_direction = pygame.Vector2(0,0)

        self.seagull_sound = pygame.mixer.Sound("sounds/seagull.wav")
        self.correct_sound = pygame.mixer.Sound("sounds/correct_sound.wav")
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
        

        self.flag_explosion = 0
        self.seagull_flag = 0
        self.explosion_flag = 0
        self.explosion_time = pygame.time.get_ticks()

    def set_new_waypoint(self, pos):
        self.blit_map()
        self.pos=pos
        if pos[0]< self.tile_size_x and pos[1]< self.tile_size_y:
            self.waypoint_list.append(pos)
        if len(self.waypoint_list) == 1:
            self.next_target = pygame.Vector2(pos)
        self.blit_waypoints()
        

    def blit_waypoints(self):

        if len(self.waypoint_list)>1: #if more than 1 point, connect them
            pygame.draw.polygon(self.image, (0,0,225), self.waypoint_list, 4)
        for wp in self.waypoint_list:
            if wp == self.next_target:
                pygame.draw.circle(self.image, (30,250,10), wp, 10)
                pygame.draw.circle(self.image, (30,250,10), wp, 20, 5)
            else:
                pygame.draw.circle(self.image, (250,10,0), wp, 5)

    def clear_waypoints(self):
        self.blit_map()
        self.waypoint_list = []
        self.drone_flag = 0
        #self.create_drone()

    def blit_map(self):
        self.image.blit(self.background_image, [0,0])

    def create_drone(self):

        self.drone_orig = pygame.image.load("images/xwing.png").convert_alpha()
        self.drone_orig = pygame.transform.scale(self.drone_orig, (int(self.tile_size_x/20), int(self.tile_size_x/20)))
        ## dron.png -> 4deg
        ## falcon.png -> 95deg
        self.drone_orig = pygame.transform.rotozoom(self.drone_orig, 185 ,1)
        self.drone = self.drone_orig

        self.rect_drone = self.drone.get_rect()

        if len(self.waypoint_list)==1: 
            self.position.x = self.waypoint_list[0][0] + 50
            self.position.y = self.waypoint_list[0][1] - 50
            self.direction = pygame.Vector2(1,0)
        elif len(self.waypoint_list)>1:
            print('here drone 2')
            self.position.x = self.waypoint_list[0][0] + 50
            self.position.y = self.waypoint_list[0][1] - 50
            self.direction = pygame.Vector2(self.waypoint_list[1][0]-self.waypoint_list[0][0],
                                            self.waypoint_list[1][1]-self.waypoint_list[0][1]).normalize()
        else:
            self.position = pygame.Vector2(self.tile_size_x/2, self.tile_size_y/2)
            self.direction = pygame.Vector2(0,1)

        self.initial_vec = self.position
        
        self.drone_flag = 1
        self.speed = 4#math.sqrt(math.pow(self.tile_size_x,2) + math.pow(self.tile_size_y,2))/30
        self.angle = (180/math.pi) * math.atan2(self.direction.x, self.direction.y)

        self.drone = pygame.transform.rotate(self.drone_orig, self.angle)
        self.image.blit(self.drone, self.rect_drone)
        self.angle_speed = 0

    def create_seagull(self):
        self.seagull_sound.play()
        self.seagull = pygame.image.load("images/seagull.png").convert_alpha()
        self.seagull = pygame.transform.scale(self.seagull, (120, 64))
        
        if np.random.random() > 0.5:
            self.position_seagull = pygame.Vector2(-10, np.random.random()*self.tile_size_y/2+self.tile_size_y/4)
            self.direction_seagull = pygame.Vector2(1,np.random.random()*0.4)
        else:
            self.position_seagull = pygame.Vector2(self.tile_size_x+10, np.random.random()*self.tile_size_y/2+self.tile_size_y/4)
            self.direction_seagull = pygame.Vector2(-1,np.random.random()*.8)
            self.seagull = pygame.transform.flip(self.seagull,1,0)
        
        self.rect_seagull = self.seagull.get_rect()
        self.speed_seagull = 10
        #self.angle_seagull = (180/math.pi) * math.atan2(self.direction_seagull.x, self.direction_seagull.y)
        #self.seagull = pygame.transform.rotate(self.seagull, self.angle_seagull)
        self.image.blit(self.seagull, self.rect_seagull)
        self.seagull_flag = 1

    def create_explosion(self):
        self.explosion_sound.play()
        self.explosion = pygame.image.load("images/explosion.png").convert_alpha()
        self.explosion = pygame.transform.scale(self.explosion, (400, 400))
        self.rect_explosion = self.rect_seagull.move(-200,-200)
        self.image.blit(self.explosion, self.rect_explosion)

        self.flag_explosion = 1


    def set_next_target(self):
        print('here set target')
        if len(self.waypoint_list)>1:
            idx_in_list = self.waypoint_list.index(self.next_target)
            if idx_in_list < len(self.waypoint_list) -1:
                self.next_target[:] = self.waypoint_list[idx_in_list + 1]
            else:
                self.next_target[:] = self.waypoint_list[0]
        elif len(self.waypoint_list) == 1:
            self.next_target[:] = self.waypoint_list[0]
        else:
            self.next_target = pygame.Vector2(0,0)

    def update(self):

        self.blit_map()
        self.blit_waypoints()

        textsurface = self.myfont.render('BMI help: ' + "{:.2f}".format(self.BMI_help), False, (255, 0, 0))
        self.image.blit(textsurface, (self.tile_size_x*0.05, self.tile_size_y*.9))
        textsurface = self.myfont.render('turn rate: ' + "{:.2f}".format(self.angle_speed_intensity), False, (255, 0, 0))
        self.image.blit(textsurface, (self.tile_size_x*0.45, self.tile_size_y*.9))
        textsurface = self.myfont.render('speed: ' + "{:.2f}".format(self.speed), False, (255, 0, 0))
        self.image.blit(textsurface, (self.tile_size_x*0.8, self.tile_size_y*.9))

        if self.drone_flag:
            if self.angle_speed != 0:
                # Rotate the direction vector and then the image.
                self.direction.rotate_ip(-self.angle_speed)
                if self.BMI_help>0.05:
                    self.next_target_direction.x = self.next_target.x - self.position.x
                    self.next_target_direction.y = self.next_target.y - self.position.y
                    if self.next_target_direction != (0,0):
                        self.next_target_direction = self.next_target_direction.normalize()
                        angle_BMI =   (180/math.pi) * math.atan2(self.next_target_direction.x, self.next_target_direction.y)
                    self.direction = self.direction *(1-self.BMI_help) + self.BMI_help*self.next_target_direction
                    self.angle = (self.angle+self.angle_speed)*(1-self.BMI_help) + self.BMI_help*angle_BMI
                else:
                    self.angle += self.angle_speed
                self.drone = pygame.transform.rotate(self.drone_orig, self.angle)
                self.rect_drone = self.drone.get_rect()
            # Update the position vector and the rect.
            self.position += self.direction * self.speed
            self.rect_drone.center = self.position
            #self.drone.fill((255,0,0))
            self.image.blit(self.drone, self.rect_drone)
            #pygame.draw.polygon(self.image, (0,255,0), [self.position, self.next_target], 4)
            if self.next_target != (0,0):

                distance = self.position - self.next_target
                
                if distance.magnitude() <= 40:
                    self.correct_sound.play()
                    self.set_next_target()

        # if self.seagull_flag:
        #     self.image.blit(self.seagull, self.rect_seagull)
        #     self.position_seagull += self.direction_seagull * self.speed_seagull
        #     self.rect_seagull.center = self.position_seagull
            
        #     if (self.position_seagull.x > self.tile_size_x +20) or (self.position_seagull.x < -20) or \
        #             (self.position_seagull.y > self.tile_size_y + 20) or (self.position_seagull.y < -20):
        #         self.seagull_flag = 0


        #     if self.drone_flag:
        #         distance = self.position - self.position_seagull
                
        #         if distance.magnitude() <= 50:
        #             print('distance')
        #             self.create_explosion()
        #             self.drone_flag = 0
        #             self.seagull_flag = 0
        #             self.explosion_time = pygame.time.get_ticks()
        # else:
        #     self.create_seagull()

        # if self.explosion_flag:
        #     if pygame.time.get_ticks() - self.explosion_time > 500:
        #         self.explosion_time = 0
