import web

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
    query_string = 'select * from Items where item_ID = $itemID'
    try:
        result = query(query_string, {'itemID': item_id})
        return result[0]
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
      query_string = "SELECT i.* FROM Items i WHERE "
    else:
      query_string = "SELECT i.* FROM Items i, Categories c WHERE "
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
      query_string = query_string + " i.Description LIKE $itemDescription"

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
    print query_string
    try:
        q = query(query_string, {'ItemID': ItemID, 'UserID': UserID, 'minPrice': minPrice, 'maxPrice': maxPrice, 'status': status, 'time': time, 'category': category, 'itemDescription': itemDescription})
    except Exception as e:
        t.rollback()
        print str(e)
        return False
    else:
        t.commit()
        return q
