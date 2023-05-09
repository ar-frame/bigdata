import Fetch, {Config, ServerResponseException} from './Fetch'
import Cipher from './Cipher'

try {
    let config  = new Config("http://localhost:5000", "aaabbbccccoopserverkey123in")
    config.setUserAuthKey("from cpp client init 1.3")
    // return
    config.USER_ACCESS_TOKEN = Cipher.randomString(10)
    let cp_fetch = new Fetch(config)
   
    // window.fetch = cp_fetch
    // fetch.getObject('server.Data', 'pushData', [pushobjdata, all_sports[0]['tz']])
    cp_fetch.getObject("server.Test", "mytest", ['1中2文能否abc'], function (data) {
        console.log(data)
    })
    
     // decodeURI
    //  console.log(Cipher.urlencode('中国'))

    //  console.log(unescape('nfffss%u4E0D%u77E5%u540D%u670D%u52A1'))
     
    //  console.log(Cipher.str2HexStr('aa大'))
    //  console.log(Cipher.hexStr2Str('61615927'))

    // window.fetch.sendRequest("server.ctl.dama.Dama", "getNeedToDamaList", [], function (data) {
    //     // 返回字符串
    //     console.log(data)
    // })

    // window.fetch.getObject("server.ctl.dama.Dama", "getNeedToDamaList", [], function (data) {
    //     console.log(11111)
    //     // 返回对象
    //     console.log(data.errMsg)
    // })


} catch (e) {
    console.log("catch err:" + e.message)
}

