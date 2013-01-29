#!/usr/bin/python

import math, random, os, sys

import pygame
from pygame.locals import *

class Obstacle (pygame.sprite.Sprite):
    def __init__(self, window, *groups):
        super(Obstacle, self).__init__(groups)
        
        self.window = window
        
        self.bounding_rect = self.window.screen_rect
        
        self.rect = Rect(random.randint(self.bounding_rect.right,self.window.level_length),random.randint(0,self.bounding_rect.height),random.randint(25,300),random.randint(10,100))
        self.image = pygame.surface.Surface(self.rect.size)
        self.image.fill((175,0,75))
        
        self.pos = [self.rect.left, self.rect.top]
        
    def update(self, time):
        self.rect.left = self.pos[0]-self.window.bg_scroll

class Player (pygame.sprite.Sprite):
    def __init__(self, window, *groups):
        super(Player, self).__init__(groups)
        
        self.window = window
        
        self.bounding_rect = self.window.screen_rect
        
        self.image = pygame.surface.Surface((48,24))
        self.image.fill((150,0,215))
        self.rect = Rect(0,0,48,24)
        self.rect.left = 50
        self.rect.centery = self.bounding_rect.centery
        
        self.speed_mult = 1.
        self.gravity = 1.25
        #self.gravity = 0.75
        self.terminal_velocity = 0.5
        self.speed = 0.
        self.direction = 90.
        self.pos = [self.rect.left,self.rect.top]
        
        i = 0
        self.jumping = False
        for key in pygame.key.get_pressed():
            i += 1
            if not i == K_ESCAPE or i == 96:
                if key != 0:
                    self.jumping = True
        self.jump_force = 2.25
        #self.jump_force = 1.75
        self.max_jump_speed = .9
        
        self.trail_length = 0
        self.trail_points = []
        
    def check_start(self):
        if self.window.bg_scroll < self.window.screen_rect.width-98:
            self.speed_mult = 0.5
        else:
            self.image.fill((175,0,200))
            if self.jumping:
                self.image.fill((200,50,225))
            self.speed_mult = 1
        
    def update(self, time, events):
        self.handle_events(time, events)
        self.check_start()
        
        self.speed += self.gravity*time/1000.
        if self.speed > self.terminal_velocity:
            self.speed = self.terminal_velocity
        if self.jumping:
            self.speed -= self.jump_force*time/1000.
            if self.speed < -self.max_jump_speed:
                self.speed = -self.max_jump_speed
        self.pos[1] += self.speed*self.speed_mult
        
        if self.rect.top < self.bounding_rect.top:
            self.pos[1] = self.bounding_rect.top
            self.speed = 0.
        
        if self.rect.bottom > self.bounding_rect.bottom:
            self.pos[1] = self.bounding_rect.bottom-self.rect.height
            self.speed = 0.
        
        self.pos[0] = 50.+(self.window.bg_scroll_add*100.)
        
        if not self.window.game_over:    
            self.rect.topleft = self.pos
        
        self.trail_length = int(50.+(self.window.bg_scroll_add*100.))
        if not self.window.game_over: self.trail_points.append([self.rect.left,self.rect.centery])
        if len(self.trail_points) > self.trail_length:
            self.trail_points.remove(self.trail_points[0])
        i = 0
        for p in self.trail_points:
            p[0] = i
            i += 1
        
        rs = []
        for sprite in self.window.obstacle_group.sprites():
            #rs.append(Rect(sprite.pos[0], sprite.pos[1], sprite.rect.width, sprite.rect.height))
            rs.append(sprite.rect)
        if self.rect.collidelist(rs) != -1 or self.rect.top <= 8 or self.rect.bottom >= self.bounding_rect.height-8:
            self.window.game_over = True
            
    def handle_events(self, time, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key != K_ESCAPE and e.key != 96:
                    self.jumping = True
                    self.image.fill((100,50,255))
            elif e.type == KEYUP:
                if e.key != K_ESCAPE and e.key != 96:
                    self.jumping = False
                    self.image.fill((50,0,215))

class Game (object):
    def __init__(self):
        self.screen_rect = Rect(0,0,1280,720)
        #self.screen_rect = Rect(0,0,1024,512)
        self.screen = pygame.display.set_mode(self.screen_rect.size)
        
        self.clock = pygame.time.Clock()
        self.max_fps = 60
        self.update_frame = True
        self.frames_skipped = 0
        self.max_frameskip = 0
        
        self.show_debug = False
        
        if not os.path.exists("scores"):
            f=file("scores", 'w')
            f.close()
            
        
    def reset(self):
        self.create_sprites()
        
        self.main()
        
    def create_sprites(self):
        self.player_group = pygame.sprite.GroupSingle()
        self.player = Player(self, self.player_group)
        
        self.bg_scroll = 0
        self.obstacle_group = pygame.sprite.Group()
        for i in range(0,self.obstacle_num):
            Obstacle(self, self.obstacle_group)

    def handle_events(self, time, events):
        for e in events:
            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                self.done = True
            elif e.type == KEYDOWN:
                if e.key != K_ESCAPE:
                    if self.game_over:
                        self.reset()
                if e.key == 96:
                    self.show_debug = not self.show_debug
                    print "Toggling debug %i"%int(self.show_debug)

    def iterate(self, time):
        events = pygame.event.get()
        result = self.handle_events(time, events)
        
        self.player_group.update(time, events)
        if not self.game_over:
            if self.bg_scroll >= self.screen_rect.width-98:
                self.bg_scroll_add += 0.0075*time/1000.
                self.bg_scroll += 300*time/1000.
                self.bg_scroll += self.bg_scroll_add
            else:
                self.bg_scroll += 150*time/1000.
        self.obstacle_group.update(time)
        
    def draw_lb(self, x, color):
        lb_text = self.score_font.render("High Scores", 1, color)
        lb_rect = lb_text.get_rect()
        lb_rect.left = x
        lb_rect.top = 50
        self.screen.blit(lb_text, lb_rect.topleft)
        i = 1
        for score in self.lb:
            lb_text = self.score_font.render("%i. %i"%(i,score), 1, color)
            lb_rect = lb_text.get_rect()
            lb_rect.left = x
            lb_rect.top = 50+(40*i)
            self.screen.blit(lb_text, lb_rect.topleft)
            i += 1
        
    def draw(self,time):
        self.screen.fill((40,25,35))
        
        pygame.draw.rect(self.screen, (45,0,50), (-self.bg_scroll,0,self.screen_rect.width,self.screen_rect.height))
        inst_text = self.score_font.render("Press and hold any key", 1, (100,75,150))
        inst_rect = inst_text.get_rect()
        inst_rect.bottom = self.player.rect.top-15
        inst_rect.right = self.screen_rect.width-self.bg_scroll-50
        self.screen.blit(inst_text, inst_rect.topleft)
        diff_text = self.score_font.render("Difficulty: %i%%"%(self.difficulty*100), 1, (100,0,150))
        diff_rect = diff_text.get_rect()
        diff_rect.top = self.player.rect.bottom+15
        diff_rect.right = self.screen_rect.width-self.bg_scroll-50
        self.screen.blit(diff_text, diff_rect.topleft)
        self.draw_lb(self.screen_rect.width-self.bg_scroll+10, (200,100,150))
        
        pygame.draw.line(self.screen, (255,100,150), (self.screen_rect.width-self.bg_scroll,0), (self.screen_rect.width-self.bg_scroll,self.screen_rect.bottom))
        
        if len(self.player.trail_points) > 47:
            pygame.draw.lines(self.screen, (90,0,5), False, self.player.trail_points[:10], 13)
            pygame.draw.lines(self.screen, (90,25,35), False, self.player.trail_points[:20], 7)
            pygame.draw.lines(self.screen, (190,25,35), False, self.player.trail_points[:35], 3)
            pygame.draw.lines(self.screen, (190,25,35), False, self.player.trail_points[45:], 3)
            pygame.draw.lines(self.screen, (255,25,35), False, self.player.trail_points[40:], 1)
        self.player_group.draw(self.screen)
        self.obstacle_group.draw(self.screen)
        pygame.draw.rect(self.screen, (200,0,70), (0,0,self.screen_rect.width,8))
        pygame.draw.rect(self.screen, (200,0,70), (0,self.screen_rect.height-8,self.screen_rect.width,8))
        
        if not self.game_over:
            score = self.bg_scroll-self.screen_rect.width
            if score < 0: score = 0
            score /= 50
            color = (45,00,55)
            if len(self.lb) > 0 and score >= self.lb[0]: color = (245,100,155)
            score_text = self.score_font.render("%i"%score, 1, color)
            score_rect = score_text.get_rect()
            score_rect.centery = self.player.rect.centery
            score_rect.right = self.player.rect.right
            if score > 0:
                self.screen.blit(score_text, score_rect.topleft)
        
        if self.game_over:
            game_over_text = self.title_font.render("Game Over", 1, (255,55,150))
            game_over_rect = game_over_text.get_rect()
            game_over_rect.center = self.screen_rect.center
            self.screen.blit(game_over_text,game_over_rect.topleft)
            score = self.bg_scroll-self.screen_rect.width
            if score < 0: score = 0
            score /= 50
            score_text = self.score_font.render("Score: %i"%(score), 1, (255,100,100))
            score_rect = score_text.get_rect()
            score_rect.centerx = self.screen_rect.centerx
            score_rect.top = game_over_rect.bottom+50
            self.screen.blit(score_text,score_rect.topleft)
            restart_text = self.score_font.render("Press any key to retry, or ESC to exit", 1, (255,255,255))
            restart_rect = restart_text.get_rect()
            restart_rect.centerx = self.screen_rect.centerx
            restart_rect.top = game_over_rect.bottom+75
            self.screen.blit(restart_text,restart_rect.topleft)
            
            if not self.scores_set:
                self.get_scores()
                self.set_scores()
            
            self.draw_lb(game_over_rect.right+150, (255,255,255))
            
        
        if self.show_debug:    
            debug_text = self.debug_font.render("Frametime %i Frames skipped %i Frame drawn %i FPS %i/%i "%(time,self.frames_skipped, self.update_frame,self.clock.get_fps(),self.max_fps), False, (255,255,255))
            self.screen.blit(debug_text, (0,8))
        
        pygame.display.update()
        
    def calculate_frameskip(self, time):
        """This function detects if the game is running faster than the maximum framerate and skips drawing frames if it is. This allows it to continue updating physics and game logic without taking the time to draw every frame.
        """
        # Time allowed per frame is 1000/max_fps
        if time < 1000./self.max_fps:
        
            if self.frames_skipped < self.max_frameskip:
                self.update_frame = False
                self.frames_skipped += 1
                pygame.time.delay(1000./self.max_fps-time)
            else:
                self.update_frame = True
                self.frames_skipped = 0
                
    def get_scores(self):
        self.lb = []
        for line in self.lb_file_read.readlines():
            self.lb.append(int(line.rstrip('/n')))
            
    def set_scores(self):
        if self.bg_scroll >= self.screen_rect.width:
            self.lb.append((self.bg_scroll-self.screen_rect.width)/50)
            self.lb.sort()
            self.lb.reverse()
            self.lb_file_read.close()
            if len(self.lb) > 10:
                self.lb.remove(self.lb[-1])
            lb_file = file("scores", 'w')
            for line in self.lb:
                lb_file.write(str(int(line))+"\n")
            lb_file.close()
            self.lb_file_read = file("scores", 'r')
        
        self.scores_set = True
                
    def load(self):
        pygame.init()
        
        self.title_font = pygame.font.SysFont("courier new", 64)
        self.score_font = pygame.font.SysFont("courier new", 24)
        self.debug_font = pygame.font.SysFont("courier new", 12)
    
        self.difficulty = 50/100. #Percent of obstacles to level length. Recommend between 0.25 and 1.5
        self.level_length = 50000 #In pixels
        self.obstacle_num = int(self.level_length*(self.difficulty/100.))
    
        self.create_sprites()
        self.lb_file_read = file("scores", 'r')
        self.get_scores()

    def main(self):
        self.lb_file_read = file("scores", 'r')
        self.scores_set = False
        self.score = 0
        self.bg_scroll_add = 0
        
        self.game_over = False
        self.done = False
        
        while not self.done:
            time = self.clock.tick()
            self.iterate(time)
            self.calculate_frameskip(time)
            if self.update_frame:
                self.draw(time)
                
    
if __name__ == '__main__':
    game = Game()
    game.load()
    game.main()
