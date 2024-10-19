import pygame

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)  # For highlighting selected items in the inventory
GREEN = (0, 255, 0)  # Color for the player character
RED = (255, 0, 0)  # Color for enemies
GRAY = (128, 128, 128)  # Color for obstacles
MOSS_GREEN = (34, 139, 34)  # Moss color for cobblestones
GOLD = (255, 215, 0)  # Color for chests
PORTAL_COLOR = (100, 100, 255)  # Portal color


# Function to draw the player's character
def draw_adventurer(screen, x, y, sprite):
    """
    :param screen: The surface to draw the sprite on.
    :param x: The x-coordinate where the sprite will be drawn.
    :param y: The y-coordinate where the sprite will be drawn.
    :param sprite: The sprite image to be drawn.
    :return: None
    """
    screen.blit(sprite, (x, y))


def draw_enemy(screen, x, y, sprite):
    """
    :param screen: The surface on which the sprite will be drawn.
    :param x: The x-coordinate where the sprite will be placed.
    :param y: The y-coordinate where the sprite will be placed.
    :param sprite: The image or sprite to be drawn on the screen.
    :return: None
    """
    screen.blit(sprite, (x, y))

# Function to draw obstacles (cobblestones with moss)
def draw_obstacle(screen, x, y, sprite):
    """
    :param screen: The display surface to which the obstacle sprite will be rendered.
    :param x: The x-coordinate where the obstacle will be placed on the screen.
    :param y: The y-coordinate where the obstacle will be placed on the screen.
    :param sprite: The sprite image represents the obstacle.
    :return: None
    """
    screen.blit(sprite, (x, y))

# Function to draw chests
def draw_chest(screen, x, y, sprite):
    """
    :param screen: The Surface object representing the game screen where the sprite will be drawn.
    :param x: The x-coordinate where the top-left corner of the sprite will be placed on the screen.
    :param y: The y-coordinate where the top-left corner of the sprite will be placed on the screen.
    :param sprite: The image or Surface object representing the chest sprite to be drawn.
    :return: None
    """
    screen.blit(sprite, (x,y))

# Function to draw the inventory
def draw_inventory(screen, inventory, selected_item_index):
    """
    :param screen: The Pygame display surface where the inventory will be drawn.
    :param inventory: A list of items where each item is a dictionary containing details like 'name' and 'description'.
    :param selected_item_index: Index of the currently selected item in the inventory.
    :return: None
    """
    inventory_width = 260
    inventory_height = 360
    pygame.draw.rect(screen, BLACK, (20, 20, inventory_width, inventory_height))
    pygame.draw.rect(screen, WHITE, (20, 20, inventory_width, inventory_height), 2)

    # Draw each item in the inventory
    for index, item in enumerate(inventory):
        color = YELLOW if index == selected_item_index else WHITE
        item_name = item["name"]
        text_surface = pygame.font.Font(None, 24).render(item_name, True, color)
        screen.blit(text_surface, (40, 40 + index * 30))

    # Display details of the selected item
    if inventory:
        selected_item = inventory[selected_item_index]
        details = f"Name: {selected_item['name']}"
        details_surface = pygame.font.Font(None, 24).render(details, True, WHITE)
        screen.blit(details_surface, (40, 250))
        description = selected_item["description"]
        description_surface = pygame.font.Font(None, 20).render(description, True, WHITE)
        screen.blit(description_surface, (40, 280))


# Function to draw the player's stats on the right side of the screen
def draw_stats(screen, player_stats, level):
    """
    :param screen: The surface on which the stats panel will be drawn.
    :param player_stats: A dictionary containing the player's health, attack, and defense stats.
    :param level: The current level of the player.
    :return: None
    """
    stats_panel_x = screen.get_width() - 180  # Position the panel on the right side of the screen
    stats_panel_y = 20
    stats_panel_width = 160
    stats_panel_height = 200

    # Draw the stats a panel background
    pygame.draw.rect(screen, BLACK, (stats_panel_x, stats_panel_y, stats_panel_width, stats_panel_height))
    pygame.draw.rect(screen, WHITE, (stats_panel_x, stats_panel_y, stats_panel_width, stats_panel_height), 2)

    # Display each stat
    stats_text = [
        f"Level: {level}",
        f"Health: {player_stats['health']}",
        f"Attack: {player_stats['attack']}",
        f"Defense: {player_stats['defense']}"
    ]

    # Render each line of the stat text
    for i, text in enumerate(stats_text):
        text_surface = pygame.font.Font(None, 24).render(text, True, WHITE)
        screen.blit(text_surface, (stats_panel_x + 10, stats_panel_y + 20 + i * 30))


def perform_attack_animation(screen, player_position, player_direction, cell_size):
    """
    :param screen: The display surface on which animations are drawn.
    :param player_position: Tuple representing the player's current position (row, column) on the grid.
    :param player_direction: String indicating the direction the player is facing; can be "up", "down", "left", or "right".
    :param cell_size: The size of each cell in the grid (width and height in pixels).
    :return: None
    """
    # Calculate the center of the player's current position
    x = player_position[1] * cell_size + cell_size // 2
    y = player_position[0] * cell_size + cell_size // 2

    # Default start and end positions based on a player direction
    start_pos = (x, y)
    if player_direction == "up":
        end_pos = (x, y - cell_size)
    elif player_direction == "down":
        end_pos = (x, y + cell_size)
    elif player_direction == "left":
        end_pos = (x - cell_size, y)
    elif player_direction == "right":
        end_pos = (x + cell_size, y)
    else:
        end_pos = start_pos

    # Draw the attack line in yellow to represent a sword swing
    pygame.draw.line(screen, YELLOW, start_pos, end_pos, 3)

    # Update the display to show the attack animation
    pygame.display.flip()

    # Pause briefly to display the animation
    pygame.time.delay(100)

    # Redraw the cell to remove the attack line (for a simple animation effect)
    pygame.draw.rect(screen, BLACK, (player_position[1] * cell_size, player_position[0] * cell_size, cell_size,
                                     cell_size))
    pygame.display.flip()


def draw_portal(screen, x, y, cell_size):
    """
    :param screen: The surface to draw the portal on.
    :param x: The x-coordinate of the top-left corner of the portal.
    :param y: The y-coordinate of the top-left corner of the portal.
    :param cell_size: The size of the cell in which the portal is drawn.
    :return: None
    """
    # Draw the outer circle of the portal
    pygame.draw.circle(screen, PORTAL_COLOR, (x + cell_size // 2, y + cell_size // 2), cell_size // 2 - 4, 2)
    # Draw an inner circle for a more layered look
    pygame.draw.circle(screen, (0, 0, 128), (x + cell_size // 2, y + cell_size // 2), cell_size // 4, 2)
    # Add a small center glow for effect
    pygame.draw.circle(screen, (173, 216, 230), (x + cell_size // 2, y + cell_size // 2), cell_size // 8)
