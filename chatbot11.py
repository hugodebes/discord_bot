# IMPORT LIBRARIES

import os
import random
from dotenv import load_dotenv
import discord
from discord import Client, Intents
from discord.ext import commands
from discord_slash import ButtonStyle, SlashCommand
from discord_slash.utils.manage_components import *
import json
from urllib.request import urlopen
import wit
from wit import Wit
import asyncio

import nest_asyncio


nest_asyncio.apply()

# CREATE BOT

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GENERAL_CHANNEL = os.getenv('GENERAL_CHANNEL')
bot = commands.Bot(command_prefix="!",description='Books Bot')
slashn = "\n"

READ_RATE = []

####################################################################################
#********************************** HELP *****************************************# ####################################################################################

bot.remove_command('help')
@bot.group(invoke_without_command=True)
async def help(ctx):
  await ctx.send("**COMMAND HELPER** \n*don't forget the `!` before each command* \n\n`!books`\n❤️ Choose your preferences and create your profile \n`!memes` \n🤣 Display funny memes/gifs of books\n`!recommendation`\n🔖 We recommend you books with the list of books you have read and rated with the command **!books** or by the ones you told us\n`!isbn` \n🌐 Search for a specific book by its ISBN(International Standard Book Number), based upon a 13-digit Standard Book Numbering.\n *Example ->* If i want more information about the book Harry potter (ISBN-13:9782070541270) i will type : **!isbn 9782070541270**\n`!title`\n 📖 Display a chosen number of books containing the input in their title. You may find some books you never heard of before.\n*Example ->* If you want more information about the book The Hobbit you can type : **!title The Hobbit**\n`!author`\n🖋️ Display a chosen number of books written by the author with their title, published date, ISBN, description, page count and picture\n*Example ->* If you want books written by Ian Fleming you can type :**!author Ian Fleming**\n`!new`\n📚 Display a chosen number of the last books written by the author with their title, published date, ISBN, description, page count and picture if they exist\n*Example ->* If you want the last written books by Stephen King you can type : **!new Stephen King** \n\n**MESSAGE**\n\n You can also send simple messages and ask questions that we will be happy to answer like :\n- I want some information about the book/author ...\n - Can you give me some information about the book/author ...\n\nYou may also tell us what books you have read and rate them on a scale from 1 to 5 like :\n- I read Hunger Games and i would give it a 3\n- I read Harry Potter (we will then ask you to rate it)")

####################################################################################
#******************************** EVENTS *****************************************# ####################################################################################

@bot.event
async def on_ready():
  general_channel : discord.TextChannel = bot.get_channel(int(GENERAL_CHANNEL))
  print('The Book Bot is connected')
  await general_channel.send(content='The **Books Bot** is connected 📚 ! \n Type `!help` to see the comands')
  await general_channel.send("https://c.tenor.com/zuUY55sg8PQAAAAC/books.gif")

@bot.event
async def on_member_join(member):
  general_channel:discord.TextChannel = bot.get_channel(GENERAL_CHANNEL)
  await general_channel.send(content=f"Bienvenue sur le serveur {member.display_name}!")


tok='EJLUTVGF2O4FO3STSXJA5FS6LKNAJT2U'
client = Wit(tok)

@bot.event
async def on_message(message):
  if message.content.lower().startswith(("hi", "hey", "hello")) and message.author.name != "BooksBot":
    channel = message.channel
    await channel.send(f'Hi {message.author.name} ! Nice to see you 👋')

  resp = client.message(message.content)
  print(message.content)
  wit_info = get_infos(resp)
  print(wit_info[0])

  if wit_info[0] == ['book_infos'] and message.author.name != "BooksBot":
    channel = message.channel
    msg = wit_info[1][0]["book_entity"]
    msg = msg.split()
    title = '.'.join(msg)
    api = "https://www.googleapis.com/books/v1/volumes?q=intitle:"
    resp = urlopen(api + title)
    book_data = json.load(resp)
    compteur = 1
    limit=1
    for books in book_data["items"] :
      display = False
      try :
        img = books["volumeInfo"]["imageLinks"]["thumbnail"]
        desc = books["volumeInfo"]["description"]
        display = True   
        if len(desc)> 2000:
          display = False
        print("interesting")
      except : 
        print("not interesting")
  
      if display == True:
        img = books["volumeInfo"]["imageLinks"]["thumbnail"]
        await channel.send(img)
        
        title = books["volumeInfo"]["title"]
        author = books["volumeInfo"]["authors"][0]
        date = books["volumeInfo"]["publishedDate"]
        isbn = books["volumeInfo"]["industryIdentifiers"][1]["identifier"]
        pages = books["volumeInfo"]["pageCount"]   
        desc = books["volumeInfo"]["description"]
   
        await channel.send(f"**📕 Title**: {title} \n**✒️ Author**: {author}\n**📆 Published date**: {date}\n**🌐 ISBN**: {isbn} \n📃 **Page count**: {pages}")
        await channel.send(f"**💬 Description**:{desc}")
        
      
        if compteur == limit:
          break;
        else :
          compteur += 1

  if wit_info[0] == ['author_infos'] and not(message.content.startswith("!author")) and message.author.name != "BooksBot":
    channel = message.channel
    msg = wit_info[1][0]["author_entity"]
    msg = msg.split()
    await channel.send(f"📚  Here are 3 books that `{' '.join(msg)}` wrote \n| \n|")
    author = '.'.join(msg)
    api = "https://www.googleapis.com/books/v1/volumes?q=inauthor:"
    resp = urlopen(api + author)
    book_data = json.load(resp)
    compteur = 1
    limit=3
    for books in book_data["items"] :
      display = False
      try :
        img = books["volumeInfo"]["imageLinks"]["thumbnail"]
        desc = books["volumeInfo"]["description"]
        display = True   
        if len(desc)> 2000:
          display = False
        print("interesting")
      except : 
        print("not interesting")
  
      if display == True:
        title = books["volumeInfo"]["title"]
        author = books["volumeInfo"]["authors"][0]
        date = books["volumeInfo"]["publishedDate"]
        isbn = books["volumeInfo"]["industryIdentifiers"][1]["identifier"]
        pages = books["volumeInfo"]["pageCount"]   
        desc = books["volumeInfo"]["description"]

        await channel.send(f"*** BOOKS #{compteur} ***")
        img = books["volumeInfo"]["imageLinks"]["thumbnail"]
        await channel.send(img)
        await channel.send(f"**📕 Title**: {title} \n**✒️ Author**: {author}\n**📆 Published date**: {date}\n**🌐 ISBN**: {isbn} \n📃 **Page count**: {pages}")
        await channel.send(f"**💬 Description**:{desc}")
        
      
        if compteur == limit:
          break;
        else :
          compteur += 1
        await channel.send("--------------------------------------------------------------")
    
  if wit_info[0] == ['already_read'] and message.author.name != "BooksBot":
    channel = message.channel
    print(wit_info[1])
    if wit_info[1] == []:
      await channel.send("I dont understand what you have read")
    else :
      try :
        title = wit_info[1][1]['book_entity']
        rate = wit_info[1][0]['rate']
        rating = [title,rate]
        READ_RATE.append(rating)
        await channel.send(f"Thank you for your rating ! (you gave {rate}⭐ to the book *{title}*)\n We'll add this book review to the list to adjust your preferences and give you better recommendations 😉")
      except :
        title = wit_info[1][0]['book_entity']
        stars = [
          create_button(style=ButtonStyle.grey,label='⭐',custom_id='1'),
          create_button(style=ButtonStyle.grey,label='⭐⭐',custom_id='2'),
          create_button(style=ButtonStyle.grey,label='⭐⭐⭐',custom_id='3'),
          create_button(style=ButtonStyle.grey,label='⭐⭐⭐⭐',custom_id='4'),
          create_button(style=ButtonStyle.grey,label='⭐⭐⭐⭐⭐',custom_id='5')
        ]
        action_row = create_actionrow(*stars)
        fait_choix = await channel.send(content="How much would you rate it ?", components=[action_row])
        button_ctx = await wait_for_component(bot, components=action_row)
        await button_ctx.edit_origin(content=f"Got it, thank you for your rating (you gave {button_ctx.custom_id}⭐ for the book **{title}**)")
        rating = [title,button_ctx.custom_id]
        READ_RATE.append(rating)
        
        
      
      
  else :
    if message.author.name != "BooksBot" and message.content != "!help" and message.content !="!memes" and message.content !="!books" and not(message.content.startswith("!isbn")) and not(message.content.startswith("!title")) and not(message.content.startswith("!author")) and not(message.content.startswith("!new")) and wit_info[0]==[] and wit_info not in [['already_read'],['author_infos'],['book_infos']]:
      channel = message.channel
      await channel.send("I'm sorry, I didn't understand what you said 🙁\nPlease use the `!help` command to guide you")
      

  await bot.process_commands(message)


####################################################################################
#********************************** ISBN *****************************************# ####################################################################################

@bot.command(help='isbn')
async def isbn(ctx,isbn):
  api = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
  resp = urlopen(api + isbn)
  book_data = json.load(resp)
  books = book_data["items"][0]
  title = books["volumeInfo"]["title"]
  author = books["volumeInfo"]["authors"][0]
  date = books["volumeInfo"]["publishedDate"]
  pages = books["volumeInfo"]["pageCount"]   
  try : 
    desc = books["volumeInfo"]["description"]
    if len(desc)>2000:
      desc = "/"
  except :
    desc = "/"
  try :
    rating = books["volumeInfo"]["averageRating"]
  except :
    rating = "/" 
  try :
    cat = books["volumeInfo"]["categories"]
  except :
    cat = "/"
  try :
    img = books["volumeInfo"]["imageLinks"]["thumbnail"]
  except : 
    img = ""
  try:
    await ctx.send(img)
  except :
    print("no pics")
  await ctx.send(f"**📕 Title**: {title} \n**✒️ Author**: {author}\n**📆 Published date**: {date} \n**📌  Categories**: {cat}\n📃 **Page count**: {pages}\n**💯 Average rating**: {rating}\n**💬 Description**: {desc} ")
  

####################################################################################
#************************************* NEW ***************************************# ####################################################################################

@bot.command(help='author')
async def new(ctx):
  msg = ctx.message.content
  msg = msg.split()
  del msg[0]
  author = '.'.join(msg)
  api = "https://www.googleapis.com/books/v1/volumes?q=inauthor:"
  max = "&maxResults=40"
  order = "&orderBy=newest"
  resp = urlopen(api + author + max + order)
  book_data = json.load(resp)
  nbooks = [
    create_button(style=ButtonStyle.grey,label='3',custom_id='3'),
    create_button(style=ButtonStyle.grey,label='5',custom_id='5'),
    create_button(style=ButtonStyle.grey,label='8',custom_id='8'),
    create_button(style=ButtonStyle.grey,label='10',custom_id='10'),
  ]
  nb = len(book_data["items"])
  await ctx.send(f"📚  We found **{nb} books** of `{' '.join(msg)}`")
  action_row = create_actionrow(*nbooks)
  fait_choix = await ctx.send("How many books do you want to see from this author ?", components=[action_row])
  def check(m):
    return m.author_id == ctx.author.id and m.origin_message.id == fait_choix.id
  button_ctx = await wait_for_component(bot, components=action_row, check=check)
  limit = int(button_ctx.custom_id)
  await button_ctx.edit_origin(content="Got it !")
  compteur = 1
  for books in book_data["items"] :
    title = books["volumeInfo"]["title"]
    date = books["volumeInfo"]["publishedDate"]
    isbn = books["volumeInfo"]["industryIdentifiers"][1]["identifier"]
    try:
      pages = books["volumeInfo"]["pageCount"]   
    except:
      pages="/"
    try : 
      desc = books["volumeInfo"]["description"]
      if len(desc)>2000:
        desc = "/"
    except :
      desc = "/"
    try :
      rating = books["volumeInfo"]["averageRating"]
    except :
      rating = "/"     
    try :
      cat = books["volumeInfo"]["categories"]
    except :
      cat = "/"  
    await ctx.send(f"*** BOOKS #{compteur} ***")
    try:
      await ctx.send(img)
    except :
      print("no pics")
    await ctx.send(f"**📕 Title**: {title} \n**📆 Published date**: {date} \n**📌  Categories**: {cat}\n**🌐 ISBN**: {isbn} \n📃 **Page count**: {pages}\n**💯 Average rating**: {rating}\n**💬 Description**: {desc} ")
    try :
      img = books["volumeInfo"]["imageLinks"]["thumbnail"]
    except : 
      img = ""
    
    await ctx.send("--------------------------------------------------------------")
    
    if compteur == limit:
      break;
    else :
      compteur += 1
  
####################################################################################
#********************************** AUTHOR ***************************************# ####################################################################################

@bot.command(help='author')
async def author(ctx):
  msg = ctx.message.content
  msg = msg.split()
  del msg[0]
  author = '.'.join(msg)
  api = "https://www.googleapis.com/books/v1/volumes?q=inauthor:"
  max = "&maxResults=40"
  resp = urlopen(api + author + max)
  print(api+author)
  book_data = json.load(resp)
  nbooks = [
    create_button(style=ButtonStyle.grey,label='3',custom_id='3'),
    create_button(style=ButtonStyle.grey,label='5',custom_id='5'),
    create_button(style=ButtonStyle.grey,label='8',custom_id='8'),
    create_button(style=ButtonStyle.grey,label='10',custom_id='10'),
  ]
  nb = len(book_data["items"])
  await ctx.send(f"📚  We found **{nb} books** of `{' '.join(msg)}`")
  action_row = create_actionrow(*nbooks)
  fait_choix = await ctx.send("How many books do you want to see from this author ?", components=[action_row])
  def check(m):
    return m.author_id == ctx.author.id and m.origin_message.id == fait_choix.id
  button_ctx = await wait_for_component(bot, components=action_row, check=check)
  limit = int(button_ctx.custom_id)
  await button_ctx.edit_origin(content="Got it !")
  compteur = 1
  for books in book_data["items"] :
    display = False
    try :
      img = books["volumeInfo"]["imageLinks"]["thumbnail"]
      desc = books["volumeInfo"]["description"]
      rating = books["volumeInfo"]["averageRating"]
      cat = books["volumeInfo"]["categories"]
      isbn = books["volumeInfo"]["industryIdentifiers"][1]["identifier"]
      display = True   
      if len(desc)> 2000:
        display = False
      print("interesting")
    except : 
      print("not interesting")

    if display == True:
      title = books["volumeInfo"]["title"]
      date = books["volumeInfo"]["publishedDate"]
      isbn = books["volumeInfo"]["industryIdentifiers"][1]["identifier"]
      pages = books["volumeInfo"]["pageCount"]   
      desc = books["volumeInfo"]["description"]
      rating = books["volumeInfo"]["averageRating"]
      cat = books["volumeInfo"]["categories"]

      await ctx.send(f"*** BOOKS #{compteur} ***")
      img = books["volumeInfo"]["imageLinks"]["thumbnail"]
      await ctx.send(img)
      await ctx.send(f"**📕 Title**: {title} \n**📆 Published date**: {date} \n**📌  Categories**: {cat}\n**🌐 ISBN**: {isbn} \n📃 **Page count**: {pages}\n**💯 Average rating**: {rating} ")
      await ctx.send(f"**💬 Description**:{desc}")
      
      await ctx.send("--------------------------------------------------------------")
    
      if compteur == limit:
        break;
      else :
        compteur += 1

####################################################################################
#************************************ TITLE ***************************************# ####################################################################################

@bot.command(help='title')
async def title(ctx):
  msg = ctx.message.content
  msg = msg.split()
  del msg[0]
  title = '.'.join(msg)
  api = "https://www.googleapis.com/books/v1/volumes?q=intitle:"
  max = "&maxResults=40"
  resp = urlopen(api + title + max)
  book_data = json.load(resp)
  nbooks = [
    create_button(style=ButtonStyle.grey,label='3',custom_id='3'),
    create_button(style=ButtonStyle.grey,label='5',custom_id='5'),
    create_button(style=ButtonStyle.grey,label='8',custom_id='8'),
    create_button(style=ButtonStyle.grey,label='10',custom_id='10'),
  ]
  nb = len(book_data["items"])
  await ctx.send(f"📚  We found **{nb} books** with `{' '.join(msg)}` in the title")
  action_row = create_actionrow(*nbooks)
  fait_choix = await ctx.send(f"How many books do you want to see with {' '.join(msg)} in the title ?", components=[action_row])
  def check(m):
    return m.author_id == ctx.author.id and m.origin_message.id == fait_choix.id
  button_ctx = await wait_for_component(bot, components=action_row, check=check)
  limit = int(button_ctx.custom_id)
  await button_ctx.edit_origin(content="Got it !")
  compteur = 1
  for books in book_data["items"] :
    display = False
    try :
      img = books["volumeInfo"]["imageLinks"]["thumbnail"]
      desc = books["volumeInfo"]["description"]
      rating = books["volumeInfo"]["averageRating"]
      cat = books["volumeInfo"]["categories"]
      isbn = books["volumeInfo"]["industryIdentifiers"][1]["identifier"]
      display = True   
      if len(desc)> 2000:
        display = False
      print("interesting")
    except : 
      print("not interesting")

    if display == True:
      title = books["volumeInfo"]["title"]
      author = books["volumeInfo"]["authors"][0]
      date = books["volumeInfo"]["publishedDate"]
      isbn = books["volumeInfo"]["industryIdentifiers"][1]["identifier"]
      pages = books["volumeInfo"]["pageCount"]   
      desc = books["volumeInfo"]["description"]
      rating = books["volumeInfo"]["averageRating"]
      cat = books["volumeInfo"]["categories"]

      await ctx.send(f"*** BOOKS #{compteur} ***")
      img = books["volumeInfo"]["imageLinks"]["thumbnail"]
      await ctx.send(img)
      await ctx.send(f"**📕 Title**: {title} \n**✒️ Author**: {author}\n**📆 Published date**: {date} \n**📌  Categories**: {cat}\n**🌐 ISBN**: {isbn} \n📃 **Page count**: {pages}\n**💯 Average rating**: {rating} ")
      await ctx.send(f"**💬 Description**:{desc}")
      
      await ctx.send("--------------------------------------------------------------")
    
      if compteur == limit:
        break;
      else :
        compteur += 1
  
####################################################################################
#********************************* MEMES *****************************************# ####################################################################################

@bot.command(help='🤣 Display funny memes/gifs of books')
async def memes(ctx):
  memes = [
    "https://img.buzzfeed.com/buzzfeed-static/static/2017-03/23/15/asset/buzzfeed-prod-fastlane-01/sub-buzz-27949-1490298158-6.jpg?downsize=900:*&output-format=auto&output-quality=auto",
     
     "https://theawesomedaily.com/wp-content/uploads/2017/12/book-lover-memes-feat-1.jpg",
     
     "https://i.pinimg.com/originals/ac/55/ce/ac55ce736b44b0ec7ed58361bfff6720.jpg",
     "https://www.liveabout.com/thmb/yseGHDZkhOc3EUv9AA99NdL8EzI=/640x651/filters:no_upscale():max_bytes(150000):strip_icc()/book-memes-1-5c52056bc9e77c0001859bcb.jpg",
     "https://cdn.shortpixel.ai/spai/w_924+q_lossy+ret_img+to_webp/https://www.hookedtobooks.com/wp-content/uploads/2019/08/You-live-in-the-real-world.jpg",
     
    "https://imgix.ranker.com/user_node_img/50105/1002096010/original/1002096010-photo-u1?auto=format&q=60&fit=crop&fm=pjpg&dpr=2&w=375",

     "https://media3.giphy.com/media/WoWm8YzFQJg5i/giphy.gif",

     "https://media0.giphy.com/media/NFA61GS9qKZ68/200.gif",

     "https://data.whicdn.com/images/171224962/original.gif",

     "https://bestanimations.com/media/books/934435559spongebob-reading-book-animation.gif"]
  messages = await ctx.channel.history(limit=1).flatten()
  for each_message in messages:
    await each_message.delete()
  index = random.randint(0,len(memes))
  await ctx.send(memes[index])

  

####################################################################################
#********************************* BOOKS *****************************************# ####################################################################################

@bot.command(help='❤️ Choose your preferences and create your profile')
async def books(ctx):
  
############## DATA ################################

  category = ['Dystopian 💀','Science-fiction 🚀','Fiction 💭','Fantasy 🐉','Romance 💌','Adult 👫','Contemporary 📆','Young Adult 🍪','Mystery 🔎','Classics 🖋️','Non-fiction 📰','Adventure 💥','Historical 📽️','Crime 🔪']

  topfive = {
'Adult 👫': [
  {'author': 'George R.R. Martin','book_id': 39,'link': 'https://images.gr-assets.com/books/1436732693m/13496.jpg','title': 'A Game of Thrones'},
  {'author': 'Kathryn Stockett','book_id': 31,'link': 'https://images.gr-assets.com/books/1346100365m/4667024.jpg','title': 'The Help'},
  {'author': 'Paula Hawkins','book_id': 61,'link': 'https://images.gr-assets.com/books/1490903702m/22557272.jpg','title': 'The Girl on the Train'},
  {'author': 'E.L. James','book_id': 96,'link': 'https://images.gr-assets.com/books/1336418837m/13536860.jpg','title': 'Fifty Shades Freed'},
  {'author': 'Erin Morgenstern','book_id': 185,'link': 'https://images.gr-assets.com/books/1387124618m/9361589.jpg','title': 'The Night Circus'}],

'Adventure 💥': [
  {'author': 'Suzanne Collins','book_id': 1,'link': 'https://images.gr-assets.com/books/1447303603m/2767052.jpg','title': 'The Hunger Games'},
  {'author': 'J.R.R. Tolkien','book_id': 7,'link': 'https://images.gr-assets.com/books/1372847500m/5907.jpg','title': 'The Hobbit or There and Back Again'},
  {'author': 'Suzanne Collins', 'book_id': 17,'link': 'https://images.gr-assets.com/books/1358273780m/6148028.jpg','title': 'Catching Fire'},
  {'author': 'J.K. Rowling, Mary GrandPré','book_id': 2,'link': 'https://images.gr-assets.com/books/1474154022m/3.jpg','title': "Harry Potter and the Philosopher's Stone"},
  {'author': 'Suzanne Collins', 'book_id': 20,'link': 'https://images.gr-assets.com/books/1358275419m/7260188.jpg','title': 'Mockingjay'}],

'Classics 🖋️': [
  {'author': 'Jane Austen','book_id': 10,'link': 'https://images.gr-assets.com/books/1320399351m/1885.jpg','title': 'Pride and Prejudice'},
  {'author': 'F. Scott Fitzgerald','book_id': 5, 'link': 'https://images.gr-assets.com/books/1490528560m/4671.jpg','title': 'The Great Gatsby'},
  {'author': 'Harper Lee','book_id': 4,'link': 'https://images.gr-assets.com/books/1361975680m/2657.jpg','title': 'To Kill a Mockingbird'},
  {'author': 'Emily Brontë, Richard J. Dunn','book_id': 63,'link': 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png','title': 'Wuthering Heights'},
  {'author': 'J.D. Salinger','book_id': 8,'link': 'https://images.gr-assets.com/books/1398034300m/5107.jpg','title': 'The Catcher in the Rye'}],

'Crime 🔪': [
  {'author': 'Stieg Larsson, Reg Keeland','book_id': 16,'link': 'https://images.gr-assets.com/books/1327868566m/2429135.jpg','title': 'Män som hatar kvinnor'},
  {'author': 'Stieg Larsson, Reg Keeland','book_id': 98,'link': 'https://images.gr-assets.com/books/1351778881m/5060378.jpg','title': 'Flickan som lekte med elden'},
  {'author': 'Gillian Flynn','book_id': 30,'link': 'https://images.gr-assets.com/books/1339602131m/8442457.jpg','title': 'Gone Girl'},
  {'author': 'Stieg Larsson, Reg Keeland','book_id': 140,'link': 'https://images.gr-assets.com/books/1327708260m/6892870.jpg','title': 'Luftslottet som sprängdes'},
  {'author': 'Robert Galbraith, J.K. Rowling','book_id': 253,'link': 'https://images.gr-assets.com/books/1358716559m/16160797.jpg','title': "The Cuckoo's Calling"}],

'Dystopian 💀': [
  {'author': 'Suzanne Collins','book_id': 1,'link': 'https://images.gr-assets.com/books/1447303603m/2767052.jpg','title': 'The Hunger Games'},
  {'author': 'Veronica Roth','book_id': 12,'link': 'https://images.gr-assets.com/books/1328559506m/13335037.jpg','title': 'Divergent'},
  {'author': 'Suzanne Collins','book_id': 20,'link': 'https://images.gr-assets.com/books/1358275419m/7260188.jpg','title': 'Mockingjay'},
  {'author': 'Veronica Roth','book_id': 69,'link': 'https://images.gr-assets.com/books/1325667729m/11735983.jpg','title': 'Insurgent'},
  {'author': 'Veronica Roth','book_id': 105,'link': 'https://images.gr-assets.com/books/1395582745m/18710190.jpg','title': 'Allegiant'}],

'Fantasy 🐉': [
  {'author': 'J.K. Rowling, Mary GrandPré','book_id': 2,'link': 'https://images.gr-assets.com/books/1474154022m/3.jpg','title': "Harry Potter and the Philosopher's Stone"},
  {'author': 'J.R.R. Tolkien','book_id': 7,'link': 'https://images.gr-assets.com/books/1372847500m/5907.jpg','title': 'The Hobbit or There and Back Again'},
  {'author': 'J.K. Rowling, Mary GrandPré','book_id': 23,'link': 'https://images.gr-assets.com/books/1474169725m/15881.jpg','title': 'Harry Potter and the Chamber of Secrets'},
  {'author': 'J.K. Rowling, Mary GrandPré, Rufus Beck','book_id': 18,'link': 'https://images.gr-assets.com/books/1499277281m/5.jpg','title': 'Harry Potter and the Prisoner of Azkaban'},
  {'author': 'J.K. Rowling, Mary GrandPré','book_id': 24,'link': 'https://images.gr-assets.com/books/1361482611m/6.jpg','title': 'Harry Potter and the Goblet of Fire'}],

'Fiction 💭': [
  {'author': 'F. Scott Fitzgerald','book_id': 5,'link': 'https://images.gr-assets.com/books/1490528560m/4671.jpg','title': 'The Great Gatsby'},
  {'author': 'George Orwell, Erich Fromm, Celâl Üster','book_id': 13,'link': 'https://images.gr-assets.com/books/1348990566m/5470.jpg','title': 'Nineteen Eighty-Four'},
  {'author': 'Suzanne Collins','book_id': 1,'link': 'https://images.gr-assets.com/books/1447303603m/2767052.jpg','title': 'The Hunger Games'},
  {'author': 'Dan Brown','book_id': 26,'link': 'https://images.gr-assets.com/books/1303252999m/968.jpg','title': 'The Da Vinci Code'},
  {'author': 'J.D. Salinger','book_id': 8,'link': 'https://images.gr-assets.com/books/1398034300m/5107.jpg','title': 'The Catcher in the Rye'}],

'Historical 📽️': [
  {'author': 'Markus Zusak','book_id': 47,'link': 'https://images.gr-assets.com/books/1390053681m/19063.jpg','title': 'The Book Thief'},
  {'author': 'Anthony Doerr','book_id': 143,'link': 'https://images.gr-assets.com/books/1451445646m/18143977.jpg','title': 'nan'},
  {'author': 'Diana Gabaldon','book_id': 137,'link': 'https://images.gr-assets.com/books/1402600310m/10964.jpg','title': 'Outlander'},
  {'author': 'Kathryn Stockett','book_id': 31,'link': 'https://images.gr-assets.com/books/1346100365m/4667024.jpg','title': 'The Help'},
  {'author': 'Ken Follett','book_id': 142,'link': 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png','title': 'The Pillars of the Earth'}],

'Mystery 🔎': [
  {'author': 'Stieg Larsson, Reg Keeland','book_id': 16,'link': 'https://images.gr-assets.com/books/1327868566m/2429135.jpg','title': 'Män som hatar kvinnor'},
  {'author': 'Agatha Christie','book_id': 200,'link': 'https://images.gr-assets.com/books/1391120695m/16299.jpg','title': 'Ten Little Niggers'},
  {'author': 'Gillian Flynn','book_id': 30,'link': 'https://images.gr-assets.com/books/1339602131m/8442457.jpg','title': 'Gone Girl'},
  {'author': 'Paula Hawkins','book_id': 61,'link': 'https://images.gr-assets.com/books/1490903702m/22557272.jpg','title': 'The Girl on the Train'},
  {'author': 'Agatha Christie','book_id': 672,'link': 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png','title': 'Murder in the Calais Coach'}],

'Non-fiction 📰': [
  {'author': 'Anne Frank, Eleanor Roosevelt, B.M. Mooyaart-Doubleday','book_id': 15,'link': 'https://images.gr-assets.com/books/1358276407m/48855.jpg','title': 'Het Achterhuis: Dagboekbrieven 14 juni 1942 - 1 augustus 1944'},
  {'author': 'Rebecca Skloot','book_id': 208,'link': 'https://images.gr-assets.com/books/1327878144m/6493208.jpg','title': 'The Immortal Life of Henrietta Lacks'},
  {'author': 'Jon Krakauer','book_id': 82,'link': 'https://images.gr-assets.com/books/1403173986m/1845.jpg','title': 'Into the Wild'},
  {'author': 'Malcolm Gladwell','book_id': 127,'link': 'https://images.gr-assets.com/books/1473396980m/2612.jpg','title': 'The Tipping Point: How Little Things Can Make a Big Difference'}],

'Romance 💌': [
  {'author': 'Jane Austen','book_id': 10,'link': 'https://images.gr-assets.com/books/1320399351m/1885.jpg','title': 'Pride and Prejudice'},
  {'author': 'John Green','book_id': 6,'link': 'https://images.gr-assets.com/books/1360206420m/11870085.jpg','title': 'The Fault in Our Stars'},
  {'author': 'Stephenie Meyer','book_id': 49,'link': 'https://images.gr-assets.com/books/1361039440m/49041.jpg','title': 'New Moon (Twilight, #2)'},
  {'author': 'Stephenie Meyer','book_id': 52,'link': 'https://images.gr-assets.com/books/1361038355m/428263.jpg','title': 'Eclipse'},
  {'author': 'Diana Gabaldon','book_id': 137,'link': 'https://images.gr-assets.com/books/1402600310m/10964.jpg','title': 'Outlander'}],

'Science-fiction 🚀': [
  {'author': 'Orson Scott Card','book_id': 70,'link': 'https://images.gr-assets.com/books/1408303130m/375802.jpg','title': "Ender's Game"},
  {'author': 'Douglas Adams','book_id': 54,'link': 'https://images.gr-assets.com/books/1327656754m/11.jpg','title': "The Hitchhiker's Guide to the Galaxy"},
  {'author': 'Frank Herbert','book_id': 126,'link': 'https://images.gr-assets.com/books/1434908555m/234225.jpg','title': 'Dune'},
  {'author': 'Suzanne Collins','book_id': 1,'link': 'https://images.gr-assets.com/books/1447303603m/2767052.jpg','title': 'The Hunger Games'},
  {'author': 'Ray Bradbury','book_id': 48,'link': 'https://images.gr-assets.com/books/1351643740m/4381.jpg','title': 'Fahrenheit 451'}],

'Young Adult 🍪': [
  {'author': 'Suzanne Collins','book_id': 1,'link': 'https://images.gr-assets.com/books/1447303603m/2767052.jpg','title': 'The Hunger Games'},
  {'author': 'Suzanne Collins','book_id': 17,'link': 'https://images.gr-assets.com/books/1358273780m/6148028.jpg','title': 'Catching Fire'},
  {'author': 'Suzanne Collins','book_id': 20,'link': 'https://images.gr-assets.com/books/1358275419m/7260188.jpg','title': 'Mockingjay'},
  {'author': 'Veronica Roth','book_id': 12,'link': 'https://images.gr-assets.com/books/1328559506m/13335037.jpg','title': 'Divergent'},
  {'author': 'John Green','book_id': 6,'link': 'https://images.gr-assets.com/books/1360206420m/11870085.jpg','title': 'The Fault in Our Stars'}]

}
  


################## FIRST 5 CATEGORIES ###################################
  buttons = create_buttons(category)
  like = []
  action_row = create_actionrow(*buttons)
  await ctx.send("📋**CREATION OF THE USER PROFILE**\n\n**Notice**: We are going to create your user profile. You'll choose what kinds of books you prefer then we'll show you some books of the categories you chose and we will ask you if you have read those books.If you have, you'll rate them on a scale from 1 to 5.")
  fait_choix = await ctx.send("What kinds of books do you like ?", components=[action_row])
  def check(m):
    return m.author_id == ctx.author.id and m.origin_message.id == fait_choix.id
  button_ctx = await wait_for_component(bot, components=action_row, check=check)
  like.append(button_ctx.custom_id)

################# ALL CATEGORIES #########################################
  
  while button_ctx.custom_id != "Stop":
    
    #delete message
    messages = await ctx.channel.history(limit=1).flatten()
    for each_message in messages:
      await each_message.delete()

    #delete kind of book
    to_delete = button_ctx.custom_id
    for i in range (len(category)):
      if category[i] == to_delete:
        del category[i]
        break;

    buttons = create_buttons(category)
    
    #ask for other kind of books  
    action_row = create_actionrow(*buttons)
    fait_choix = await ctx.send("Other ones ?", components=[action_row])
    button_ctx = await wait_for_component(bot, components=action_row, check=check)
    like.append(button_ctx.custom_id)

  del like[len(like)-1]
  await button_ctx.send(f"Your preferences have been registered! \n You like {like}")
  await ctx.send("https://i.gifer.com/Ybin.gif")


#################### BOOKS LIKED IN THE CATEGORIES #############################

  
  await ctx.send("Now let's see what books have you `read` in the categories you liked ! 🔖 ")
  read_all = []
  yesno = [ create_button(style=ButtonStyle.green,label='yes',custom_id='yes'),create_button(style=ButtonStyle.red,label='no',custom_id='no')
  ]
  stars = [
    create_button(style=ButtonStyle.grey,label='⭐',custom_id='1'),
    create_button(style=ButtonStyle.grey,label='⭐⭐',custom_id='2'),
    create_button(style=ButtonStyle.grey,label='⭐⭐⭐',custom_id='3'),
    create_button(style=ButtonStyle.grey,label='⭐⭐⭐⭐',custom_id='4'),
    create_button(style=ButtonStyle.grey,label='⭐⭐⭐⭐⭐',custom_id='5')
  ]
  
  for cat in like:
    await ctx.send(f"---------------------------------------------------------------------------------------------------------- {slashn}{slashn} Here are 5 books you may have read in the category **{cat}**")
    for key,value in topfive.items():
      if key == cat:
        read = []
        for book in value:
          to_delete = 3
          
          await ctx.send(book['link'])
          await ctx.send(f"**Title** : {book['title']} {slashn}**Author** : {book['author']}")
          action_row = create_actionrow(*yesno)
          fait_choix = await ctx.send("Have you read this book ?", components=[action_row])
          def check(m):
            return m.author_id == ctx.author.id and m.origin_message.id == fait_choix.id
          button_ctx = await wait_for_component(bot, components=action_row, check=check)
          if button_ctx.custom_id == "yes":
            to_delete=4
            await button_ctx.edit_origin(content="Cool! Did you like it ?")
            action_row = create_actionrow(*stars)
            fait_choix = await ctx.send(content="How much would you rate it ?", components=[action_row])
            def check(m):
              return m.author_id == ctx.author.id and m.origin_message.id == fait_choix.id
            button_ctx2 = await wait_for_component(bot, components=action_row, check=check)
            await button_ctx2.edit_origin(content=f"Got it, thank you for your rating (you gave {button_ctx2.custom_id} ⭐ for this book)")
            book_like= [book['title'],button_ctx2.custom_id,book['book_id']]
            read.append(book_like)
            read_all.append(book_like)
            READ_RATE.append(book_like)
          else:
            await button_ctx.edit_origin(content="Too bad it's a great book")


          messages = await ctx.channel.history(limit=to_delete).flatten()
          for each_message in messages:
            await each_message.delete()
            
        summary = ""
        for b in read:
          summary += "➢ " + b[0] + " (" + b[1] + " ⭐)" + slashn
        
        await ctx.send(f"To summarize, in the category `{cat}` you read and rated : {slashn}{summary}{slashn}{slashn}")

        
  await ctx.send(read_all)

####################################################################################
#********************************** RECOMMAND *************************************# ####################################################################################

@bot.command(help='give recommendations')
async def recommendation(ctx):
  await ctx.send(READ_RATE)

  
###############FUNCTIONS TO HELP##########################################

def create_buttons (books):
  buttons = []
  number = 4
  if len(books)<4:
    number = len(books)
  indexes = random.sample(range(0,len(books)),number)
  for i in range(len(indexes)):
    button = create_button(style=ButtonStyle.blue,label=books[indexes[i]],custom_id=books[indexes[i]])
    buttons.append(button)   
  stop_button = create_button(style=ButtonStyle.danger,label="It's okay",custom_id="Stop")
  buttons.append(stop_button)
  return buttons

def get_infos(resp):
    intents=resp["intents"]
    intents_name=[]
    for i in range(len(intents)):
        name=resp["intents"][i]['name']
        c=resp["intents"][i]['confidence']
        #print(c)
        if(c>0.77):
          intents_name.append(name)
    entities=resp['entities'].keys()
    entities=list(entities)
    ent=[]
    for i in entities:
        i=i.split(':')
        i=i[0]
        ent.append(i)
    dic_entities=resp["entities"]
    best_entities=[]
    for i in range(len(entities)):
        conf=dic_entities[entities[i]][0]['confidence']
        if(conf>0.8):
            name=dic_entities[entities[i]][0]['name']
            body=dic_entities[entities[i]][0]['body']
            dic={}
            dic[name]=body
            best_entities.append(dic)
    if(len(intents_name)==0):
      print("Sorry, we didn't understand")
    return intents_name,best_entities

#client = discord.Client(intents=Intents.default())
loop = asyncio.get_event_loop()

task2 = loop.create_task(bot.run(TOKEN))
#task1 = loop.create_task(client.wait_until_ready())

gathered = asyncio.gather(task2, loop=loop)
loop.run_until_complete(gathered)