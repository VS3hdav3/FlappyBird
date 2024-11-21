import neat.population
import neat.stagnation
import pygame
import neat
import os
import pickle
from objects import bird
from objects import pipe
from objects import base
pygame.font.init()

width = 500
height = 800
floor = 730
font = pygame.font.SysFont("PixelifySans-Regular", 50)
draw_lines = True

win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

bird_img = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))), 
        pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))), 
        pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))]
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png")))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bg.png")))

gen = 0

def draw_window(win, birds, pipes, base, score, gen, pipe_index):
    win.blit(bg_img, (0, 0))
    base.draw(win)
    for pipe_obj in pipes:
        pipe_obj.draw(win)
        
    for bird_obj in birds:
        # draw lines from bird to pipe
        if draw_lines:
            try:
                pygame.draw.line(win, (255, 255, 255), (bird_obj.x + bird_obj.img.get_width()/2, bird_obj.y + bird_obj.img.get_height() / 2), (pipes[pipe_index].x + pipes[pipe_index].PIPE_TOP.get_width() / 2, pipes[pipe_index].height), 5)
                pygame.draw.line(win, (255, 255, 255), (bird_obj.x + bird_obj.img.get_width()/2, bird_obj.y + bird_obj.img.get_height() / 2), (pipes[pipe_index].x + pipes[pipe_index].PIPE_BOTTOM.get_width() / 2, pipes[pipe_index].bottom), 5)
            except:
                pass
        # draw bird
        bird_obj.draw(win)
        
    # score
    score_label = font.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (width - score_label.get_width() - 15, 10))
    
    # generations
    score_label = font.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))
    
    # alive
    score_label = font.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))
    
    pygame.display.update()
    
def eval_genomes(genomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    bird_objs = []
    
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        bird_objs.append(bird.Bird(230, 350))
        g.fitness = 0
        ge.append(g)
        
    base_obj = base.Base(730)
    pipe_objs = [pipe.Pipe(700)]  
    score = 0  
    run = True
    
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        #bird_obj.move()
        pipe_index = 0
        if len(bird_objs) > 0:
            if len(pipe_objs) > 1 and bird_objs[0].x > pipe_objs[0].x + pipe_objs[0].PIPE_TOP.get_width():
                pipe_index = 1 
        else:
            run = False
            break
        for x, bird_obj in enumerate(bird_objs):
            bird_obj.move()
            ge[x].fitness += 0.1
            output = nets[x].activate((bird_obj.y, 
                                       abs(bird_obj.y - pipe_objs[pipe_index].height), 
                                       abs(bird_obj.y - pipe_objs[pipe_index].bottom)))
            if output[0] > 0.5:
                bird_obj.jump()
        
        add_pipe = False
        rem = []
        for pipe_obj in pipe_objs:
            for x, bird_obj in enumerate(bird_objs):
                if pipe_obj.collide(bird_obj, win):
                    ge[x].fitness -= 1
                    bird_objs.pop(x)
                    nets.pop(x)
                    ge.pop(x)                    
                if not pipe_obj.passed and pipe_obj.x < bird_obj.x:
                    pipe_obj.passed = True
                    add_pipe = True
            if pipe_obj.x + pipe_obj.PIPE_TOP.get_width() < 0:
                rem.append(pipe_obj)
            pipe_obj.move()
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipe_objs.append(pipe.Pipe(700))
        for r in rem:
            pipe_objs.remove(r)
        for x, bird_obj in enumerate(bird_objs):
            if bird_obj.y + bird_obj.img.get_height() >= 730 or bird_obj.y < 0:
                ge[x].fitness -= 1
                bird_objs.pop(x)
                nets.pop(x)
                ge.pop(x)
        base_obj.move()
        draw_window(win, bird_objs, pipe_objs, base_obj, score, gen, pipe_index)
        
        if score > 50:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                                config_path)
    
    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)
    
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))
    
    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)
    
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
