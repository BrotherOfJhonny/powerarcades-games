#!/usr/bin/env python3
"""Browser integration with system Chromium; preview must already be running."""
from pathlib import Path
import struct
import tempfile
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8765'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
    # Test-only clock and gamepad shim, not shipped to visitors.
    context.add_init_script('''(() => {
      const nativeNow = performance.now.bind(performance); let offset = 0;
      performance.now = () => nativeNow() + offset;
      window.advanceTestClock = value => { offset += value; };
      window.testPadButtons = [];
      navigator.getGamepads = () => [{axes:[0,0],buttons:Array.from({length:16},(_,i)=>({pressed:!!window.testPadButtons[i]}))}];
    })();''')
    page=context.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(BASE+'/games/devfest-galactic/')
    page.locator('#loading').wait_for(state='hidden')
    page.screenshot(path='/tmp/devfest-web-title.png',full_page=True)
    page.click('#start');page.wait_for_timeout(1700)
    page.keyboard.down('Space');page.wait_for_timeout(1500);page.keyboard.up('Space')
    page.screenshot(path='/tmp/devfest-web-play.png',full_page=True)
    page.evaluate('advanceTestClock(181000)')
    page.locator('#name-panel').wait_for(state='visible')
    # Same gamepad button as fire selects A, then navigation to B selects B.
    page.evaluate('testPadButtons[0]=true');page.wait_for_timeout(150)
    page.evaluate('testPadButtons[0]=false');page.wait_for_timeout(150)
    page.evaluate('testPadButtons[15]=true');page.wait_for_timeout(90)
    page.evaluate('testPadButtons[15]=false');page.wait_for_timeout(90)
    page.evaluate('testPadButtons[0]=true');page.wait_for_timeout(150)
    page.evaluate('testPadButtons[0]=false');page.wait_for_timeout(100)
    assert page.input_value('#player-name')=='AB',page.input_value('#player-name')
    page.get_by_role('button',name='Salvar nome e pontuação',exact=True).first.click()
    page.locator('#result-panel').wait_for(state='visible')
    values=page.evaluate('JSON.parse(localStorage.getItem("devfest-galactic-site-v1"))')
    assert len(values)==1 and values[0]['name']=='AB' and values[0]['origin']=='site'
    assert values[0]['rank']==1
    page.screenshot(path='/tmp/devfest-web-result.png',full_page=True)
    with tempfile.TemporaryDirectory() as tmp:
        for button,dimensions in [('download-feed',(1080,1350)),('download-story',(1080,1920))]:
            with page.expect_download() as info: page.click('#'+button)
            dest=Path(tmp,button+'.png');info.value.save_as(dest)
            assert struct.unpack('>II',dest.read_bytes()[16:24])==dimensions
    page.reload();page.locator('#loading').wait_for(state='hidden')
    page.click('#ranking');assert 'AB' in page.inner_text('#score-list')
    page.goto(BASE+'/');page.wait_for_selector('[data-slug="devfest-galactic"]')
    assert page.locator('[data-slug="devfest-galactic"] a').get_attribute('href')=='games/devfest-galactic/'
    mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    phone=mobile.new_page();phone.goto(BASE+'/games/devfest-galactic/')
    phone.locator('#loading').wait_for(state='hidden')
    assert phone.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert phone.locator('.touch').is_visible()
    phone.screenshot(path='/tmp/devfest-web-mobile.png',full_page=True)
    assert not errors,errors
    print('Browser OK: iniciar, tiro, fim, mesmo botão para letras, salvar, origem SITE, persistência, PNG feed/story, catálogo e mobile sem overflow.')
    print('Erros JavaScript:',len(errors))
    browser.close()
