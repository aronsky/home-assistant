"use strict";function setOfCachedUrls(e){return e.keys().then(function(e){return e.map(function(e){return e.url})}).then(function(e){return new Set(e)})}function notificationEventCallback(e,t){firePushCallback({action:t.action,data:t.notification.data,tag:t.notification.tag,type:e},t.notification.data.jwt)}function firePushCallback(e,t){delete e.data.jwt,0===Object.keys(e.data).length&&e.data.constructor===Object&&delete e.data,fetch("/api/notify.html5/callback",{method:"POST",headers:new Headers({"Content-Type":"application/json",Authorization:"Bearer "+t}),body:JSON.stringify(e)})}var precacheConfig=[["/","0899bec0981cfd4ced9d5c4415c727f7"],["/frontend/panels/dev-event-91347dedf3b4fa9b49ccf4c0a28a03c4.html","f74c44ab9bfbdc81badb56518ef8113d"],["/frontend/panels/dev-info-6d09483730b86588fb3dc4f2242807aa.html","78a5b6d63d75af6e14d9448ea0b99a08"],["/frontend/panels/dev-service-a9247f255174b084fad2c04bdb9ec7a9.html","4d5f34f8ebc6c5fc4bdcff1ef7b4eb35"],["/frontend/panels/dev-state-90f3bede9602241552ef7bb7958198c6.html","277716ed9b76fa4313a1653dc757741b"],["/frontend/panels/dev-template-3eeabe4a47ac6bea5b7af0f2b7cf5e90.html","28d7e28a03f519f921d34a20beca6502"],["/frontend/panels/map-970f1a71ca1807fc7f6f049b5f38dbb0.html","f4f94d03fabd83294f75a4276b42d661"],["/static/compatibility-83d9c77748dafa9db49ae77d7f3d8fb0.js","5f05c83be2b028d577962f9625904806"],["/static/core-adfeb513cf650acf763e284d76a48d6b.js","f5fdf5f1f754e801f9f54ad31a3cc922"],["/static/frontend-ea7529d0d835b6b87109a052e69955db.html","8880859617d4dc8d148c62ed90e279ba"],["/static/mdi-c1dde43ccf5667f687c418fc8daf9668.html","6a3c9317736ca26e3390316335be9ba5"],["static/fonts/roboto/Roboto-Bold.ttf","d329cc8b34667f114a95422aaad1b063"],["static/fonts/roboto/Roboto-Light.ttf","7b5fb88f12bec8143f00e21bc3222124"],["static/fonts/roboto/Roboto-Medium.ttf","fe13e4170719c2fc586501e777bde143"],["static/fonts/roboto/Roboto-Regular.ttf","ac3f799d5bbaf5196fab15ab8de8431c"],["static/icons/favicon-192x192.png","419903b8422586a7e28021bbe9011175"],["static/icons/favicon.ico","04235bda7843ec2fceb1cbe2bc696cf4"],["static/images/card_media_player_bg.png","a34281d1c1835d338a642e90930e61aa"],["static/webcomponents-lite.min.js","32b5a9b7ada86304bec6b43d3f2194f0"]],cacheName="sw-precache-v2--"+(self.registration?self.registration.scope:""),ignoreUrlParametersMatching=[/^utm_/],addDirectoryIndex=function(e,t){var a=new URL(e);return"/"===a.pathname.slice(-1)&&(a.pathname+=t),a.toString()},createCacheKey=function(e,t,a,n){var c=new URL(e);return n&&c.toString().match(n)||(c.search+=(c.search?"&":"")+encodeURIComponent(t)+"="+encodeURIComponent(a)),c.toString()},isPathWhitelisted=function(e,t){if(0===e.length)return!0;var a=new URL(t).pathname;return e.some(function(e){return a.match(e)})},stripIgnoredUrlParameters=function(e,t){var a=new URL(e);return a.search=a.search.slice(1).split("&").map(function(e){return e.split("=")}).filter(function(e){return t.every(function(t){return!t.test(e[0])})}).map(function(e){return e.join("=")}).join("&"),a.toString()},hashParamName="_sw-precache",urlsToCacheKeys=new Map(precacheConfig.map(function(e){var t=e[0],a=e[1],n=new URL(t,self.location),c=createCacheKey(n,hashParamName,a,!1);return[n.toString(),c]}));self.addEventListener("install",function(e){e.waitUntil(caches.open(cacheName).then(function(e){return setOfCachedUrls(e).then(function(t){return Promise.all(Array.from(urlsToCacheKeys.values()).map(function(a){if(!t.has(a))return e.add(new Request(a,{credentials:"same-origin",redirect:"follow"}))}))})}).then(function(){return self.skipWaiting()}))}),self.addEventListener("activate",function(e){var t=new Set(urlsToCacheKeys.values());e.waitUntil(caches.open(cacheName).then(function(e){return e.keys().then(function(a){return Promise.all(a.map(function(a){if(!t.has(a.url))return e.delete(a)}))})}).then(function(){return self.clients.claim()}))}),self.addEventListener("fetch",function(e){if("GET"===e.request.method){var t,a=stripIgnoredUrlParameters(e.request.url,ignoreUrlParametersMatching);t=urlsToCacheKeys.has(a);var n="index.html";!t&&n&&(a=addDirectoryIndex(a,n),t=urlsToCacheKeys.has(a));var c="/";!t&&c&&"navigate"===e.request.mode&&isPathWhitelisted(["^((?!(static|api|local|service_worker.js|manifest.json)).)*$"],e.request.url)&&(a=new URL(c,self.location).toString(),t=urlsToCacheKeys.has(a)),t&&e.respondWith(caches.open(cacheName).then(function(e){return e.match(urlsToCacheKeys.get(a)).then(function(e){if(e)return e;throw Error("The cached response that was expected is missing.")})}).catch(function(t){return console.warn('Couldn\'t serve response for "%s" from cache: %O',e.request.url,t),fetch(e.request)}))}}),self.addEventListener("push",function(e){var t;e.data&&(t=e.data.json(),e.waitUntil(self.registration.showNotification(t.title,t).then(function(e){firePushCallback({type:"received",tag:t.tag,data:t.data},t.data.jwt)})))}),self.addEventListener("notificationclick",function(e){var t;notificationEventCallback("clicked",e),e.notification.close(),e.notification.data&&e.notification.data.url&&(t=e.notification.data.url,t&&e.waitUntil(clients.matchAll({type:"window"}).then(function(e){var a,n;for(a=0;a<e.length;a++)if(n=e[a],n.url===t&&"focus"in n)return n.focus();if(clients.openWindow)return clients.openWindow(t)})))}),self.addEventListener("notificationclose",function(e){notificationEventCallback("closed",e)});