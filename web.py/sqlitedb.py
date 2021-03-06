import web
from datetime import datetime
from auctionbase import string_to_time
db = web.database(dbn='sqlite', db='auctions.db')

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    return results[0].Time

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where itemID = $itemID'
    try:
        result = query(query_string, {'itemID': item_id})
        return result[0]
    except Exception as e:
        print str(e)

def getCategoriesForItemId(item_id):
    query_string = 'select Category from Categories where itemId = $itemID'
    try:
        result = query(query_string, {'itemID': item_id})
        return result
    except Exception as e:
        print str(e)

def getBidsForItemId(item_id):
    query_string = 'select UserID, Amount, Time from Bids where itemId = $itemID'
    try:
        result = query(query_string, {'itemID': item_id})
        return result
    except Exception as e:
        print str(e)

def getAuctionStatusForItemId(item_id):
    # TODO: needs to also check if the buy_price has been bidded, and if so, return 'Closed'
    query_string = 'select started, ends from Items where itemId = $itemID'
    currentTime = string_to_time(getTime())
    try:
        results = query(query_string, {'itemID': item_id})[0]
        startTime = string_to_time(results['Started'])
        endTime = string_to_time(results['Ends'])
        if currentTime < endTime and currentTime > startTime:
            return 'Open'
        elif currentTime >= endTime:
            return 'Closed'
        else:
            return 'Not Started'
    except Exception as e:
        print str(e)

def getWinnerForItemId(item_id):
    query_string = 'select UserID from Bids where ItemID = $itemID order by Amount DESC Limit 1'
    try:
        results = query(query_string, {'itemID': int(item_id)})
        return results[0]['UserID']
    except Exception as e:
        print str(e)

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return db.query(query_string, vars)

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time

def updateCurrentTime(time):
    t = transaction()
    query_string = 'UPDATE CurrentTime SET Time = $time'
    try:
        query(query_string, {'time': time})
    except Exception as e:
        t.rollback()
        print str(e)
        return False
    else:
        t.commit()

def addBid(itemID, UserID, amount, time):
    t = transaction()
    query_string = 'INSERT INTO Bids VALUES ($ItemID, $UserID, $Amount, $Time)'
    try:
        query(query_string, {'ItemID': itemID, 'UserID': UserID, 'Amount': amount, 'Time': time})
    except Exception as e:
        t.rollback()
        print str(e)
        return False
    else:
        try:
          t.commit()
          return True
        except Exception as e:
          t.rollback()
          print str(e)
          return False

def search(ItemID, UserID, minPrice, maxPrice, status, time, category, itemDescription):
    itemDescription = '%'+itemDescription+'%'
    t = transaction()
    if(category == ''):
      query_string = "SELECT * FROM Items i WHERE "
    else:
      query_string = "SELECT * FROM Items i, Categories c WHERE "
    if ItemID != '':
			query_string = query_string + "i.ItemID == $ItemID AND"
    if UserID != '':
			query_string = query_string + " i.Seller_UserID == $UserID AND"
    if minPrice != '':
			query_string = query_string + " i.Currently >= $minPrice AND"
    if maxPrice != '':
			query_string = query_string + " i.Currently <= $maxPrice AND"
    if category != '':
      query_string = query_string + " i.ItemID == c.ItemID AND c.Category == $category AND"
    if itemDescription != '':
      query_string = query_string + " i.Description LIKE $itemDescription AND"

    if str(status) == "notStarted":
			query_string = query_string + " i.Started > $time"
    elif str(status) == "close":
			query_string = query_string + " i.Ends < $time"
    elif str(status) == "open":
			query_string = query_string + " i.Started < $time AND i.Ends > $time"
    if(query_string.endswith(' AND')):
			query_string = query_string[:-3]
    if(query_string.endswith(' WHERE ')):
      query_string = query_string[:-6]
    try:
        q = query(query_string, {'ItemID': ItemID, 'UserID': UserID, 'minPrice': minPrice, 'maxPrice': maxPrice, 'status': status, 'time': time, 'category': category, 'itemDescription': itemDescription})
    except Exception as e:
        t.rollback()
        print str(e)
        return False
    else:
        t.commit()
        return q
