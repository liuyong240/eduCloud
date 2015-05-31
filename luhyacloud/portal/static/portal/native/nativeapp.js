

function userBrowser(){
    var browserName=navigator.userAgent.toLowerCase();
    if(/msie/i.test(browserName) && !/opera/.test(browserName)){
        return "IE";
    } else if(/firefox/i.test(browserName)){
        return "Firefox";
    } else if(/chrome/i.test(browserName) && /webkit/i.test(browserName) && /mozilla/i.test(browserName)){
        return "Chrome";
    } else if(/opera/i.test(browserName)){
        return "Opera";
    } else if(/iPad/i){
        return "ipad";
    } else if(/webkit/i.test(browserName) &&!(/chrome/i.test(browserName) && /webkit/i.test(browserName) && /mozilla/i.test(browserName))){
        return "Safari";
    }else{
        return "unKnow";
    }
}

function userOSType() {
    var browserName=navigator.userAgent.toLowerCase();
    if (/linux/i.test(browserName)) {
        return "linux";
    } else if (/macintos/i.test(browserName)) {
        return "macintos";
    } else if (/windows/i.test(browserName)) {
        return "windows";
    }
}

function runNativeAppbyLinuxFirefox() {
    var localFile = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsILocalFile);
    localFile.initWithPath("/usr/bin/rdesktop");

    var process = Cc["@mozilla.org/process/util;1"].createInstance(Ci.nsIProcess);
    process.init(localFile);

    var args = [' -A "c:\Program Files\ThinLinc\WTSTools\seamlessrdpshell.exe" ',
                ' -s ' + vapp_info['exe'],
                ' -u ' + vapp_info['user'],
                vapp_info['ip']];

    process.run(false, args, args.length);
}

function runNativeAppbyLinuxChrome() {
}
function runNativeAppbyMacFirefox() {
    var localFile = Components.classes["@mozilla.org/file/local;1"].createInstance(Components.interfaces.nsILocalFile);
    localFile.initWithPath("/usr/local/bin/rdesktop");

    var process = Components.classes["@mozilla.org/process/util;1"].createInstance(Components.interfaces.nsIProcess);
    process.init(localFile);

    var args = [' -A "c:\Program Files\ThinLinc\WTSTools\seamlessrdpshell.exe" ',
                ' -s ' + vapp_info['exe'],
                ' -u ' + vapp_info['user'],
                vapp_info['ip']];

    process.run(false, args, args.length);
}
function runNativeAppbyMacChrome() {
}
function runNativeAppbyWinFirefox() {
}
function runNativeAppbyWinChrome() {
}
function runNativeAppbyWinIE() {
}


function start_native_app(vapp_info) {
    var {Cc, Ci} = require("chrome");
    btype = userBrowser();
    ostype = userOSType();

    switch (btype) {
        case 'IE':
            runNativeAppbyWinIE();
            break;
        case 'Firefox':
            switch (ostype) {
                case 'linux':
                    runNativeAppbyLinuxFirefox(vapp_info);
                    break;
                case 'macintos':
                    runNativeAppbyMacFirefox(vapp_info);
                    break;
                case 'windows':
                    runNativeAppbyWinFirefox(vapp_info);
                    break;
            }
            break;
        case 'Chrome':
            switch (ostype) {
                case 'linux':
                    runNativeAppbyLinuxChrome(vapp_info);
                    break;
                case 'macintos':
                    runNativeAppbyMacChrome(vapp_info);
                    break;
                case 'windows':
                    runNativeAppbyWinChrome(vapp_info);
                    break;
            }
            break;
    }
}