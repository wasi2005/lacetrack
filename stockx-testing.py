from stockxsdk import Stockx
stockx = Stockx()

email = 'wasgucciiii@gmail.com'
password = 'wasi2005!!'
stockx.authenticate(email, password)

# product_id = stockx.get_first_product_id('BB1234')
#
# highest_bid = stockx.get_highest_bid(product_id)
# print(highest_bid.shoe_size, highest_bid.order_price)
#
# lowest_ask = stockx.get_lowest_ask(product_id)
# print(lowest_ask.shoe_size, lowest_ask.order_price)
