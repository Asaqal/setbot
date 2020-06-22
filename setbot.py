# ========================================================================
# ========================================================================
import time
import re
from selenium import webdriver
from pynput import keyboard

# ========================================================================
# ========================================================================
driver = webdriver.Chrome() # initalizes the chromedriver

def setup():
    """Maximizes the window, navigates to setwithfriends, chooses dark theme, sets name to "setbot"
    """
    driver.maximize_window()
    time.sleep(1)
    driver.get("https://setwithfriends.com/")
    time.sleep(5)
    driver.find_element_by_xpath("//button[contains(@class,'MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textPrimary')]").click()
    time.sleep(1)
    driver.find_element_by_xpath("//button[contains(@class,'MuiButtonBase-root MuiIconButton-root MuiIconButton-colorInherit')][2]").click()
    time.sleep(1)
    driver.find_element_by_xpath("//button[contains(@class,'MuiButtonBase-root MuiIconButton-root MuiIconButton-colorInherit')][1]").click()
    time.sleep(1)
    driver.find_element_by_xpath("//input[contains(@id,'name')]").send_keys("setbot")
    time.sleep(1)
    driver.find_element_by_xpath("//div[contains(@class,'MuiDialogActions-root MuiDialogActions-spacing')]/button[contains(@class,'MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary')]").click()

setup() # runs on program launch

# ========================================================================
# ========================================================================
def get_deck():
    """Creates a deck out of the cards on screen

    Returns:
        webelement-list: visible cards
    """
    deck = driver.find_elements_by_xpath("//div[contains(@style,'transition: height 0.75s ease 0s;')]/div[contains(@style,'visibility: visible')]")
    return deck

# ========================================================================
def get_pixel_positions(deck):
    """Gets the pixel position of each card in order to later place the cards correctly

    Args:
        deck (webelement-list): visible cards

    Returns:
        2D-list: [x-coords, y-coords] pixel locations of the cards
    """
    x_positions = []
    y_positions = []
    
    for card in deck:
        text = card.get_attribute("style")
        
        x = int(re.search("\((.+?)px", text).group(1))
        if x not in x_positions:
            x_positions.append(x)
        
        y = int(re.search(", (.+?)px", text).group(1))
        if y not in y_positions:
            y_positions.append(y)

    return [sorted(x_positions), sorted(y_positions)]

def get_position(positions, card):
    """Returns the correct x and y grid location of the card

    Args:
        positions (2D-list): pixel positions of the visible cards -> output from get_pixel_positions
        card (webelement): a visible card

    Returns:
        list: [x, y] grid location of the card
    """
    text = card.get_attribute("style")
    
    x = positions[0].index(int(re.search("\((.+?)px", text).group(1)))
    y = positions[1].index(int(re.search(", (.+?)px", text).group(1)))
    
    return [x, y]

def sort_deck(deck):
    """Places the cards in the correct positions

    Args:
        deck (webelement-list): visible cards

    Returns:
        webelement-list: visible cards
    """
    positions = get_pixel_positions(deck)
    temp_deck = [[None]*3 for _ in range(7)]
    
    for card in deck:
        card_pos = get_position(positions, card)
        temp_deck[card_pos[1]][card_pos[0]] = card
        
    temp_deck = sum(temp_deck, [])
    return temp_deck[0:temp_deck.index(None)]

# ========================================================================
def get_key(i):
    """Returns the corresponding hotkey of the card

    Args:
        i (int): card's position

    Returns:
        str: card's hotkey
    """
    return "123qweasdzxcrtyfghvbn"[i]

def get_num(card):
    """Returns the card's number

    Args:
        card (webelement): a visible card

    Returns:
        int: card's number
    """
    return len(card.find_elements_by_xpath(".//div//*")) // 3

def get_color(card):
    """Returns the card's color

    Args:
        card (webelement): a visible card

    Returns:
        str: card's color
    """
    color = card.find_element_by_xpath(".//div/*[name()='svg']/*[name()='use'][2]").get_attribute("stroke")

    # both light and dark theme
    if (color == "#ff0101" or color == "#ffb047"):
        color = "red"
    elif (color == "#800080" or color == "#ff47ff"):
        color = "purple"
    else:
        color = "green"
    
    return color

def get_shape(card):
    """Returns the card's shape

    Args:
        card (webelement): a visible card

    Returns:
        str: card's shape
    """
    return card.find_element_by_xpath(".//div/*[name()='svg']/*[name()='use'][1]").get_attribute("href")[1:]

def get_fill(card):
    """Returns the card's fill

    Args:
        card (webelement): a visible card

    Returns:
        str: card's fill
    """
    fill = card.find_element_by_xpath(".//div/*[name()='svg']/*[name()='use'][1]").get_attribute("fill")

    if (fill == "transparent"):
        fill = "clear"
    else:
        mask = card.find_element_by_xpath(".//div/*[name()='svg']/*[name()='use'][1]").get_attribute("mask")

        if (mask == "url(#mask-stripe)"):
            fill = "half"
        else:
            fill = "solid"
    
    return fill

def get_info(deck):
    """Returns a 2D-list representing the deck. Each card is represented by [hotkey, number, color, shape, fill]

    Args:
        deck (webelement-list): visible cards

    Returns:
        2D-list: visible cards, with each card represented by 5 characteristics
    """
    temp_deck = [[None]*5 for _ in range(len(deck))]

    for i, temp_card in enumerate(temp_deck):
        temp_card[0] = get_key(i)
        temp_card[1] = get_num(deck[i])
        temp_card[2] = get_color(deck[i])
        temp_card[3] = get_shape(deck[i])
        temp_card[4] = get_fill(deck[i])
    
    return temp_deck

# ========================================================================
def construct_deck():
    """Constructs the deck of visible cards

    Returns:
        2D-list: visible cards, with each card represented by 5 characteristics
    """
    deck = get_deck()
    deck = sort_deck(deck)
    deck = get_info(deck)
    return deck

# ========================================================================
# ========================================================================
def is_match(set, i):
    """Checks if the three cards all have the same characteristic

    Args:
        set (2D-list): a set of three cards
        i (int): characterstic

    Returns:
        boolean: boolean
    """
    if (set[0][i] == set[1][i] and set[1][i] == set[2][i]):
        return True
    return False

def is_diff(set, i):
    """Checks if the cards all have different characteristics

    Args:
        set (2D-list): a set of three cards
        i (int): characteristic

    Returns:
        boolean: boolean
    """
    if (set[0][i] != set[1][i] and set[1][i] != set[2][i] and set[0][i] != set[2][i]):
        return True
    return False

def is_valid(set):
    """Checks if the set is valid

    Args:
        set (2D-list): a set of three cards

    Returns:
        boolean: boolean
    """
    for i in range(1, 5):
        if not(is_match(set, i) or is_diff(set, i)):
            return False
    return True

def solve(deck):
    """Finds a valid set for the visible cards

    Args:
        deck (2D-list): visible cards, with each card represented by 5 characteristics

    Returns:
        str: the hotkeys for the valid set
    """
    sets = []
    for i in range(len(deck)):
        for j in range(i+1, len(deck)):
            for k in range(j+1, len(deck)):
                set = [deck[i], deck[j], deck[k]]
                sets.append(set)
                if (is_valid(set)):
                    return set[0][0] + set[1][0] + set[2][0]

# =======================================================================
def bot():
    """Continuously chooses valid sets until the game is over
    """
    while (driver.find_element_by_xpath("//div[contains(@class,'MuiGrid-grid-md-6')]/div[contains(@style,'visibility')]").get_attribute("style") == "opacity: 0; visibility: hidden;"): # while the end-game popup is hidden
        try:
            deck = construct_deck()
            solution = solve(deck)
            keyboard.Controller().type(solution)
        except:
            pass # does not throw errors if the bot constructs a deck too early
        time.sleep(0.1)

# ========================================================================
# ========================================================================
def on_press(key):
    """A keyboard listener to control the starting of the bot, and the closing of the chromedriver

    Args:
        key (key): pressed key

    Returns:
        boolean: ends the keyboard listener
    """
    try:
        if (key.char == "`"):
            bot()

    except AttributeError:
        if (key == keyboard.Key.esc):
            driver.quit()
            return False

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# ========================================================================
# ========================================================================