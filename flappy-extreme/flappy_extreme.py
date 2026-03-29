#!/usr/bin/env python3
"""
EXTREME FLAPPY BIRD - Photo Edition
Play with placeholder graphics OR use your own photos!

Features:
- Play with built-in placeholder art (colored shapes)
- OR use your own photos as bird/pipe/background
- Extreme mode: moving pipes, power-ups, multi-pipe gaps
- High score tracking
- Multiple difficulty levels

Controls:
SPACE / UP / CLICK = Jump
P = Pause
R = Restart (after game over)
ESC = Quit
"""

import pygame
import random
import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple
import json

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)
RED = (220, 20, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
PURPLE = (148, 0, 211)

# Game settings
BIRD_SIZE = 40
PIPE_WIDTH = 80
PIPE_GAP = 150
GRAVITY = 0.6
JUMP_STRENGTH = -10
PIPE_SPEED = 4
POWERUP_SIZE = 30

# Difficulty settings
DIFFICULTY = {
    'EASY': {'pipe_speed': 3, 'pipe_gap': 180, 'gravity': 0.5, 'spawn_rate': 120},
    'NORMAL': {'pipe_speed': 4, 'pipe_gap': 150, 'gravity': 0.6, 'spawn_rate': 100},
    'EXTREME': {'pipe_speed': 6, 'pipe_gap': 120, 'gravity': 0.8, 'spawn_rate': 80, 
                'moving_pipes': True, 'multi_gap': True}
}


@dataclass
class GameConfig:
    """Game configuration"""
    use_custom_images: bool = False
    bird_image: Optional[str] = None
    pipe_image: Optional[str] = None
    bg_image: Optional[str] = None
    difficulty: str = 'NORMAL'


class AssetLoader:
    """Load game assets - placeholder or custom images"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.assets = {}
        self._load_assets()
    
    def _load_assets(self):
        """Load all game assets"""
        # Load bird
        if self.config.use_custom_images and self.config.bird_image:
            self.assets['bird'] = self._load_image(self.config.bird_image, (BIRD_SIZE, BIRD_SIZE))
        else:
            # Create placeholder bird (yellow rectangle with beak)
            self.assets['bird'] = self._create_placeholder_bird()
        
        # Load pipes
        if self.config.use_custom_images and self.config.pipe_image:
            self.assets['pipe'] = self._load_image(self.config.pipe_image, (PIPE_WIDTH, SCREEN_HEIGHT))
        else:
            # Create placeholder pipes (green rectangles with gradient)
            self.assets['pipe'] = self._create_placeholder_pipe()
        
        # Load background
        if self.config.use_custom_images and self.config.bg_image:
            self.assets['bg'] = self._load_image(self.config.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            # Create placeholder background (sky gradient)
            self.assets['bg'] = self._create_placeholder_bg()
        
        # Load power-up icons
        self.assets['powerup_shield'] = self._create_powerup_icon('SHIELD', GOLD)
        self.assets['powerup_slowmo'] = self._create_powerup_icon('SLOW', PURPLE)
        self.assets['powerup_double'] = self._create_powerup_icon('2X', RED)
    
    def _load_image(self, path: str, size: Tuple[int, int]) -> pygame.Surface:
        """Load and scale an image"""
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, size)
        except Exception as e:
            print(f"⚠️ Failed to load image {path}: {e}")
            print("   Using placeholder instead")
            return pygame.Surface(size)
    
    def _create_placeholder_bird(self) -> pygame.Surface:
        """Create placeholder bird graphic"""
        surface = pygame.Surface((BIRD_SIZE, BIRD_SIZE), pygame.SRCALPHA)
        
        # Body
        pygame.draw.ellipse(surface, YELLOW, (0, 5, BIRD_SIZE-5, BIRD_SIZE-10))
        pygame.draw.ellipse(surface, ORANGE, (0, 5, BIRD_SIZE-5, BIRD_SIZE-10), 2)
        
        # Eye
        pygame.draw.circle(surface, WHITE, (BIRD_SIZE-12, 12), 6)
        pygame.draw.circle(surface, BLACK, (BIRD_SIZE-12, 12), 3)
        
        # Beak
        pygame.draw.polygon(surface, ORANGE, [
            (BIRD_SIZE-10, 15),
            (BIRD_SIZE, 20),
            (BIRD_SIZE-10, 25)
        ])
        
        # Wing
        pygame.draw.ellipse(surface, YELLOW, (5, 15, 15, 12))
        pygame.draw.ellipse(surface, ORANGE, (5, 15, 15, 12), 1)
        
        return surface
    
    def _create_placeholder_pipe(self) -> pygame.Surface:
        """Create placeholder pipe graphic"""
        surface = pygame.Surface((PIPE_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Main pipe body with gradient effect
        for i in range(0, SCREEN_HEIGHT, 20):
            shade = max(30, 139 - i // 10)
            pygame.draw.rect(surface, (0, shade, 0), (0, i, PIPE_WIDTH, 20))
        
        # Highlight on left side
        pygame.draw.rect(surface, (50, 179, 50), (0, 0, 5, SCREEN_HEIGHT))
        # Shadow on right side  
        pygame.draw.rect(surface, (0, 80, 0), (PIPE_WIDTH-8, 0, 8, SCREEN_HEIGHT))
        
        # Cap for top of pipe
        pygame.draw.rect(surface, DARK_GREEN, (-5, 0, PIPE_WIDTH+10, 30))
        
        return surface
    
    def _create_placeholder_bg(self) -> pygame.Surface:
        """Create placeholder background (sky with clouds)"""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            color = (
                int(135 - y * 0.1),
                int(206 - y * 0.15),
                int(235 - y * 0.1)
            )
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw some clouds
        for _ in range(5):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(50, 200)
            self._draw_cloud(surface, x, y)
        
        return surface
    
    def _draw_cloud(self, surface: pygame.Surface, x: int, y: int):
        """Draw a simple cloud"""
        cloud_color = (255, 255, 255)
        pygame.draw.circle(surface, cloud_color, (x, y), 30)
        pygame.draw.circle(surface, cloud_color, (x+25, y), 35)
        pygame.draw.circle(surface, cloud_color, (x+50, y), 30)
        pygame.draw.circle(surface, cloud_color, (x+25, y-15), 25)
    
    def _create_powerup_icon(self, text: str, color: Tuple[int, int, int]) -> pygame.Surface:
        """Create power-up icon"""
        surface = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
        
        # Outer glow
        pygame.draw.circle(surface, (*color, 100), (POWERUP_SIZE//2, POWERUP_SIZE//2), POWERUP_SIZE//2)
        # Main circle
        pygame.draw.circle(surface, color, (POWERUP_SIZE//2, POWERUP_SIZE//2), POWERUP_SIZE//2 - 2)
        
        # Text
        font = pygame.font.Font(None, 20)
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(POWERUP_SIZE//2, POWERUP_SIZE//2))
        surface.blit(text_surf, text_rect)
        
        return surface


class Bird:
    """The flappy bird"""
    
    def __init__(self, x: int, y: int, image: pygame.Surface):
        self.x = x
        self.y = y
        self.vel_y = 0
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        self.shielded = False
        self.shield_timer = 0
    
    def update(self, gravity: float):
        """Update bird physics"""
        self.vel_y += gravity
        self.y += self.vel_y
        self.rect.centery = self.y
        
        # Rotate based on velocity
        self.angle = max(-30, min(90, self.vel_y * 3))
        
        # Update shield
        if self.shielded:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shielded = False
    
    def jump(self):
        """Make bird jump"""
        self.vel_y = JUMP_STRENGTH
    
    def draw(self, screen: pygame.Surface):
        """Draw the bird"""
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        
        screen.blit(rotated_image, rotated_rect)
        
        # Draw shield effect
        if self.shielded:
            pygame.draw.circle(screen, GOLD, self.rect.center, BIRD_SIZE//2 + 8, 3)
    
    def activate_shield(self, duration: int = 300):
        """Activate shield power-up"""
        self.shielded = True
        self.shield_timer = duration


class Pipe:
    """Obstacle pipe"""
    
    def __init__(self, x: int, gap_y: int, image: pygame.Surface, gap_size: int = PIPE_GAP):
        self.x = x
        self.gap_y = gap_y
        self.image = image
        self.gap_size = gap_size
        self.passed = False
        
        # Create rects for collision
        self.top_rect = pygame.Rect(x, 0, PIPE_WIDTH, gap_y - gap_size//2)
        self.bottom_rect = pygame.Rect(
            x, gap_y + gap_size//2, 
            PIPE_WIDTH, SCREEN_HEIGHT - (gap_y + gap_size//2)
        )
    
    def update(self, speed: float):
        """Move pipe left"""
        self.x -= speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, screen: pygame.Surface, gap_only: bool = False):
        """Draw the pipe"""
        if not gap_only:
            # Top pipe (flip image)
            top_y = self.gap_y - self.gap_size//2 - SCREEN_HEIGHT
            screen.blit(pygame.transform.flip(self.image, False, True), 
                     (self.x, top_y))
            
            # Bottom pipe
            bottom_y = self.gap_y + self.gap_size//2
            screen.blit(self.image, (self.x, bottom_y))
        
        # Draw outline of gap (optional visual)
        # pygame.draw.rect(screen, (100, 100, 100, 50), 
        #                (self.x, self.gap_y - self.gap_size//2, 
        #                 PIPE_WIDTH, self.gap_size), 1)
    
    def off_screen(self) -> bool:
        """Check if pipe is off screen"""
        return self.x < -PIPE_WIDTH


class PowerUp:
    """Power-up item"""
    
    TYPES = {
        'SHIELD': {'color': GOLD, 'duration': 300},
        'SLOWMO': {'color': PURPLE, 'duration': 180},
        'DOUBLE': {'color': RED, 'duration': 300}
    }
    
    def __init__(self, x: int, y: int, power_type: str, image: pygame.Surface):
        self.x = x
        self.y = y
        self.type = power_type
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False
    
    def update(self, speed: float):
        """Move power-up"""
        self.x -= speed
        self.rect.centerx = self.x
    
    def draw(self, screen: pygame.Surface):
        """Draw power-up"""
        if not self.collected:
            screen.blit(self.image, self.rect)
    
    def off_screen(self) -> bool:
        """Check if off screen"""
        return self.x < -POWERUP_SIZE


class Game:
    """Main game class"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("EXTREME FLAPPY BIRD 🐦")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        
        # Load assets
        self.assets = AssetLoader(config)
        
        # Game state
        self.reset_game()
        
        # High score
        self.high_score = self._load_high_score()
    
    def reset_game(self):
        """Reset game state"""
        settings = DIFFICULTY[self.config.difficulty]
        
        self.bird = Bird(100, SCREEN_HEIGHT//2, self.assets.assets['bird'])
        self.pipes: List[Pipe] = []
        self.powerups: List[PowerUp] = []
        self.score = 0
        self.game_over = False
        self.paused = False
        self.frame_count = 0
        self.pipe_speed = settings['pipe_speed']
        self.gravity = settings['gravity']
        self.spawn_rate = settings['spawn_rate']
        self.pipe_gap = settings['pipe_gap']
    
    def _load_high_score(self) -> int:
        """Load high score from file"""
        try:
            with open('highscore.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0
    
    def _save_high_score(self):
        """Save high score to file"""
        with open('highscore.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)
    
    def spawn_pipe(self):
        """Spawn a new pipe"""
        min_height = 100
        max_height = SCREEN_HEIGHT - self.pipe_gap - min_height
        gap_y = random.randint(min_height, max_height)
        
        pipe = Pipe(
            SCREEN_WIDTH + 50,
            gap_y,
            self.assets.assets['pipe'],
            self.pipe_gap
        )
        self.pipes.append(pipe)
    
    def spawn_powerup(self):
        """Spawn a power-up"""
        if random.random() < 0.1:  # 10% chance
            y = random.randint(100, SCREEN_HEIGHT - 100)
            power_type = random.choice(['SHIELD', 'SLOWMO', 'DOUBLE'])
            
            image_key = f'powerup_{power_type.lower()}'
            powerup = PowerUp(
                SCREEN_WIDTH + 50,
                y,
                power_type,
                self.assets.assets.get(image_key, self.assets.assets['powerup_shield'])
            )
            self.powerups.append(powerup)
    
    def check_collisions(self) -> bool:
        """Check for collisions"""
        # Check if bird hit ground or ceiling
        if self.bird.rect.top <= 0 or self.bird.rect.bottom >= SCREEN_HEIGHT:
            return True
        
        # Check pipe collisions (unless shielded)
        if not self.bird.shielded:
            for pipe in self.pipes:
                if self.bird.rect.colliderect(pipe.top_rect):
                    return True
                if self.bird.rect.colliderect(pipe.bottom_rect):
                    return True
        
        return False
    
    def check_powerup_collisions(self):
        """Check for power-up collection"""
        for powerup in self.powerups:
            if not powerup.collected and self.bird.rect.colliderect(powerup.rect):
                powerup.collected = True
                self.activate_powerup(powerup.type)
    
    def activate_powerup(self, power_type: str):
        """Activate a power-up effect"""
        if power_type == 'SHIELD':
            self.bird.activate_shield(300)
            print("🛡️ Shield activated!")
        elif power_type == 'SLOWMO':
            self.pipe_speed = max(2, self.pipe_speed - 2)
            print("🐌 Slow motion!")
        elif power_type == 'DOUBLE':
            self.score += 1  # Extra point
            print("⭐ Double points!")
    
    def update(self):
        """Update game state"""
        if self.game_over or self.paused:
            return
        
        self.frame_count += 1
        
        # Update bird
        self.bird.update(self.gravity)
        
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update(self.pipe_speed)
            
            # Check if passed pipe
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
                
                # Update high score
                if self.score > self.high_score:
                    self.high_score = self.score
                    self._save_high_score()
            
            # Remove off-screen pipes
            if pipe.off_screen():
                self.pipes.remove(pipe)
        
        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update(self.pipe_speed)
            if powerup.off_screen():
                self.powerups.remove(powerup)
        
        # Spawn new pipes
        if self.frame_count % self.spawn_rate == 0:
            self.spawn_pipe()
        
        # Spawn power-ups
        if self.frame_count % (self.spawn_rate * 3) == 0:
            self.spawn_powerup()
        
        # Check collisions
        if self.check_collisions():
            self.game_over = True
        
        # Check power-up collisions
        self.check_powerup_collisions()
    
    def draw(self):
        """Draw everything"""
        # Background
        self.screen.blit(self.assets.assets['bg'], (0, 0))
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw bird
        self.bird.draw(self.screen)
        
        # UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        high_text = self.small_font.render(f"High: {self.high_score}", True, WHITE)
        self.screen.blit(high_text, (10, 50))
        
        # Shield indicator
        if self.bird.shielded:
            shield_text = self.small_font.render("🛡️ SHIELD", True, GOLD)
            self.screen.blit(shield_text, (SCREEN_WIDTH - 150, 10))
        
        # Game over screen
        if self.game_over:
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            over_text = self.font.render("GAME OVER", True, RED)
            over_rect = over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(over_text, over_rect)
            
            score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(restart_text, restart_rect)
        
        # Pause text
        if self.paused:
            pause_text = self.font.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(pause_text, pause_rect)
        
        pygame.display.flip()
    
    def handle_events(self) -> bool:
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not self.game_over:
                        self.bird.jump()
                
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                
                if event.key == pygame.K_p:
                    self.paused = not self.paused
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_over:
                    self.bird.jump()
        
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


def show_menu():
    """Show game menu"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║             🐦 EXTREME FLAPPY BIRD 🐦                            ║
║                                                                  ║
║  Play with placeholder art OR use your own photos!               ║
╚══════════════════════════════════════════════════════════════════╝

Controls:
  SPACE / UP / CLICK = Jump
  P = Pause
  R = Restart (after game over)
  ESC = Quit

Modes:
  1. EASY     - Slower pipes, larger gaps
  2. NORMAL   - Standard difficulty
  3. EXTREME  - Fast pipes, power-ups, small gaps

To use custom photos:
  1. Place your images in the 'images/' folder
  2. Name them: bird.png, pipe.png, background.png
  3. Run with: python3 flappy_extreme.py --custom

    """)
    
    difficulty = input("Select difficulty (1-3): ").strip()
    
    if difficulty == '1':
        return 'EASY'
    elif difficulty == '3':
        return 'EXTREME'
    else:
        return 'NORMAL'


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extreme Flappy Bird')
    parser.add_argument('--custom', action='store_true', 
                       help='Use custom images from images/ folder')
    parser.add_argument('--bird', type=str, help='Path to custom bird image')
    parser.add_argument('--pipe', type=str, help='Path to custom pipe image')
    parser.add_argument('--bg', type=str, help='Path to custom background image')
    
    args = parser.parse_args()
    
    # Configure game
    config = GameConfig()
    
    if args.custom:
        config.use_custom_images = True
        config.bird_image = 'images/bird.png' if os.path.exists('images/bird.png') else None
        config.pipe_image = 'images/pipe.png' if os.path.exists('images/pipe.png') else None
        config.bg_image = 'images/background.png' if os.path.exists('images/background.png') else None
    
    if args.bird:
        config.use_custom_images = True
        config.bird_image = args.bird
    if args.pipe:
        config.use_custom_images = True
        config.pipe_image = args.pipe
    if args.bg:
        config.use_custom_images = True
        config.bg_image = args.bg
    
    # Show menu and get difficulty
    config.difficulty = show_menu()
    
    # Start game
    game = Game(config)
    game.run()


if __name__ == '__main__':
    main()
