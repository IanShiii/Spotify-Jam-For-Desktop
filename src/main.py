import subprocess
import json
from dotenv import load_dotenv
import sys
from processes import join

load_dotenv()

with open('src/config/config.json', 'r') as configs:
    cookies = json.load(configs)
    configs.close()
    USER1_SP_DC_COOKIE = cookies['USER1_SP_DC_COOKIE']
    USER2_SP_DC_COOKIE = cookies['USER2_SP_DC_COOKIE']
USER1_TOKEN = json.loads(subprocess.run('node src/token_access/getTokens.js', capture_output=True, text=True).stdout)['user1']
USER2_TOKEN = json.loads(subprocess.run('node src/token_access/getTokens.js', capture_output=True, text=True).stdout)['user2']

sys.setrecursionlimit(2000) #LMAO
join(USER1_TOKEN, USER2_TOKEN)