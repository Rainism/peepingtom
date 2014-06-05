var page = require('webpage').create(),
    url, filename, size;

url = phantom.args[0];
filename = phantom.args[1];
page.viewportSize = { width: 800, height: 600 };
page.clipRect = { top: 0, left: 0, width: 800, height: 600 };
page.open(url, function (status) {
    //if (status !== 'success') {
    //    console.log('Unable to load the address!');
    //} else {
        window.setTimeout(function () {
            page.render(filename);
            //console.log(url  + ' complete.');
            phantom.exit();
        }, 200);
    //}
});
