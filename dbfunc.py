# Database
import sqlite3

def initialiseTable():
    conn = sqlite3.connect('floornftdb.db')

    # Run once to generate SQLite where necessary
    conn.execute('''CREATE TABLE NFTFLOORPRICE
                (ID INT PRIMARY KEY NOT NULL,
                NAME TEXT NOT NULL,
                PRICE DECIMAL NOT NULL,
                COLLECTION_NAME TEXT NOT NULL,
                COLLECTION_ID TEXT NOT NULL,
                IMG_URL TEXT NOT NULL,
                MINT_ADDRESS TEXT NOT NULL,
                MAGICEDEN_URL TEXT NOT NULL);''')
    
    conn.close()

def fetchAllNftsFromDB():
    conn = sqlite3.connect('floornftdb.db')
    nftList = []
    # Fetch Database and store database in Array of Objects
    cursor = conn.execute("SELECT * FROM NFTFLOORPRICE")
    for item in cursor:
        nft = {
            'id' : item[0],
            'name' : item[1],
            'price' : item[2],
            'collection_name' : item[3],
            'collection_id' : item[4],
            'img_url' : item[5],
            'mint_address' : item[6],
            'magiceden_url' : item[7]
        }

        nftList.append(nft)
    
    conn.close()
    return nftList

def insertNftToDB(nft):
    conn = sqlite3.connect('floornftdb.db')

    conn.execute("INSERT INTO NFTFLOORPRICE VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (
        nft['id'],
        nft['name'],
        nft['price'],
        nft['collection_name'],
        nft['collection_id'],
        nft['img_url'],
        nft['mint_address'],
        nft['magiceden_url'],
    ))

    conn.commit()
    conn.close()

def clearNFTTable():
    conn = sqlite3.connect('floornftdb.db')

    conn.execute("DELETE FROM NFTFLOORPRICE")

    conn.commit()
    conn.close()