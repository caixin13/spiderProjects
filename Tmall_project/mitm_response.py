# coding:utf-8

import mitmproxy.http
from mitmproxy import ctx
injected_javascript = '''
// overwrite the `languages` property to use a custom getter
Object.defineProperty(navigator, "languages", {
  get: function() {
    return ["zh-CN","zh","zh-TW","en-US","en"];
  }
});

// Overwrite the `plugins` property to use a custom getter.
Object.defineProperty(navigator, 'plugins', {
  get: () => [1, 2, 3, 4, 5],
});

// Pass the Webdriver test
Object.defineProperty(navigator, 'webdriver', {
  get: () => undefined,
});


// Pass the Chrome Test.
// We can mock this in as much depth as we need for the test.
window.navigator.chrome = {
  runtime: {},
  // etc.
};

// Pass the Permissions Test.
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
  parameters.name === 'notifications' ?
    Promise.resolve({ state: Notification.permission }) :
    originalQuery(parameters)
);
'''



def response(flow):
    for filename in {'114.js', 'um.js', '115.js'}:
        if filename in flow.request.url:
            flow.response.text = injected_javascript + flow.response.text
            print('url={0} 注入js成功'.format(flow.request.url))

    if '/request_nick_check.do' in flow.request.url:
        print("当前请求链接为：",flow.request.url)
        flow.response.text = flow.response.text.replace('true','false')
        print('修改检查值！')
    if '/js/yoda.' in flow.request.url:
        # 屏蔽selenium检测
        for webdriver_key in ['webdriver', '__driver_evaluate', '__webdriver_evaluate', '__selenium_evaluate',
                              '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
                              '__selenium_unwrapped', '__fxdriver_unwrapped', '_Selenium_IDE_Recorder', '_selenium',
                              'calledSelenium', '_WEBDRIVER_ELEM_CACHE', 'ChromeDriverw', 'driver-evaluate',
                              'webdriver-evaluate', 'selenium-evaluate', 'webdriverCommand',
                              'webdriver-evaluate-response', '__webdriverFunc', '__webdriver_script_fn',
                              '__$webdriverAsyncExecutor', '__lastWatirAlert', '__lastWatirConfirm',
                              '__lastWatirPrompt', '$chrome_asyncScriptInfo', '$cdc_asdjflasutopfhvcZLmcfl_']:
            ctx.log.info('Remove "{}" from {}.'.format(webdriver_key, flow.request.url))
            flow.response.text = flow.response.text.replace('"{}"'.format(webdriver_key), '"NO-SUCH-ATTR"')
        flow.response.text = flow.response.text.replace('t.webdriver', 'false')
        flow.response.text = flow.response.text.replace('ChromeDriver', '')
    if not flow.response.status_code == 200:
        return

    # Inject a script tag containing the JavaScript.
    html = flow.response.text
    html = html.replace('<head>', '<head><script>%s</script>' % injected_javascript)
    flow.response.text = str(html)
    ctx.log.info('>>>> js代码插入成功 <<<<')

def request(flow):
    if flow.request.host == 'log.mmstat.com':
        ctx.log.info("catch search word: %s" % flow.request.query.get("ok"))
        flow.request.query.set_all("ok", ["1"])
    if flow.request.url == 'https://login.taobao.com/member/login.jhtml':
    # if flow.request.url == 'https://www.feizhu.com/':
    # if flow.request.url == 'https://login.taobao.com/member/login.jhtml?f=top&redirectURL=https%3A%2F%2Fwww.feizhu.com%2F':

        new_ua = "113#qMhW8NfFfJ8POf4ABkitrYbxbskPBZOF/Pf6bFbOxKuno3QRk5/GobKVGz9XjWRD1PF670L/d91CjdD0kXUxKYS/yM5Yk0Ro1PK3cWiOmIh8Dh2xkWKnosixc2/4kkqx13oqtFKfsPD8wyDZkW6gojadbsKOk05oK6FA1FoKRnGAoYxIkDmmxs4kWeH4klhx1Kf61DiOs6mL79bRkS38D9pG1s4Ok05sbcaKD7A2abcxoXMXk0inoYvv1YDB7vPD16fWbDbOs6FzDsD6x0vnT06DbsoOHDRo1Pf6bFoFsUTXugR5xWuEDyOUbY79ZW8c16nKAF2Ss6lbDXtHk0OuoYOibYcuP08416wBJWKfyH1RFsqEkWiwikY01u7vIvLR+HDNqYPdQ+XU7syo+oe6Qw6/19tJ+v6tz9kN9R07OipcNGLZsgKZxiMLnvKkGIJY8g4hnXpOIiF9XkMEQC/UsmxMEsUH45YT1BvPTYwAP672pbQEnzu9Xf/f6u/VfFIIFljIdH1EEcfoQkmaFmCJ8rY9K+4cUtZU0pxRfX2fZj6BsRAw/Bj4SZwUJbGstRtJgvHesNBs+Uk+FQ9JLDuyv0l55ux9MKq6OmmtUIi36RzZ1KYP4v4rtR8G+Ph2t4r6tzCl2VewAp4v3s1baFyBn8AH+l9k5CrPPmymdjYifZJMmP9Od4WgzofJau6U2ERUt+G6vWRjazjnJOkgDFv+cQV+EmxucbTyPStezVc4HzhiaEX7WQJYe75GoapnRuZqePQgWlT+3hJ5O3ZqH0mm/OZFB62xka3MdD3vEgeJ5Z8WyJly8lu8+koYNwCT4urvgZT9bLSWnWXNi1/kf/G9JeGF/BbituQ+YVuRgbAxM7yCwpP8sRlw0JadOs8nfHyFT1Nioeibvok="
        if flow.request.urlencoded_form:
            print("修改UA值")
            flow.request.urlencoded_form["ua"] = new_ua
        else:
            print("创建UA值")
            flow.request.urlencoded_form = [
                ("ua", new_ua)
            ]
        print('登陆表单数据为:',flow.request.urlencoded_form)