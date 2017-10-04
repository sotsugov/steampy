# Steampy
Steampy is a notification service for your Steam wishlist. Set the threshold and your phone number. Steampy will track your wishlist items for sales and discounts. As soon as the price drops, you'll get a text message with the name, price and a link to the store https://steampy.xyz

### Dependencies
```
$ pip install beautifulsoup4
```

### Usage
Update the steam_ids with your steam64id/s, and set other parameters
```python
THRESHOLD = 33
VARIANCE = 10
STEAM_ID = '76561197987677089'
LOCALE = 'ee'
STEAM_STORE_URL = "https://store.steampowered.com/app/{}"
WISH_LIST_URL = "https://steamcommunity.com/profiles/{}/wishlist"
```

Then run the script from console or main
```python
if __name__ == "__main__":
    wl = WishList(STEAM_ID)
    print wl
    print prepare_payload(wl).encode('utf-8')

```

If there are any matches, you'll see an output similar to:
```
Steampy (url: http://steamcommunity.com/profiles/76561197989260017/wishlist)

STRAFE: Millennium Edition is £9.99 with -50% off:
https://store.steampowered.com/app/442780
```
