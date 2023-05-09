import Fetch, { Config } from '../getcoder/Fetch'
import Cipher from '../getcoder/Cipher'


let config = new Config("http://localhost:5000", "aaabbbccccoopserverkey123in")
config.setUserAuthKey("from nodejs client init 1.5")
// return
config.USER_ACCESS_TOKEN = Cipher.randomString(10)
let cp_fetch = new Fetch(config)

let Func = {}
Func.fetch = cp_fetch


export function getNowTime() {
    return Date.parse(new Date()) / 1000
}

export default Func