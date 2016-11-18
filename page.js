//headlessブラウザを作る
var page = require('webpage').create();
var system = require('system');
var fs = require('fs');

var t, address;
//指定したURLを開く
//headlessブラウザを作る
var page = require('webpage').create();

//<>内に指定のURLを入れる
if (system.args.length < 2) {
  console.log('Usage: loadspeed.js <http://www.google.com>');
  phantom.exit();
}

if (system.args.length < 3) {
  console.log('Usage: dist');
  phantom.exit();
}

var address = system.args[1];
var dist = system.args[2]
console.log(address)
page.open(address, function(status) {
  if (status == 'success') {
    page.render(dist + '.jpg', {format: 'jpeg', quality: '100'});
    var elements = page.evaluate(function() {
      function getRect(elements) {
        var list = [];
        for (var i = 0;i < elements.length; i++) {
          var element = elements[i];
          var rect = element.getBoundingClientRect();
          list.push({
            'width': rect.width,
            'top': rect.top,
            'left': rect.left,
            'height': rect.height
          })
        }
        return list;
      }
      var text = document.querySelectorAll('.text');
      var graph = document.querySelectorAll('.graph');
      var math = document.querySelectorAll('.math');
      var random = document.querySelectorAll('.random');
      var hand = document.querySelectorAll('.hand');
      return {
        'text': getRect(text),
        'graph': getRect(graph),
        'math': getRect(math),
        'random': getRect(random),
        'hand': getRect(hand)
      }
    });
    fs.write(dist + '.json', JSON.stringify(elements, null, '  '));
  }
  phantom.exit();
});
