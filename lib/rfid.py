from pn532pi import Pn532

def readData(nfc: Pn532, uid: str) -> str:
    # Check if our NFC tag is the type we expect
    if (len(uid) == 7):
        # User data is stored between pages 4 and 215 in 4x2 bit chunks
        # We want everything from the last bit of page 5 onwards
        hexArray = []
        page1Success, page1Data = nfc.mifareclassic_ReadPage(5)
        
        # Only run if we successfully grab the first page - if we don't, something is probably wrong
        if page1Success:
            ## last bit of page 5
            hexArray.append(page1Data[-1:])
            
            run = True
        
            for page in range(6,216) and run:
                success, data = nfc.mifareultralight_ReadPage(page)
                if success:
                    # loop through our page chunk
                    for item in data:
                        # fe is the 'final' bit - once we read it we have everything stored on the tag
                        if item == "fe":
                            run = False
                            break
                        else:
                            hexArray.append(item)
                            
        # Decode our full array and return it as a string
        byteString = b''.join(hexArray)
        return byteString.decode()
        
