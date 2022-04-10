"""
A simple discord bot

Author: Nadav Nir
GitHub: https://github.com/Nadav-Nir
"""

__author__ = "Nadav Nir"
__github__ = "https://github.com/Nadav-Nir"

# imports
import asyncio
import os
import disnake
from disnake.ext import commands
from disnake.enums import ButtonStyle
from disnake import TextInputStyle
from dotenv import load_dotenv
import requests
import secrets
import pokepy
import random

# classess

class TicTacToe:  # class for tic tac toe game
    def __init__(self, p1, p2):
        self.SWAP_REFERENCE = {  # dictionary to make it easier to swap the current active player between the players
            p1: p2,
            p2: p1
        }
        self.game_won = False
        self.winner = None
        self.P1 = p1
        self.P2 = p2
        self.board = [[":black_large_square:", ":white_large_square:", ":black_large_square:"],  # tic tac toe board
                      [":white_large_square:", ":black_large_square:", ":white_large_square:"],
                      [":black_large_square:", ":white_large_square:", ":black_large_square:"]]
        self.SYMBOL = {  # dictionary to make it easier to refer to each player's symbol.
            self.P1: ":regional_indicator_x:",
            self.P2: ":regional_indicator_o:"
        }

    def message_to_coords(self, coords):  # converts text to coordinates
        if "," not in coords:  # checks if there is a comma separating each
            return False       # number to be able to differentiate between them
        coords = coords.replace(" ", "").replace("(", "")\
            .replace(")", "").split(",")  # removes spaces from the message and separates
        coords[0] = int(coords[0])                   # the message at the comma to provide two different
        coords[1] = int(coords[1])                   # strings, which are then turned into numbers
        if coords[0] and coords[1] > len(self.board) - 1:
            return False  # checks if each coordinate is bigger than the biggest coordinate in the board
        return coords

    def print_board(self):  # function to print the board
        s_board = ""  # the string form of the board
        board_len = len(self.board)  # var to contain length of board to avoid continuous use of len(self.board)
        for i in range(board_len):
            for j in range(board_len):
                s_board += self.board[i][j]  # adds every spot in the board to the string
            s_board += "\n"  # adds a new line every row
        return s_board

    def choose_spot(self, player, coords):  # function to let the player choose the spot they want to play their symbol.
        coords = self.message_to_coords(coords)  # converts the coords string into a usable int array
        if not coords:  # returns false if coords not usable
            return False
        if self.board[coords[0]][coords[1]] != ":regional_indicator_x:" \
                or self.board[coords[0]][coords[1]] != ":regional_indicator_o:":
            # checks if the wanted spot is available to place the player's symbol
            self.board[coords[0]][coords[1]] = self.SYMBOL[player]  # places the player's symbol
            return True
        return False

    def check_row(self, player):
        for row in self.board:
            count = 0
            for spot in row:
                if spot == self.SYMBOL[player]:
                    count += 1
                    continue
                count = 0
                break
            if count == len(self.board):
                return True

    def check_column(self, player):
        for x in range(len(self.board)):
            count = 0
            for y in range(len(self.board)):
                if self.board[y][x] == self.SYMBOL[player]:
                    count += 1
                    continue
                count = 0
                print("break")
                break
            if count == len(self.board):
                return True
        return False

    def check_diagonal(self, player):
        count = 0
        for i in range(len(self.board)):
            if self.board[i][i] == self.SYMBOL[player]:
                count += 1
                continue
            break
        if count == len(self.board):
            return True
        return False

    def check_diagonal2(self, player):
        j = len(self.board) - 1
        count = 0
        for i in range(3):
            if self.board[i][j] == self.SYMBOL[player]:
                count += 1
                j -= 1
                continue
            break
        if count == 3:
            return True

    def check_win(self, player):
        if self.check_column(player):
            self.set_winner(player)
            return True
        if self.check_row(player):
            self.set_winner(player)
            return True
        if self.check_diagonal(player):
            self.set_winner(player)
            return True
        if self.check_diagonal2(player):
            self.set_winner(player)
            return True

        return False

    def set_winner(self, player):
        self.winner = player
        self.game_won = True

class help_buttons(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Categories", style=ButtonStyle.primary)
    async def help_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = await help(interaction, None, True)
        await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Fun", style=ButtonStyle.primary)
    async def fun_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = await help(interaction, "fun", True)
        await interaction.response.edit_message(embed=embed)

    @disnake.ui.button(label="Useful", style=ButtonStyle.primary)
    async def useful_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = await help(interaction, "useful", True)
        await interaction.response.edit_message(embed=embed)

load_dotenv()
token = os.getenv('discord_Token')
prefix = "!"

# variables
pokemon = None
#bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all(), self_bot=False)  # bot declaration
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), self_bot=False, intents=disnake.Intents.all())
#slash = SlashCommand(bot, sync_commands=True)
bot.remove_command('help')

im = ["I'm", "i'm", "I'M",
      "i'M", "Im", "im",
      "IM", "iM", "I am",
      "i Am", "i aM", "I Am",
      "I AM", "i AM", "I aM",
      "i am"]  # list of I'm possibilities for the im function

async def ttt_turn(game, ctx, player):
    game.print_board()
    msg = f"{player.mention} where would you like to place your " + game.SYMBOL[player] + \
          "?You have 30 seconds to respond with" + " coordinates (eg. " + \
          str(secrets.randbelow(3)) + "," + str(secrets.randbelow(3)) + \
          "/" + str(secrets.randbelow(3)) + "," + str(secrets.randbelow(3)) + ")."

    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.channel.send(msg, allowed_mentions=disnake.AllowedMentions.none())
    else:
        await ctx.send(msg, allowed_mentions=disnake.AllowedMentions.none())

    def check(m):
        return m.channel == ctx.channel and m.author == player

    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.channel.send(f"{player.mention} you realize you need to play for a game to work right?")
        else:
            await ctx.send(f"{player.mention} you realize you need to play for a game to work right?")
        game.set_winner(game.SWAP_REFERENCE(player))
    else:
        await ttt_commit_turn(game, ctx, player, msg.content)
        return msg.content

async def ttt_commit_turn(game, ctx, player, results):
    if not game.choose_spot(player, results):
        msg = f"{player.mention}, the coordinates you inputted are invalid or are" \
              f" already taken. Please actually do it right this time."
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.channel.send(msg, allowed_mentions=disnake.AllowedMentions.none())
        else:
            await ctx.send(msg, allowed_mentions=disnake.AllowedMentions.none())
        await ttt_turn(game, ctx, player)
    else:
        return True

def ttt_switch_turn(player, swap_reference):
    return swap_reference[player]

async def ttt_game(ctx, p1, p2):
    game = TicTacToe(p1, p2)
    player = p1
    turns = 0
    while not game.game_won:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.channel.send(game.print_board())
            await ctx.channel.send(f"It is {player.mention}'s Turn! (" + game.SYMBOL[player] + ")",
                                   allowed_mentions=disnake.AllowedMentions.none())
        else:
            await ctx.send(game.print_board())
            await ctx.send(f"It is {player.mention}'s Turn! (" + game.SYMBOL[player] + ")",
                           allowed_mentions=disnake.AllowedMentions.none())
        await ttt_turn(game, ctx, player)
        turns += 1
        game.check_win(player)
        player = ttt_switch_turn(player, game.SWAP_REFERENCE)
        if turns == 9:
            game.winner = False
            break
    if game.winner:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.channel.send(f"Player {game.winner.mention} has won! The game lasted {turns} turns!",
                                   allowed_mentions=disnake.AllowedMentions.none())
            await ctx.channel.send(game.print_board())
            return game.winner
        await ctx.send(f"Player {game.winner.mention} has won! The game lasted {turns} turns!",
                       allowed_mentions=disnake.AllowedMentions.none())
        await ctx.send(game.print_board())
        return game.winner
    else:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.channel.send("The game has ended in a tie!")
            await ctx.channel.send(game.print_board())
            return False
        await ctx.send("The game has ended in a tie!")
        await ctx.send(game.print_board())
        return False

async def rps_ask(player, og):
    dm = await player.create_dm()

    await dm.send(f"{player.mention} what is your choice? (rock/paper/scissors) You have 60 seconds to answer.")

    try:
        msg = await bot.wait_for('message', timeout=60)
    except asyncio.TimeoutError:
        await dm.send(f"{player.mention} you realize you need to play for a game to work right?")
        await og.send(f"{player.mention} did not reply in time and therefore the game has ended")
        return -1

    await dm.send(f'{player.mention} thank you for answering. You may now go back to the original channel.',
                  allowed_mentions=disnake.AllowedMentions.none())

    result = msg.content.lower()
    if result != "rock" and result != "paper" and result != "scissors":
        return False
    return result

async def rps_game(ctx, p1, p2):
    p1_choice = await rps_ask(p1, ctx)
    while not p1_choice:
        p1_choice = await rps_ask(p1, ctx)
    p2_choice = await rps_ask(p2, ctx)
    while not p2_choice:
        p2_choice = await rps_ask(p2, ctx)
    if p1_choice and p2_choice == -1:
        return -1

    if p1_choice == "rock":
        if p2_choice == "rock":
            resolution = f"Since both {p1.mention} and {p2.mention} have chosen rock, the game has ended in a tie!"
        elif p2_choice == "paper":
            resolution = f"Since {p2.mention} has chosen paper which overpowers {p1.mention}'s" \
                         f" choice of rock, The winner is {p2.mention}!"
        else:
            resolution = f"Since {p1.mention} has chosen rock which overpowers {p2.mention}'s" \
                         f" choice of scissors, The winner is {p1.mention}!"
    elif p1_choice == "paper":
        if p2_choice == "rock":
            resolution = f"Since {p1.mention} has chosen paper which overpowers {p2.mention}'s" \
                         f" choice of rock, The winner is {p1.mention}!"
        elif p2_choice == "paper":
            resolution = f"Since both {p1.mention} and {p2.mention} have chosen paper, the game has ended in a tie!"
        else:
            resolution = f"Since {p2.mention} has chosen scissors which overpowers {p1.mention}'s" \
                         f" choice of rock, The winner is {p2.mention}!"
    else:  # p1 chose scissors
        if p2_choice == "rock":
            resolution = f"Since {p2.mention} has chosen rock which overpowers {p2.mention}'s" \
                         f" choice of scissors, The winner is {p1.mention}!"
        elif p2_choice == "paper":
            resolution = f"Since {p1.mention} has chosen scissors which overpowers {p2.mention}'s" \
                         f" choice of paper, The winner is {p2.mention}!"
        else:
            resolution = f"Since both {p1.mention} and {p2.mention} have chosen scissors, the game has ended in a tie!"

    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.channel.send(f'{p1.mention} has chosen {p1_choice} and {p2.mention} has chosen {p2_choice}. '
                               + resolution, allowed_mentions=disnake.AllowedMentions.none())
        return
    await ctx.send(f'{p1.mention} has chosen {p1_choice} and {p2.mention} has chosen {p2_choice}. ' + resolution,
                   allowed_mentions=disnake.AllowedMentions.none())

async def status():  # obtained help from https://www.youtube.com/watch?v=xNTV5DVhxxk
    await bot.wait_until_ready()

    while not bot.is_closed():
        activity = disnake.Game(name=requests.get("https://icanhazdadjoke.com/",
                                headers={'Accept': 'application/json'}).json().get('joke'))
        await bot.change_presence(activity=activity)
        await asyncio.sleep(30)

# end of function supporting functions

# command functions

async def dadjoke(ctx):
    joke_msg = requests.get("https://icanhazdadjoke.com/", headers={'Accept': 'application/json'}).json().get('joke')
    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(joke_msg)
        return
    await ctx.reply(joke_msg)

async def wikipedia(ctx):
    wikipedia_article = requests.get("https://en.wikipedia.org/wiki/Special:Random").content.decode()
    wikipedia_article = wikipedia_article.split("<title>")[1].split("- Wikipedia</title>")[0]
    wikipedia_article = "Article: "+wikipedia_article+"\nArticle Link: https://en.wikipedia.org/wiki/" + \
                        wikipedia_article.replace(" ", "_")
    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(wikipedia_article)
        return
    await ctx.reply(wikipedia_article)

async def check(ctx, member: disnake.Member):  # obtains information about a person in the guild and sends it
    member_info = f"Name: {member.name}\n" \
                  f"Nickname: {member.nick}\n" \
                  f"Member ID: {member.id}\n" \
                  f"Member Status: {member.status}\n" \
                  f"Date member made account: {member.created_at} UTC\n" \
                  f"Date member joined guild: {member.joined_at} UTC\n" \
                  f"Member avatar URL: {member.avatar}\n" \
                  f"Member's highest role: {member.top_role}\n"
    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(member_info, allowed_mentions=disnake.AllowedMentions.none())
        return
    await ctx.reply(member_info, allowed_mentions=disnake.AllowedMentions.none())

async def rps(ctx, p2: disnake.Member):  # rock paper scissors game
    p1 = ctx.author
    challenge_msg = p1.mention + " has challenged " + p2.mention +\
                    "! If you would like to accept this challenge, type 'yes'." + \
                    " If you do not want to accept the challenge," + \
                    " just don't respond." + \
                    " The request will time out in 3 minutes."

    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(challenge_msg, allowed_mentions=disnake.AllowedMentions.none())
    else:
        await ctx.reply(challenge_msg, allowed_mentions=disnake.AllowedMentions.none())

    def check(m):
        return m.content.lower() == 'yes' and m.channel == ctx.channel and m.author == p2

    try:
        await bot.wait_for('message', check=check, timeout=180)
    except asyncio.TimeoutError:
        await ctx.send(f'{p2.mention} has failed to respond, or did not want'
                       f' to accept the challenge. What a coward.', allowed_mentions=disnake.AllowedMentions.none())
    else:
        await ctx.send(f'{p2.mention} has accepted the challenge! What a chad.',
                       allowed_mentions=disnake.AllowedMentions.none())
        await ctx.send(f'Let the game begin!')
        await rps_game(ctx, p1, p2)

async def tictactoe(ctx, p2: disnake.Member):  # tic tac toe game
    p1 = ctx.author

    challenge_msg = p1.mention + " has challenged " + \
                    p2.mention + "! If you would like to accept this challenge, type 'yes'." + \
                    " If you do not want to accept the challenge," + \
                    " just don't respond." + \
                    " The request will time out in 3 minutes."

    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(challenge_msg, allowed_mentions=disnake.AllowedMentions.none())
    else:
        await ctx.reply(challenge_msg, allowed_mentions=disnake.AllowedMentions.none())

    def check(m):
        return m.content.lower() == 'yes' and m.channel == ctx.channel and m.author == p2

    try:
        await bot.wait_for('message', check=check, timeout=180)
    except asyncio.TimeoutError:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.channel.send(f'{p2.mention} has failed to respond, or did not want to accept the '
                                   f'challenge. What a coward.', allowed_mentions=disnake.AllowedMentions.none())
        else:
            await ctx.send(f'{p2.mention} has failed to respond, or did not want'
                           f' to accept the challenge. What a coward.', allowed_mentions=disnake.AllowedMentions.none())
    else:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.channel.send(f'{p2.mention} has accepted the challenge! What a chad.',
                                   allowed_mentions=disnake.AllowedMentions.none())
            await ctx.channel.send(f'Let the game begin!')
        else:
            await ctx.send(f'{p2.mention} has accepted the challenge! What a chad.',
                           allowed_mentions=disnake.AllowedMentions.none())
            await ctx.send(f'Let the game begin!')
        await ttt_game(ctx, p1, p2)

async def help(ctx, category=None, edit=False):
    view = help_buttons()

    if category is None:
        title = "Help Commands"
        description = "Available help command categories:"
        footer = f"Requested by {ctx.author.display_name}."
        color = disnake.Colour.purple()
        user_pfp = ctx.author.avatar

        embed = disnake.Embed(title=title, description=description, color=color)

        embed.set_footer(text=footer, icon_url=user_pfp)

        embed.add_field(name="Fun", value=f"{prefix}help fun")
        embed.add_field(name="Useful", value=f"{prefix}help useful")
        embed.add_field(name="Generic Help Command Section", value=f"{prefix}help generic")
        embed.add_field(name="Generic Help Command Section", value=f"{prefix}help generic")
        embed.add_field(name="Generic Help Command Section", value=f"{prefix}help generic")
        embed.add_field(name="Generic Help Command Section", value=f"{prefix}help generic")

        if edit:
            return embed
        else:
            await ctx.send(embed=embed, view=view)
    elif category.lower() == "fun":
        title = "Fun Commands"
        color = disnake.Colour.purple()
        footer = f"Requested by {ctx.author.display_name}."
        description = "Available fun commands:"
        user_pfp = ctx.author.avatar

        embed = disnake.Embed(title=title, description=description, color=color)

        embed.set_footer(text=footer, icon_url=user_pfp)

        embed.add_field(name=f"{prefix}dadjoke", value="Sends a random dad joke")
        embed.add_field(name=f"{prefix}rps (mention)",
                        value=f"Starts a game of rock paper scissors."
                        f" Example: {prefix}rps @GenericName")
        embed.add_field(name=f"{prefix}tictactoe (mention)",
                        value=f"Starts a game of tic tac toe."
                             f" Aliases: {prefix}TicTacToe"
                             f" Example: {prefix}ttt @GenericName")
        embed.add_field(name=f"{prefix}wikipedia",
                        value=f"Sends a random wikipedia article. Aliases: {prefix}wk, {prefix}article")
        embed.add_field(name=f"{prefix}roll",
                        value=f"Rolls a die! Aliases: {prefix}dice")
        embed.add_field(name=f"{prefix}pokemon",
                        value=f"Retrieves information about a pokemon. Aliases: {prefix}poke, {prefix}mon, {prefix}pkmn")
        embed.add_field(name=f"{prefix}flip", value=f"Flips a coin.")

        if edit:
            return embed
        else:
            await ctx.send(embed=embed, view=view)
    elif category.lower() == "useful":
        title = "Useful Commands"
        color = disnake.Colour.purple()
        footer = f"Requested by {ctx.author.display_name}."
        description = "Available useful commands:"
        user_pfp = ctx.author.avatar

        embed = disnake.Embed(title=title, description=description, color=color)

        embed.set_footer(text=footer, icon_url=user_pfp)

        embed.add_field(name=f"{prefix}check", value="Returns a lot of information about the user.")
        embed.add_field(name=f"/ReportProblem", value="Opens a problem report form for the user.")
        embed.add_field(name=f"/Feedback", value="Opens a feedback form for the user.")

        if edit:
            return embed
        else:
            await ctx.send(embed=embed, view=view)
    else:
        title = "Non-existent category"
        color = disnake.Colour.purple()
        footer = f"Requested by {ctx.author.display_name}."
        description = "This category does not exist."
        user_pfp = ctx.author.avatar

        embed = disnake.Embed(title=title, description=description, color=color)

        embed.set_footer(text=footer, icon_url=user_pfp)

        if edit:
            return embed
        else:
            await ctx.send(embed=embed, view=view)

async def roll(ctx, roll):
    user_roll = roll.split('d')
    if len(user_roll) > 2:
        print(user_roll + "\n" + str(len(user_roll)))
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.response.send_message("Please write the roll command properly. Format: [amount of die]d[die type]")
            return
        await ctx.reply("Please write the roll command properly. Format: [amount of die]d[die type]")
        return

    try:
        amount = int(user_roll[0])
        die = int(user_roll[1])
    except ValueError:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.response.send_message("Please reply with numbers, not letters or words.")
            return
        await ctx.reply("Please reply with numbers, not letters or words.")
        return

    total = 0

    if "+" in user_roll[1]:
        user_roll[1].split('+').remove('+')
        try:
            add = int(user_roll[1][1])
            total = add
        except ValueError:
            if "ApplicationCommandInteraction" in str(type(ctx)):
                await ctx.response.send_message("Please reply with numbers, not letters or words.")
                return
            await ctx.reply("Please reply with numbers, not letters or words.")
            return

    result = "`"

    nums = []

    for i in range(amount):
        nums.append(secrets.randbelow(die))

    nums.sort(reverse=True)

    for num in nums:
        total += num
        result += f"{num},"

    result = result[:-1]
    result += f".` The total result is: {total}. Rolled {amount} die of d{die}."

    if len(result) > 2000:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.response.send_message(f"The total result is {total}. Sadly there wasn't"
                            f" enough space to send all the individual numbers.")
            return
        await ctx.reply(f"The total result is {total}. Sadly there wasn't"
                        f" enough space to send all the individual numbers.")
        return

    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(result)
        return
    await ctx.reply(result)

async def pokemon(ctx, pokemon_name=None):
    client = pokepy.V2Client()
    if pokemon_name is None:
        if "ApplicationCommandInteraction" in str(type(ctx)):
            await ctx.response.send_message("You must specify a pokemon in order to get information about it")
            return
        await ctx.reply("You must specify a pokemon in order to get information about it")
        return
    pokemon = client.get_pokemon(pokemon_name)[0]

    title = pokemon.name
    description = f"{pokemon.name}'s stats:"
    footer = f"Requested by {ctx.author.display_name}."
    color = disnake.Colour.purple()
    user_pfp = ctx.author.avatar

    embed = disnake.Embed(title=title, description=description, color=color)

    embed.set_footer(text=footer, icon_url=user_pfp)
    embed.set_thumbnail(url=pokemon.sprites.front_default)

    embed.add_field(name="ID", value=str(pokemon.id))
    if len(pokemon.types) == 1:
        embed.add_field(name="Types", value=pokemon.types[0].type)
    else:
        type1 = str(pokemon.types[0].type).split("| ")[1].split(">")[0].capitalize()
        type2 = str(pokemon.types[1].type).split("| ")[1].split(">")[0].capitalize()

        embed.add_field(name="Types", value=f"{type1}, {type2}")
    embed.add_field(name="Weight", value=f"{pokemon.weight/10}kg")
    embed.add_field(name="Height", value=f"{pokemon.height*10}cm")

    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(embed=embed)
        return
    await ctx.reply(embed=embed)

async def flip(ctx):
    result = secrets.randbelow(2)
    if result == 0:
        title = "Coin landed on heads!"
        description = "Heads!"
    else:
        title = "Coin landed on tails!"
        description = "Tails!"
    footer = f"Requested by {ctx.author.display_name}."
    color = disnake.Colour.purple()
    user_pfp = ctx.author.avatar

    embed = disnake.Embed(title=title, description=description, color=color)

    embed.set_footer(text=footer, icon_url=user_pfp)
    url = 'https://freight.cargo.site/t/original/i/8c26cb1e6d8b7aead75057ad75428318b5e604d054e018e62d7b3a628c6bb70b/coinflip_01.gif'
    embed.set_image(url=url)

    if "ApplicationCommandInteraction" in str(type(ctx)):
        await ctx.response.send_message(embed=embed)
        return
    await ctx.reply(embed=embed)

# end of command functions

# events
@bot.event  # event to send message in console when bot connected to discord
async def on_ready():
    print(f'{bot.user.name} ({bot.user.id}) connected to discord.')

@bot.event  # event to check if member joins discord guild
async def on_member_join(ctx, member):
    # print(f'{member.name} has joined') # prints the member name in the console
    await member.send(f'Welcome to the server {member.name}! Nice to meet you.',
                      allowed_mentions=disnake.AllowedMentions.none())

@bot.event  # events that trigger when someone sends a message (not commands)
async def on_message(message):
    if message.author == bot.user:  # refrains from answering itself.
        return

    ''' disabling this because for it's really really annoying
    for i in range(len(im)):  # answers with the classic "Hi (something), I'm dad" joke
        if im[i]+" " in message.content:
            await message.channel.send("Hi" + message.content.split(im[i], 1)[1] + f", I'm {bot.user.name}!")
            break
    '''
    await bot.process_commands(message)  # makes it so commands don't get ignored
# end of events

# responds from a random dad joke grabbed from icanhazdadjoke.com's api

@bot.command(name='dadjoke', help='responds with a dad joke')
async def dadjoke_command(ctx):
    await dadjoke(ctx)

# responds with a random wikipedia article
@bot.command(name='wikipedia', help='responds with a random wikipedia article', alias=["wk", "article"])
async def wikipedia_command(ctx):
    await wikipedia(ctx)

@bot.command(name='check', help='Provides information about a server member')
async def check_command(ctx, member: disnake.Member):  # obtains information about a person in the guild and sends it
    await check(ctx, member)

@bot.command(name="rps", help="starts a game of rock paper scissors", aliases=["rockpaperscissors"])
async def rps_command(ctx, p2: disnake.Member):  # rock paper scissors game
    await rps(ctx, p2)

@bot.command(name='tictactoe', help='starts a game of tic tac toe', aliases=["ttt"])
async def tictactoe_command(ctx, p2: disnake.Member):  # tic tac toe game
    await tictactoe(ctx, p2)

@bot.command(name="help", help='help command')
async def help_command(ctx, category=None):
    await help(ctx, category)

@bot.command(name='roll', help='Rolls dice', aliases=['dice'])
async def roll_command(ctx, user_roll):
    await roll(ctx, user_roll)

@bot.command(name='pokemon', help='retrieves info about a pokemon', aliases=['poke', 'mon', 'pkmn'])
async def pokemon_command(ctx, pokemon_name=None):
    await pokemon(ctx, pokemon_name)

@bot.command(name="flip", help="Flips a coin")
async def flip_command(ctx):
    await flip(ctx)

# re-implementation of commands above as slash commands
@bot.slash_command(name='ReportProblem', description='Report a problem with the bot')
async def problem_report(inter: disnake.AppCmdInter):
    await inter.response.send_modal(
        title="Problem Report Form",
        custom_id="problem_report",
        components=[
            disnake.ui.TextInput(
                label="What is the problem you encountered?",
                placeholder="Problem",
                custom_id="problem",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Please expand more on the problem",
                placeholder="Problem explanation",
                custom_id="explanation",
                style=TextInputStyle.paragraph,
            )
        ]
    )

    await inter.send("Opening problem report form!")

    try:
        modal_inter: disnake.ModalInteraction = await bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "problem_report" and i.author.id == inter.author.id,
            timeout=300
        )
    except asyncio.TimeoutError:
        await inter.send(f"{inter.author.name} did not respond in time :(")
        return

    results = modal_inter.text_values
    response = f"Author: {inter.author.name}\n" \
               f"Author ID: {inter.author.id}\n" \
               f"Problem: {results['problem']}\n" \
               f"Explanation: {results['explanation']}" \
               "--------------"

    with open('reports.txt', 'a', encoding='utf-8') as f:
        f.write(response)

    await inter.send("Thank you for reporting a problem!")

@bot.slash_command(name='Feedback', description='Give feedback!')
async def feedback(inter: disnake.AppCmdInter):
    await inter.response.send_modal(
        title="Feedback Form",
        custom_id="feedback",
        components=[
                    disnake.ui.TextInput(
                        label="How has your experience with the bot been?",
                        custom_id="experience",
                        style=TextInputStyle.short,
                        max_length=100,
                    ),
                    disnake.ui.TextInput(
                        label="Would you recommend this bot to a friend?",
                        custom_id="recommend",
                        style=TextInputStyle.short,
                        max_length=100,
                    ),
                    disnake.ui.TextInput(
                        label="If you answered no, please explain why.",
                        custom_id="recommend_explanation",
                        style=TextInputStyle.paragraph,
                    ),
                    disnake.ui.TextInput(
                        label="What features do you want added?",
                        placeholder="Please list any features here.",
                        custom_id="features",
                        style=TextInputStyle.paragraph,
                    ),
                    disnake.ui.TextInput(
                        label="Any more notes?",
                        placeholder="If you have anything you are yet to say, please say it here!",
                        custom_id="notes",
                        style=TextInputStyle.paragraph,
                    )
                    ]
    )
    await inter.send(f"Opening the form!")
    try:
        modal_inter: disnake.ModalInteraction = await bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "feedback" and i.author.id == inter.author.id,
            timeout=300
        )
    except asyncio.TimeoutError:
        await inter.send(f"{inter.author.name} did not respond in time :(")
        return

    results = modal_inter.text_values
    response = f"Author: {inter.author.name}\n" \
               f"Author ID: {inter.author.id}\n" \
               f"Experience: {results['experience']}\n" \
               f"Recommend: {results['recommend']}\n" \
               f"Recommend Explanation: {results['recommend_explanation']}\n" \
               f"Features: {results['features']}\n" \
               f"Notes: {results['notes']}\n" \
               "--------------"

    with open('feedback.txt', 'a', encoding='utf-8') as f:
        f.write(response)

    await inter.send("Thank you for giving feedback!")

@bot.slash_command(name="dadjoke", description='Responds with a random dad joke')
async def dad_joke_slash(ctx):
    await dadjoke(ctx)

@bot.slash_command(name='wikipedia', description='Responds with a random wikipedia article')
async def wikipedia_slash(ctx):
    await wikipedia(ctx)

@bot.slash_command(name='check', description='Responds with information about a specific user')
async def check_slash(ctx, member: disnake.Member):  # obtains information about a person in the guild and sends it
    await check(ctx, member)

@bot.slash_command(name='rps', description='Starts a game of rock paper scissors')
async def rps_slash(ctx, opponent: disnake.Member):  # rock paper scissors game
    await rps(ctx, opponent)

@bot.slash_command(name='tictactoe', description='Starts a game of tic tac toe')
async def tictactoe_slash(ctx, opponent: disnake.Member):  # tic tac toe game
    await tictactoe(ctx, opponent)

@bot.slash_command(name='help', description='Sends a help menu')
async def help_slash(ctx, category=None):
    await help(ctx, category)

@bot.slash_command(name="pokemon", description="Flips a coin")
async def pokemon_slash(ctx, name=None):
    print(name)
    await pokemon(ctx, name)

@bot.slash_command(name='flip', description='Flips a coin')
async def flip_slash(ctx):
    await flip(ctx)

@bot.slash_command(name='roll', description='Rolls the dice')
async def roll_command(ctx, user_roll):
    await roll(ctx, user_roll)

# end of re-implementation of commands as slash commands

bot.loop.create_task(status())
bot.run(token)
