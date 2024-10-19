import pygame
import random
from collections import deque
from draw_functions import (draw_adventurer, draw_enemy, draw_obstacle, draw_chest, draw_inventory, draw_stats,
                            draw_portal)

# Initialize Pygame
pygame.init()

# Set up the screen
map_size = 10
cell_size = 50
screen_width = (map_size + 2) * cell_size + 200  # Additional space for stats panel
screen_height = (map_size + 2) * cell_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dungeon Crawler")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)  # Color for sword swing
GOLD = (255, 215, 0)
PORTAL_COLOR = (100, 100, 255)  # Color for the portal

# Define inventory properties
inventory = []
selected_item_index = 0
inventory_open = False

current_message = ""
message_timer = 0  # Timer to track how long the message should display

# Define items in chests
item_pool = [
    {"name": "Iron Sword", "attack_bonus": 2, "description": "A sturdy sword with a sharp edge."},
    {"name": "Healing Potion", "healing": 20, "description": "Restores 20 health."},
    {"name": "Steel Shield", "defense_bonus": 3, "description": "A strong shield for defense."}
]

# Player stats
player_stats = {
    "health": 100,
    "attack": 5,
    "defense": 1
}

# Level counter
level = 1
player_position = [1, 1]
player_direction = "down"

# Enemy stats
enemy_stats = {
    "health": 30,
    "attack": 3
}


class Boss:
    """
        Class Boss:
            Represents a boss enemy with higher health and attack than regular enemies.

            Methods
            -------
            __init__(self, position)
                Initializes the Boss with a specified position.

            Move_towards(self, target_position)
                Moves the boss towards the player at a slower pace.

            Attack_player(self, player_stats)
                Attacks the player if the player is adjacent.
    """
    def __init__(self, position):
        self.position = position
        self.health = 100  # Higher health than regular enemies
        self.attack = 8  # Stronger attack than regular enemies
        self.sprite = pygame.transform.scale(spider_sprite, (int(cell_size * 1.5), int(cell_size * 1.5)))  # Larger size
        self.movement_speed = 0.5  # Moves slower than regular enemies

    def move_towards(self, target_position):
        """
        Moves the boss towards the player at a slower pace.
        """
        diff_x = target_position[1] - self.position[1]
        diff_y = target_position[0] - self.position[0]

        move_x = 0
        move_y = 0

        if abs(diff_x) > abs(diff_y):
            move_x = 1 if diff_x > 0 else -1
        else:
            move_y = 1 if diff_y > 0 else -1

        # Move every other turn for slower movement
        if random.random() < self.movement_speed:
            new_pos = [self.position[0] + move_y, self.position[1] + move_x]
            if 1 <= new_pos[0] <= map_size and 1 <= new_pos[1] <= map_size and new_pos != player_position:
                self.position = new_pos

    def attack_player(self, player_stats):
        """
        Attacks the player if adjacent.
        """
        diff_x = abs(player_position[1] - self.position[1])
        diff_y = abs(player_position[0] - self.position[0])

        if diff_x + diff_y == 1:  # Adjacent to the player
            player_stats["health"] -= self.attack
            global current_message, message_timer
            current_message = f"The boss hits you for {self.attack} damage!"
            message_timer = 60


class SpriteLoader:
    """
        class SpriteLoader:
    def __init__(self, file_name, cell_size):
        """
    def __init__(self, file_name, cell_size):
        """
        Initialize the sprite loader with the file name and desired cell size.

        :param file_name: Path to the sprite image file.
        :param cell_size: Tuple (width, height) for scaling the sprite.
        """
        self.file_name = file_name
        self.cell_size = cell_size
        self.sprite = self.load_and_scale()

    def load_and_scale(self):
        """
        Load the sprite from the file and scale it to the desired size.

        :return: Scaled sprite as a pygame.Surface object.
        """
        sprite = pygame.image.load(self.file_name).convert_alpha()
        return pygame.transform.scale(sprite, self.cell_size)


# Define the cell size for scaling
cell_size_tuple = (cell_size, cell_size)

# Load all sprites using the SpriteLoader class
adventurer_sprite = SpriteLoader('adventurer.png', cell_size_tuple).sprite
goblin_sprite = SpriteLoader('goblin.png', cell_size_tuple).sprite
wall_sprite = SpriteLoader('wal.png', cell_size_tuple).sprite
chest_sprite = SpriteLoader('chest.png', cell_size_tuple).sprite
spider_sprite = SpriteLoader('spooder.png', cell_size_tuple).sprite

# Portal position
portal_position = []

# Define global variables for game entities
obstacles = []
enemies = []
chests = []


# Function to check if a path exists using BFS
def is_path_available(start, end, obstacles):
    """
    :param start: Starting point of the pathfinding as a list [y, x].
    :param end: End point of the pathfinding as a list [y, x].
    :param obstacles: List of points that are obstacles, each point represented as a list [y, x].
    :return: Boolean value indicating whether a path exists from start to end without hitting obstacles.
    """
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
    queue = deque([start])
    visited = set()
    visited.add(tuple(start))

    while queue:
        current = queue.popleft()
        if current == end:
            return True

        for dy, dx in directions:
            neighbor = [current[0] + dy, current[1] + dx]
            if (1 <= neighbor[0] <= map_size and 1 <= neighbor[1] <= map_size and
                    tuple(neighbor) not in visited and neighbor not in obstacles):
                queue.append(neighbor)
                visited.add(tuple(neighbor))

    return False


def generate_new_map():
    """
    Generate a new map for the game, including player position, enemies, obstacles, chests, portal, and a boss if applicable.

    :return: None
    """
    global enemies, obstacles, chests, player_position, portal_position, boss
    player_position = [1, 1]  # Reset player position to the starting point
    boss = None  # Reset the boss for each level
    num_enemies = 2 + level  # Increase enemies with each level
    num_chests = 3

    if level == 5:
        # Boss room with no obstacles, just the player and the boss
        obstacles = []
        chests = []
        enemies = []
        boss_position = [map_size // 2, map_size // 2]  # Center of the map
        boss = Boss(boss_position)
    else:
        # Normal room generation with enemies and chests
        # Create an empty grid to represent the maze structure, all walls initially (0 = wall, 1 = path)
        maze = [[0 for _ in range(map_size)] for _ in range(map_size)]

        # Start from a random position in the maze and mark it as a path
        start_x, start_y = random.choice(range(1, map_size, 2)), random.choice(range(1, map_size, 2))
        maze[start_y][start_x] = 1

        # List of walls to consider for carving paths
        walls = [(start_y + dy, start_x + dx) for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)] if
                 0 <= start_y + dy < map_size and 0 <= start_x + dx < map_size]

        # Carve out the maze using Prim's algorithm
        while walls:
            wy, wx = random.choice(walls)
            walls.remove((wy, wx))

            # Check if it is a wall and has exactly one adjacent path
            adjacent_paths = [(wy + dy, wx + dx) for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= wy + dy <
                              map_size and 0 <= wx + dx < map_size and maze[wy + dy][wx + dx] == 1]
            if maze[wy][wx] == 0 and len(adjacent_paths) == 1:
                # Turn this wall into a path with a higher probability (e.g., 80%)
                if random.random() < 0.9:
                    maze[wy][wx] = 1

                # Add neighboring walls to the list
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = wy + dy, wx + dx
                    if 0 <= ny < map_size and 0 <= nx < map_size and maze[ny][nx] == 0:
                        walls.append((ny, nx))

        # Convert the maze into obstacle positions (walls are 0)
        obstacles = [[r + 1, c + 1] for r in range(map_size) for c in range(map_size) if maze[r][c] == 0]

        # Find open positions for enemies and chests
        open_positions = [[r + 1, c + 1] for r in range(map_size) for c in range(map_size) if maze[r][c] == 1]

        # Place enemies and chests at random open positions
        enemies = random.sample([pos for pos in open_positions if pos != player_position],
                                min(num_enemies, len(open_positions)))
        chests = random.sample([pos for pos in open_positions if pos not in enemies and pos != player_position],
                               min(num_chests, len(open_positions)))

        # Place the portal at a random open position far from the player
        portal_position = random.choice(
            [pos for pos in open_positions if pos not in enemies and pos not in chests and pos != player_position])

        # Ensure there's a path from the player to the portal
        while not is_path_available(player_position, portal_position, obstacles):
            # Remove a random obstacle to clear a path
            if obstacles:
                obstacles.pop(random.randint(0, len(obstacles) - 1))


# Initialize the first map
generate_new_map()


def move_player(direction):
    """
    :param direction: The direction in which the player should move. Accepted values are "up", "down", "left", and "right".
    :return: None. The function updates the player's position and triggers relevant game mechanics such as enemy turns, chest interactions, and level advancement.
    """
    global player_position, player_direction
    player_direction = direction
    new_position = player_position.copy()

    if direction == "up":
        new_position[0] -= 1
    elif direction == "down":
        new_position[0] += 1
    elif direction == "left":
        new_position[1] -= 1
    elif direction == "right":
        new_position[1] += 1

    # Check if the new position is valid for movement
    if ((1 <= new_position[0] <= map_size and 1 <= new_position[1] <= map_size) and
            new_position not in enemies and
            new_position not in obstacles and
            (not boss or new_position != boss.position)):
        player_position = new_position
        enemy_turn()  # Trigger enemy turn only if the player actually moved

    # Check for interaction with chests if the player moves into a chest's position
    if new_position in chests:
        open_chest(new_position)

    # Check for interaction with the portal
    if new_position == portal_position:
        advance_level()


# Function to open a chest and add item to inventory
def open_chest(position):
    """
    :param position: The coordinates of the chest that the player has interacted with.
    :return: Returns nothing.
    """
    global current_message, message_timer
    chests.remove(position)
    item = random.choice(item_pool)
    inventory.append(item)
    current_message = f"You picked up {item['name']}!"
    message_timer = 60  # Display the message for about 60 frames (adjust as needed)


def attack():
    """
    Performs the player's attack action. It updates the game state by handling
    the attack animation, removing enemies if hit, damaging the boss if hit,
    and triggering the enemy's turn.

    Global Variables:
        current_message (str): The message displayed to the player.
        Message_timer (int): The timer for the current message.
        Boss (Boss): The boss object in the game.

    Game State Variables:
        player_position (list of int): The current position of the player.
        Player_direction (str): The direction the player is facing.
        Cell_size (int): The size of each cell in the game grid.
        Screen (pygame.Surface): The game screen where graphics are drawn.
        YELLOW (tuple of int): The color used for the attack animation.
        Enemies (list of int): The list of enemy positions.
        Player_stats (dict): Dictionary containing player's stats such as attack power.

    :return: None
    """
    global current_message, message_timer, boss  # Declare boss as global to modify it
    # Get the position the player is attacking based on a direction
    attack_position = player_position.copy()
    if player_direction == "up":
        attack_position[0] -= 1
    elif player_direction == "down":
        attack_position[0] += 1
    elif player_direction == "left":
        attack_position[1] -= 1
    elif player_direction == "right":
        attack_position[1] += 1

    # Draw a more dynamic attack animation
    x = player_position[1] * cell_size
    y = player_position[0] * cell_size

    # Create a circular effect for the attack
    for radius in range(5, 15, 3):  # Vary the size for an expanding circle
        if player_direction == "up":
            pygame.draw.circle(screen, YELLOW, (x + cell_size // 2, y - cell_size // 4), radius, 1)
        elif player_direction == "down":
            pygame.draw.circle(screen, YELLOW, (x + cell_size // 2, y + cell_size + cell_size // 4), radius, 1)
        elif player_direction == "left":
            pygame.draw.circle(screen, YELLOW, (x - cell_size // 4, y + cell_size // 2), radius, 1)
        elif player_direction == "right":
            pygame.draw.circle(screen, YELLOW, (x + cell_size + cell_size // 4, y + cell_size // 2), radius, 1)
        pygame.display.flip()
        pygame.time.delay(30)

    # Remove the enemy if one is at the attack position
    if attack_position in enemies:
        enemies.remove(attack_position)
        current_message = "You defeated an enemy!"
        message_timer = 60

    # Attack the boss if it is at the attack position
    if boss and attack_position == boss.position:
        boss.health -= player_stats["attack"]
        current_message = f"You hit the boss for {player_stats['attack']} damage!"
        message_timer = 60

        # Check if the boss is defeated
        if boss.health <= 0:
            current_message = "You defeated the boss!"
            message_timer = 120
            boss = None  # Remove the boss after it's defeated
            advance_level()  # Advance the level when the boss is defeated

    # Trigger enemy turn after the player attacks
    enemy_turn()


def enemy_turn():
    """
    Performs the enemy's turn in the game. This involves moving each enemy towards the player's position and updating the player's health if any enemy is adjacent to the player. The function also processes the boss's actions if a boss exists.

    Global player_stats: Dictionary containing the player's statistics.
    Global current_message: String for the message to be displayed to the player.
    Global message_timer: Integer for the duration of the current message will be displayed.

    :var new_enemy_positions: List to store new positions of enemies.
    :var enemy_pos: List containing the current position of an enemy.
    :var diff_x: Integer for the difference in the x-axis between player and enemy.
    :var diff_y: Integer for the difference in the y-axis between player and enemy.
    :var move_x: Integer for the movement step in the x-axis.
    :var move_y: Integer for the movement step in the y-axis.
    :var new_pos: List containing the new coordinates for the enemy after movement.
    :var damage: Integer for the damage dealt to the player by an adjacent enemy.

    :return: None
    """
    global player_stats, current_message, message_timer
    new_enemy_positions = []

    for enemy_pos in enemies:
        diff_x = player_position[1] - enemy_pos[1]
        diff_y = player_position[0] - enemy_pos[0]
        move_x = 0
        move_y = 0

        if abs(diff_x) > abs(diff_y):
            move_x = 1 if diff_x > 0 else -1
        else:
            move_y = 1 if diff_y > 0 else -1

        new_pos = [enemy_pos[0] + move_y, enemy_pos[1] + move_x]

        if ((1 <= new_pos[0] <= map_size and 1 <= new_pos[1] <= map_size) and new_pos not in obstacles and new_pos not
                in new_enemy_positions and new_pos != player_position):
            new_enemy_positions.append(new_pos)
        else:
            new_enemy_positions.append(enemy_pos)

        if abs(diff_x) + abs(diff_y) == 1:
            damage = enemy_stats["attack"]
            player_stats["health"] -= damage
            current_message = f"You suffered {damage} damage!"
            message_timer = 60

    enemies[:] = new_enemy_positions

    # Handle boss turn if it exists
    if boss:
        boss.move_towards(player_position)
        boss.attack_player(player_stats)


# Function to advance to the next level
def advance_level():
    """
    Increases the current level by one and generates a new map for the advanced level.

    :return: None
    """
    global level
    level += 1
    generate_new_map()


# Function to toggle the inventory display
def toggle_inventory():
    """
    Toggles the state of the inventory. If the inventory is currently open, it will be closed,
    and if it is currently closed, it will be opened.

    :return: None
    """
    global inventory_open
    inventory_open = not inventory_open


# Function to equip an item
def equip_item(item):
    """
    :param item: Dictionary representing the item to equip. It may contain keys like 'attack_bonus', 'defense_bonus', or 'healing'.
    :return: None
    """
    if "attack_bonus" in item:
        player_stats["attack"] += item["attack_bonus"]
    elif "defense_bonus" in item:
        player_stats["defense"] += item["defense_bonus"]
    elif "healing" in item:
        player_stats["health"] = min(100, player_stats["health"] + item["healing"])
    inventory.remove(item)


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if inventory_open:
                if event.key == pygame.K_UP:
                    selected_item_index = max(0, selected_item_index - 1)
                elif event.key == pygame.K_DOWN:
                    selected_item_index = min(len(inventory) - 1, selected_item_index + 1)
                elif event.key == pygame.K_e and inventory:
                    equip_item(inventory[selected_item_index])
                elif event.key == pygame.K_i:
                    toggle_inventory()
            else:
                if event.key == pygame.K_UP:
                    move_player("up")
                elif event.key == pygame.K_DOWN:
                    move_player("down")
                elif event.key == pygame.K_LEFT:
                    move_player("left")
                elif event.key == pygame.K_RIGHT:
                    move_player("right")
                elif event.key == pygame.K_SPACE:
                    attack()
                elif event.key == pygame.K_i:
                    toggle_inventory()

    # Draw the background
    screen.fill(BLACK)

    # Draw the map and entities
    for row in range(map_size + 2):
        for col in range(map_size + 2):
            x = col * cell_size
            y = row * cell_size

            if row == 0 or row == map_size + 1 or col == 0 or col == map_size + 1:
                pygame.draw.rect(screen, WHITE, (x, y, cell_size, cell_size), 1)
            elif [row, col] == player_position:
                draw_adventurer(screen, x, y, adventurer_sprite)
            elif [row, col] in enemies:
                draw_enemy(screen, x, y, goblin_sprite)
            elif [row, col] in obstacles:
                draw_obstacle(screen, x, y, wall_sprite)
            elif [row, col] in chests:
                draw_chest(screen, x, y, chest_sprite)
            elif [row, col] == portal_position:
                draw_portal(screen, x, y, cell_size)
            else:
                pygame.draw.rect(screen, BLACK, (x, y, cell_size, cell_size))

    # Draw the boss if it exists (Level 5)
    if boss:
        draw_enemy(screen, boss.position[1] * cell_size, boss.position[0] * cell_size, boss.sprite)

    # Check if the player's health is zero or below
    if player_stats["health"] <= 0:
        current_message = "You have been defeated!"
        message_timer = 120
        running = False  # End the game or replace this with a game over screen/restart logic

    # Draw the inventory if it's open
    if inventory_open:
        draw_inventory(screen, inventory, selected_item_index)

    # Draw the stats panel
    draw_stats(screen, player_stats, level)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
