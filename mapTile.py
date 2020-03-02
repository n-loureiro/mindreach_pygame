import pygame 
import math

class MapTile(pygame.sprite.Sprite):
    def __init__(self, pos_in_screen, tile_size):
        super().__init__()
        

        pos_in_screen_x = pos_in_screen[0]
        pos_in_screen_y = pos_in_screen[1]
        self.tile_size_x = tile_size[0]
        self.tile_size_y = tile_size[1]

        self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.background_image = pygame.image.load("images/champ.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, 
                                                (int(self.tile_size_x), int(self.tile_size_y)))
        self.blit_map()
        self.rect = self.image.get_rect()
        self.rect.center = ((pos_in_screen_x)+self.tile_size_x/2, 
                            (pos_in_screen_y)+self.tile_size_y/2)

        self.waypoint_list = []
        
        self.drone_flag = 0
        
        self.position = pygame.Vector2(self.tile_size_x/2, self.tile_size_y/2)
        self.direction = pygame.Vector2(1,0)
        self.speed = 0#math.sqrt(math.pow(self.tile_size_x,2) + math.pow(self.tile_size_y,2))/30
        self.angle = 0
        self.angle_speed = 0

        self.BMI_help = 1

        self.next_target = pygame.Vector2(0,0)
        self.next_target_direction = pygame.Vector2(0,0)

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
            self.direction = pygame.Vector2(1,0)

        self.initial_vec = self.position
        self.image.blit(self.drone, self.rect_drone)
        self.drone_flag = 1
        self.speed = 4#math.sqrt(math.pow(self.tile_size_x,2) + math.pow(self.tile_size_y,2))/30
        self.angle = 0
        self.angle_speed = 0

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

        if self.drone_flag:
            if self.angle_speed != 0:
                # Rotate the direction vector and then the image.
                self.direction.rotate_ip(self.angle_speed)
                if self.BMI_help:
                    self.next_target_direction.x = self.next_target.x - self.position.x
                    self.next_target_direction.y = self.next_target.y - self.position.y
                    if self.next_target_direction != (0,0):
                        self.next_target_direction = self.next_target_direction.normalize()
                        angle_BMI =   (180/math.pi) * math.atan2(self.next_target_direction.x, self.next_target_direction.y)
                    self.direction = self.direction *(1-self.BMI_help) + self.BMI_help*self.next_target_direction
                    self.angle = self.angle_speed*(1-self.BMI_help) + self.BMI_help*angle_BMI
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
                
                if distance.magnitude() <= self.tile_size_x/200:
                    self.set_next_target()