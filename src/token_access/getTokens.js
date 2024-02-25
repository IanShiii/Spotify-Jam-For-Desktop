const buddyList = require('.')
const fs = require('fs')

function getConfigs() {
  return new Promise((resolve, reject) => {
    fs.readFile('src/config/config.json', 'utf8', (err, data) => {
      if (err) {
        reject(err);
        return;
      }

      try {
        const jsonData = JSON.parse(data);
        resolve(jsonData);
      } catch (err) {
        reject(err);
      }
    });
  });
}

async function main() {

  const configs = await getConfigs()
  const user1Token = await buddyList.getWebAccessToken(configs['USER1_SP_DC_COOKIE'])
  const user2Token = await buddyList.getWebAccessToken(configs['USER2_SP_DC_COOKIE'])

  // const {accessToken} = await buddyList.getWebAccessToken(spDcCookie)
  // const friendActivity = await buddyList.getFriendActivity(accessToken)

  tokens = {
    'user1': user1Token['accessToken'],
    'user2': user2Token['accessToken']
  }
  console.log(JSON.stringify(tokens))
}

main()
