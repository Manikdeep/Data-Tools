#keyDown(Key.CTRL)
#keyDown(Key.ALT)
#type("t")
#keyUp(Key.CTRL)
#keyUp(Key.ALT)
#wait(2)
#type("python3 fetchDatabase.py 'channel'>channellinks.txt"+Key.ENTER)
#wait (5)

f = open("channelLinks.txt",'r')

text = f.read()
print(text)
channels = text.split('\n')
f.close()
pc = open("channelsCompleted",'r')
previousChannels = pc.read().split('\n')
nf = open("channelsNotFound",'r')
notFound = nf.read().split()
nf.close()
pc.close()

count = 0
for channel in channels[::-1]: 
    channelsNotFound = open("channelLinks",'a')
    channelsCompleted = open("channelsCompleted",'a')
    channelsJoined = open("channelsJoined",'a')

    print("Channel: " + str(count))
    print(channel)
    count += 1
    if channel.strip() == "":
        continue
    if(channel.strip() in previousChannels or channel.strip() in notFound):
        continue
    else:
        click(Pattern("1708966740313.png").targetOffset(1,2))
        click(Pattern("1708966740313.png").targetOffset(1,2))
        click(Pattern("1708966853943.png").targetOffset(0,-1))
        wait(4)
        click(Pattern("1708966905147.png").targetOffset(-306,-2))
        type(channel+Key.ENTER)
        print("Check")
        wait(4)
       
        click(Pattern("1708966962576.png").targetOffset(-3,1))
      
    click("1666031140187.png")
    wait(2)

    click (Pattern("1668137003653.png").targetOffset(19,0))
    if exists(Pattern("1611801699277.png").targetOffset(-10,-3)):
        print("Export Initiated")
        click(Pattern("1611801699277.png").targetOffset(-22,-2))
    elif exists(Pattern("channel_dropdown.png").targetOffset(-7,3)):
        click(Pattern("channel_dropdown.png").targetOffset(-5,1))
    elif exists(Pattern("notjoinedchannel_dropdown.png").targetOffset(14,17)):
        click(Pattern("notjoinedchannel_dropdown.png").targetOffset(22,19))
    elif exists(Pattern("export_chat_history_lone.png").targetOffset(13,-2)):
        click(Pattern("export_chat_history_lone.png").targetOffset(28,-4)) 
    else:
        print("Export Initiation Failed")
        channelsNotFound.write(channel.strip() + '\n')
        channelsNotFound.close()
        continue
    dragDrop(Pattern("1658765122524.png").targetOffset(10,0), Pattern("1658765188407.png").targetOffset(0,14))
    click(Pattern("1609896265433.png").targetOffset(-2,-1))
    click(Pattern("1609896346117.png").targetOffset(-86,2))
    click(Pattern("1658436454533.png").targetOffset(0,-1))

    #for initial scrapes comment out the next two lines of code.
    click(Pattern("1649450402643.png").targetOffset(-1,-1)) 
    click(Pattern("1675369164819.png").targetOffset(-3,-2))
    click(Pattern("1675312416949.png").targetOffset(0,-4))
    click(Pattern("1675312535054.png").targetOffset(2,0)) 
    type("CF M")
   
    wait(7)
    if exists(Pattern("1685770626175.png").targetOffset(6,1)):
            doubleClick(Pattern("1685770626175.png").targetOffset(6,1))
    else:
            doubleClick(Pattern("1716963056932.png").targetOffset(-1,0))

    click(Pattern("1671041359497.png").targetOffset(0,-2))
    paste(channel.strip().split("/")[-1])
    click(Pattern("Createbtn_new_UI-1.jpg").similar(0.01).targetOffset(14,-1))
    click(Pattern("1666205905608.png").targetOffset(-8,0))
    wait(5)
    click(Pattern("1670556582359.png").targetOffset(-18,-1))
    wait(1)
    click(Pattern("1728310279624.png").targetOffset(-82,-2))
    click(Pattern("1649456734335.png").targetOffset(-5,1))
    wait(3)
    click(Pattern("1728310346983.png").targetOffset(86,3))
    #click()
  
    click(Pattern("1651683858061.png").similar(0.80).targetOffset(122,1))
    while not exists(Pattern("1650054668601.png").targetOffset(9,-3)):
        wait(7)
    if exists:
        click(Pattern("1667926797997.png").targetOffset(146,-1))
    channelsCompleted.write(channel.strip() + '\n')
    channelsCompleted.close()
print("Telegram Channels Download - Done!!!")
channelsNotFound.close()
channelsJoined.close()
channelsCompleted.close()