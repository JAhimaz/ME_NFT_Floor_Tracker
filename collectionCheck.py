# Requests & Environment
import json
from dotenv import load_dotenv
import os

# Selenium
import undetected_chromedriver as uc
from selenium import webdriver
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
                return
            else:
                print(f'New NFT Floor of {nft["price"]} for {nft["collection_name"]}')
                index = storedNFTs.index(next(filter(lambda n : n.get('collection_id') == nft['collection_id'], storedNFTs)))
                indexedNft = storedNFTs[index]
                # Compare Prices
                percentageDifference = round(float(((nft['price'] - indexedNft['price']) / indexedNft['price']) * 100), 2)
                
            
            # Test push NFT information
            # insertNftToDB(nft)

            # try:
            embed = discord.Embed(
                title = f'**{nft["name"]}**',
                url=nft['magiceden_url'],
                description = nft['collection_name'],
                # This value will change depending on the price change
                colour = discord.Colour.green() if percentageDifference >= 0 else discord.Colour.red()
            )

            embed.set_image(url=nft['img_url'])
            # embed.set_thumbnail(url=nft['img_url'])
            embed.add_field(name='Price', value=f'{nft["price"]} SOL', inline=True)
            embed.add_field(name='Value (%)', value=f'{percentageDifference}%', inline=True)
            embed.add_field(name='Old Floor', value=f'{indexedNft["price"]} SOL', inline=False)
            embed.set_footer(text='Powered by Telescan Bots https://discord.gg/gkangJkUKT')

            await channel.send(embed=embed)
            # except:
            #     print("ERROR: Unable to Send Message to Channel")
        
        await asyncio.sleep(5)
        

if __name__ == '__main__':
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
