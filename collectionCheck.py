# Requests & Environment
import json
from dotenv import load_dotenv
import os

# Selenium
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from dbfunc import *

# Discord
import discord
import asyncio

# Logging
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

initialiseNewDB = False
clearAllNFTs = False

# def configureLogging():
#     logFormatter = logging.Formatter("%(levelname)s - %(asctime)s --> %(message)s")
    
#     fileHandler = RotatingFileHandler("logs/output.log", mode="a+", maxBytes=10*1024*1024, backupCount=3)
#     # fileHandler = RotatingFileHandler("/home/app/logs/output.log", mode="a+", maxBytes=10*1024*1024, backupCount=3)
#     fileHandler.setFormatter(logFormatter)
#     streamHandler = logging.StreamHandler()
#     streamHandler.setFormatter(logFormatter)

#     log = logging.getLogger()
#     log.setLevel(print)
#     log.addHandler(streamHandler)
#     log.addHandler(fileHandler)

# configureLogging()

SYMBOLS = [
    "<:minor_1:979342488915562576><:minor_2:979342488735211610><:minor_3:979342488777134080>", # Minor 
    "<:medium_1:979343003497955328><:medium_2:979343003015581720><:medium_3:979343003690889216>", # Medium
    "<:major_1:979343232402092072><:major_2:979343232125247529><:major_3:979343232041377864>", # Major
    "<:extreme_1:979343381765451776><:extreme_2:979343382159700018><:extreme_3:979343382033858600>"  # Extreme
    ]

def setNFTData(data):
    nft = {
        'id' : data['id'],
        'name' : data['title'],
        'price' : data['price'],
        'collection_name' : data['collectionTitle'],
        'collection_id' : data['collectionName'],
        'img_url' : data['img'],
        'mint_address' : data['mintAddress'],
        'magiceden_url' : f'https://magiceden.io/item-details/{data["mintAddress"]}'
    }

    return nft

def getTelescanView(percentage):
    val = abs(percentage)

    if(val >= 0 and val < 5):
        indication = SYMBOLS[0]
    elif(val >= 5 and val < 10):
        indication = SYMBOLS[1]
    elif(val >= 10 and val < 25):
        indication = SYMBOLS[2]
    elif(val >= 25):
        indication = SYMBOLS[3]
    else:
        indication = "Error"

    return indication

# Convert the collection name into an API URL
def getAPIUrl(collection_name):
    url_first_half = 'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQueryLite?q={"$match":{"collectionSymbol":"'
    url_second_half = '"},"$sort":{"takerAmount":1},"$skip":0,"$limit":20,"status":[]}'
    return url_first_half + collection_name + url_second_half

def fetchNFTData(collection_name):
    # Make an attempt to get the API for that collection
    try:
        driver.get(getAPIUrl(collection_name))
    except:
        print(f'ERROR: Failed to fetch API for {collection_name}')
        return

    # Convert the JSON and get the NFT
    content = driver.page_source
    content = driver.find_element(By.TAG_NAME, 'pre').text
    parsed_json = json.loads(content)
    if(not parsed_json['results']):
        print(f"ERROR: No Results for {collection_name}")
        return

    # Set the NFT as the object
    nft = setNFTData(parsed_json['results'][0])
    return nft

async def main(bot):

    # clearNFTTable()

    collections = open("./collections.txt", "r").read().splitlines()
    
    storedNFTs = fetchAllNftsFromDB()
    # print(storedNFTs)

    while(True):
        for collection in collections:
            nft = fetchNFTData(collection)
            channel = bot.get_channel(977522354341163018)

            if nft in storedNFTs:
                print(f'No Changes to {nft["collection_name"]}')
                continue
            else:
                try:
                    index = storedNFTs.index(next(filter(lambda n : n.get('collection_id') == nft['collection_id'], storedNFTs)))
                    indexedNft = storedNFTs[index]

                    print(f'New NFT Floor of {nft["price"]} for {nft["collection_name"]}')

                    # Compare Prices
                    percentageDifference = round(float(((nft['price'] - indexedNft['price']) / indexedNft['price']) * 100), 2)
                    embedColour = discord.Colour.green() if percentageDifference >= 0 else discord.Colour.red()
                    telescanView = getTelescanView(percentageDifference)

                    # Database Functions
                    deleteNft(indexedNft['collection_id'])
                    insertNftToDB(nft)

                    # List Functions
                    del storedNFTs[index]
                    storedNFTs.append(nft)

                except:
                    print(f"New Collection Found: {nft['collection_name']}")

                    insertNftToDB(nft)
                    storedNFTs.append(nft)
                    indexedNft = {'price' : '-'}
                    percentageDifference = "- "
                    embedColour = discord.Colour.blue()
                    telescanView = "-"

            try:
                embed = discord.Embed(
                    title = f'**{nft["name"]}**',
                    url=nft['magiceden_url'],
                    description = nft['collection_name'],
                    # This value will change depending on the price change
                    colour = embedColour
                )

                embed.set_image(url=nft['img_url'])
                embed.set_thumbnail(url='https://i.ibb.co/BN39Xk9/telescanlogo.gif')
                embed.add_field(name='Price', value=f'{nft["price"]} SOL', inline=True)
                embed.add_field(name='Old Floor', value=f'{indexedNft["price"]} SOL', inline=True)
                embed.add_field(name='Value (%)', value=f'{percentageDifference}%', inline=True)
                embed.add_field(name=":telescanlogo~1: Verdict", value=f'{telescanView}', inline=True)
                embed.set_footer(text='Powered by Telescan Bots https://discord.gg/gkangJkUKT')

                await channel.send(embed=embed)
            except:
                print("ERROR: Unable to Send Message to Channel")
        
        await asyncio.sleep(10)

if __name__ == '__main__':
    if(initialiseNewDB):
        initialiseTable()
        print("Successfully Initialised The Database")
        os._exit(0)
    
    if(clearAllNFTs):
        clearNFTTable()
        print("Successfully Deleted All NFTs on DB")
        os._exit(0)

    # Set options for Chrome
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')

    # Create Driver
    driver = uc.Chrome(options=options)

    class MyClient(discord.Client):
        async def on_ready(self):
            print('[{0} HAS STARTED]'.format(self.user))
            await main(self)
    
    client = MyClient()
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
