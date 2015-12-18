import os,re,sys,urllib,urlparse, control, cache, client, cachemeta, workers, views

# TO CHECK AND AMMEND
phNews = 'http://mecca.watchkodi.com/news.xml'

def getDirectory(name, url, audio, image, fanart, playable, content, close=True, local=False):
    if local == True:
        f = control.openFile(url) ; result = f.read() ; f.close()
    else:
        result = cache.get(client.request, 0, url)

    result = str(result).replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','')

    try: fanart = re.findall('<fanart>(.+?)</fanart>', result)[0]
    except: fanart = '0'


    try:
        notify = re.compile('<notify>(.+?)</notify>').findall(result)[0]

        vip = re.findall('<poster>(.+?)</poster>', result)[0]
        if not re.search('[a-zA-Z]', vip): raise Exception()

        def message(vip): return (vip+version)

        check = cache.get(message, 600000000, vip, table='rel_vip')

        version = re.findall('<new>(.+?)</new>', notify)[0]
        if not version.isdigit(): raise Exception()

        if check == (vip+version): raise Exception()

        title = '[B]Announcement From %s![/B]' % vip
        msg1 = re.findall('<message1>(.+?)</message1>', notify)[0]
        msg2 = re.findall('<message2>(.+?)</message2>', notify)[0]
        msg3 = re.findall('<message3>(.+?)</message3>', notify)[0]

        check = cache.get(message, 0, vip, table='rel_vip')

        control.dialog.ok(str(title), str(msg1), str(msg2), str(msg3))
    except:
        pass


    infos = re.compile('<info>(.+?)</info>').findall(result)

    for info in infos:
        try:
            name = re.findall('<message>(.+?)</message>', info)[0]

            try: image = re.findall('<thumbnail>(.+?)</thumbnail>', info)[0]
            except: image = '0'

            addDirectoryItem(name, '0', '0', image, image, fanart, '0', '0', {})
        except:
            pass


    popups = re.compile('<popup>(.+?)</popup>').findall(result)

    for popup in popups:
        try:
            name = re.findall('<name>(.+?)</name>', popup)[0]

            url = re.findall('<popImage>(.+?)</popImage>', popup)[0]

            try: image = re.findall('<thumbnail>(.+?)</thumbnail>', popup)[0]
            except: image = '0'

            try: audio = re.findall('<sound>(.+?)</sound>', popup)[0]
            except: audio = '0'

            addDirectoryItem(name, url, 'openDialog', image, image, fanart, audio, '0', {})
        except:
            pass


    special = re.compile('<name>([^<]+)</name><link>([^<]+)</link><thumbnail>([^<]+)</thumbnail><date>([^<]+)</date>').findall(result)
    for name, url, image, date in special:
        if re.search(r'\d+', date): name += ' [COLOR red] Updated %s[/COLOR]' % date
        addDirectoryItem(name, url, 63, image, image, fanart, '0', '0', {})

    special = re.compile('<name>([^<]+)</name><link>([^<]+)</link><thumbnail>([^<]+)</thumbnail><mode>([^<]+)</mode>').findall(result)
    for name, url, image, action in special:
        print '#~#~#~#~ MAIN MENU : ' + action
        if action == 'ndmode':
            action = 63
        if action == 'dmode':
            action = 63
        if not url == phNews: addDirectoryItem(name, url, action, image, image, fanart, '0', '0', {})



    meta = False

    try: content = re.findall('<meta>(.+?)</meta>', result)[0]
    except: content = '0'

    try: tvshow = re.findall('<tvshow>(.+?)</tvshow>', result)[0]
    except: tvshow = '0'

    if content in ['seasons', 'episodes'] and tvshow == '0':
        content = '0'

    if content in ['movies', 'tvshows'] and control.setting('meta') == 'true':
        try:
            from metahandler import metahandlers
            metaget = metahandlers.MetaData(preparezip=False)
            meta = True
        except:
            meta = False

    elif content in ['seasons', 'episodes']:
        try:
            from metahandler import metahandlers
            metaget = metahandlers.MetaData(preparezip=False)
            #tvd = metaget.get_meta('tvshow', tvshow)
            tvd = cachemeta.get(metaget.get_meta, 24, 'tvshow', tvshow, '', '', '')
        except:
            tvd = {}


    dirs = re.compile('<dir>(.+?)</dir>').findall(result)

    totalItems = len(dirs)

    for dir in dirs:
        try:
            data = {}

            name = re.findall('<name>(.+?)</name>', dir)[0]

            url = re.findall('<link>(.+?)</link>', dir)[0]

            try: image = re.findall('<thumbnail>(.+?)</thumbnail>', dir)[0]
            except: image = '0'

            try: fanart2 = re.findall('<fanart>(.+?)</fanart>', dir)[0]
            except: fanart2 = fanart

            if meta == True and content =='tvshows':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': title}

                    #data = metaget.get_meta('tvshow', title)
                    data = cachemeta.get(metaget.get_meta, 24, 'tvshow', title, '', '', '')

                    metafanart = data['backdrop_url']
                    if not metafanart == '': fanart2 = metafanart
                except:
                    pass

            elif content =='tvshows':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': title}
                except:
                    pass

            elif content =='seasons':
                try:
                    title = cleantitle(tvshow).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': title}

                    data.update(tvd)

                    metafanart = tvd['backdrop_url']
                    if not metafanart == '': fanart2 = metafanart
                except:
                    pass

            addDirectoryItem(name, url, 63, image, image, fanart2, '0', content, data, totalItems=totalItems)
        except:
            pass

    items = re.compile('<item>(.+?)</item>').findall(result)

    try: sort = re.findall('<sort>(.+?)</sort>', result)[0]
    except: sort = ''
    if sort == 'yes': items = sorted(items)
    totalItems = len(items)
	
    for item in items:
        try:

            data = {}

            name = re.findall('<title>(.+?)</title>', item)[0]

            url = re.findall('<link>(.+?)</link>', item)[0]

            try: image = image2 = re.findall('<thumbnail>(.+?)</thumbnail>', item)[0]
            except: image = image2 = '0'

            try: fanart2 = re.findall('<fanart>(.+?)</fanart>', item)[0]
            except: fanart2 = fanart

            if meta == True and content == 'movies':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title}

                    title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
                    title = cleantitle(title).encode('utf-8')
                    data = {'title': title, 'year': year}

                    #data = metaget.get_meta('movie', title, year=year)
                    data = cachemeta.get(metaget.get_meta, 24, 'movie', title, '', '', year)

                    metaimage = data['cover_url']
                    if not metaimage == '': image = metaimage
                    metafanart = data['backdrop_url']
                    if not metafanart == '': fanart2 = metafanart
                except:
                    pass

            elif content =='movies':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title}

                    title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
                    title = cleantitle(title).encode('utf-8')
                    data = {'title': title, 'year': year}
                except:
                    pass

            elif content == 'episodes':
                try:
                    title = cleantitle(name).encode('utf-8')
                    data = {'title': title, 'tvshowtitle': tvshow}
                except:
                    pass
                try:
                    i = cleaneptitle(tvshow, title)
                    title, season, episode = i[0].encode('utf-8'), i[1], i[2]
                    data = {'title': title, 'tvshowtitle': tvshow, 'season': season, 'episode': episode}
                except:
                    pass
                try:
                    data.update({'year': tvd['year'], 'imdb_id' : tvd['imdb_id'], 'tvdb_id' : tvd['tvdb_id'], 'tvshowtitle': tvd['TVShowTitle'], 'genre' : tvd['genre'], 'studio': tvd['studio'], 'status': tvd['status'], 'duration' : tvd['duration'], 'rating': tvd['rating'], 'mpaa' : tvd['mpaa'], 'plot': tvd['plot'], 'cast': tvd['cast']})

                    metafanart = tvd['backdrop_url']
                    if not metafanart == '': image = fanart2 = metafanart
                except:
                    pass


            if 'sublink' in url:
                addDirectoryItem(name, url, 62, image, image2, fanart2, '0', content, data, tvshow=tvshow, totalItems=totalItems, isFolder=True)
                print 'PLP SubLink: ' + url
            else:
                addDirectoryItem(name, url, 61, image, image2, fanart2, '0', content, data, totalItems=totalItems, isFolder=False)
        except:
            pass

    endDirectory(content, close)

def endDirectory(content, close):
    if content in ['movies', 'tvshows', 'seasons', 'episodes']:
        control.content(int(sys.argv[1]), content)

    if close == True: control.directory(int(sys.argv[1]), cacheToDisc=True)

    if close == True and content in ['movies', 'tvshows', 'seasons', 'episodes']:
        views.setView(content)

def addDirectoryItem(name, url, action, image, image2, fanart, audio, content, data, tvshow='0', totalItems=0, isFolder=True):
    if not str(image).lower().startswith('http'): image = control.addonInfo('icon')

    if not str(image2).lower().startswith('http'): image2 = control.addonInfo('icon')

    if not str(fanart).lower().startswith('http'): fanart = control.addonInfo('fanart')

    if content in ['movies', 'episodes']: playable = 'true'
    else: playable = 'false'

    sysaddon = sys.argv[0]

    u = '%s?name=%s&url=%s&audio=%s&image=%s&fanart=%s&playable=%s&tvshow=%s&content=%s&mode=%s' % (sysaddon, urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(audio), urllib.quote_plus(image), urllib.quote_plus(fanart), urllib.quote_plus(playable), str(tvshow), str(content), str(action))

    cm = []

    if content in ['movies', 'tvshows']:
        data.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, urllib.quote_plus(name))})
        cm.append((control.lang(30707).encode('utf-8'), 'RunPlugin(%s?action=trailer&name=%s)' % (sysaddon, urllib.quote_plus(name))))

    if not 'plot' in data:
        data.update({'plot': control.lang(30706).encode('utf-8')})


    if content == 'movies':
        cm.append((control.lang(30708).encode('utf-8'), 'XBMC.Action(Info)'))
    elif content in ['tvshows', 'seasons']:
        cm.append((control.lang(30709).encode('utf-8'), 'XBMC.Action(Info)'))
    elif content == 'episodes':
        cm.append((control.lang(30710).encode('utf-8'), 'XBMC.Action(Info)'))


    if content == 'movies' and not isFolder == True:
        downloadFile = name
        try: downloadFile = '%s (%s)' % (data['title'], data['year'])
        except: pass
        cm.append((control.lang(30722).encode('utf-8'), 'RunPlugin(%s?action=addDownload&name=%s&url=%s&image=%s)' % (sysaddon, urllib.quote_plus(downloadFile), urllib.quote_plus(url), urllib.quote_plus(image))))

    elif content == 'episodes' and not isFolder == True:
        downloadFile = name
        try: downloadFile = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))
        except: pass
        cm.append((control.lang(30722).encode('utf-8'), 'RunPlugin(%s?action=addDownload&name=%s&url=%s&image=%s)' % (sysaddon, urllib.quote_plus(downloadFile), urllib.quote_plus(url), urllib.quote_plus(image))))


    if content == 'movies':
        cm.append((control.lang(30711).encode('utf-8'), 'RunPlugin(%s?action=addView&content=movies)' % sysaddon))
    elif content == 'tvshows':
        cm.append((control.lang(30712).encode('utf-8'), 'RunPlugin(%s?action=addView&content=tvshows)' % sysaddon))
    elif content == 'seasons':
        cm.append((control.lang(30713).encode('utf-8'), 'RunPlugin(%s?action=addView&content=seasons)' % sysaddon))
    elif content == 'episodes':
        cm.append((control.lang(30714).encode('utf-8'), 'RunPlugin(%s?action=addView&content=episodes)' % sysaddon))


    item = control.item(name, iconImage='DefaultFolder.png', thumbnailImage=image)
    try: item.setArt({'poster': image2, 'tvshow.poster': image2, 'season.poster': image2, 'banner': image, 'tvshow.banner': image, 'season.banner': image})
    except: pass
    item.addContextMenuItems(cm, replaceItems=False)
    item.setProperty('Fanart_Image', fanart)
    if playable == 'true': item.setProperty('IsPlayable', 'true')
    item.setInfo(type='Video', infoLabels=data)

    control.addItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=totalItems,isFolder=isFolder)


def subDirectory(name, url, audio, image, fanart, playable, tvshow, content):
    match = re.compile('<sublink>(.+?)</sublink>').findall(url)
    if len(match) == 0: return
    data = {}
    try:
        title = cleantitle(name).encode('utf-8')
        data = {'title': title}
    except:
        pass

    try:
        if not content == 'movies': raise Exception()

        title = cleantitle(name).encode('utf-8')
        data = {'title': title}

        title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
        title = cleantitle(title).encode('utf-8')
        data = {'title': title, 'year': year}

        from metahandler import metahandlers
        metaget = metahandlers.MetaData(preparezip=False)

        #data = metaget.get_meta('movie', title, year=year)
        data = cachemeta.get(metaget.get_meta, 24, 'movie', title, '', '', year)

        metaimage = data['cover_url']
        if not metaimage == '': image = metaimage
        metafanart = data['backdrop_url']
        if not metafanart == '': fanart = metafanart
    except:
        pass

    try:
        if tvshow == '0' and not content == 'episodes': raise Exception()

        try:
            title = cleantitle(name).encode('utf-8')
            data = {'title': title, 'tvshowtitle': tvshow}
        except:
            pass
        try:
            i = cleaneptitle(tvshow, title)
            title, season, episode = i[0].encode('utf-8'), i[1], i[2]
            data = {'title': title, 'tvshowtitle': tvshow, 'season': season, 'episode': episode}
        except:
            pass

        from metahandler import metahandlers
        metaget = metahandlers.MetaData(preparezip=False)
        tvd = metaget.get_meta('tvshow', tvshow)
        tvd = cachemeta.get(metaget.get_meta, 24, 'tvshow', tvshow, '', '', '')

        data.update({'year': tvd['year'], 'imdb_id' : tvd['imdb_id'], 'tvdb_id' : tvd['tvdb_id'], 'tvshowtitle': tvd['TVShowTitle'], 'genre' : tvd['genre'], 'studio': tvd['studio'], 'status': tvd['status'], 'duration' : tvd['duration'], 'rating': tvd['rating'], 'mpaa' : tvd['mpaa'], 'plot': tvd['plot'], 'cast': tvd['cast']})

        metafanart = tvd['backdrop_url']
        if not metafanart == '': image = fanart = metafanart
    except:
        pass

    for i in range(0, len(match)):
        url = match[i]
        label = '%s %s %s' % (name, control.lang(30704).encode('utf-8'), str(i+1))
        addDirectoryItem(label, url, 61, image, image, fanart, '0', content, data, isFolder=False)

    control.directory(int(sys.argv[1]), cacheToDisc=True)

def resolveUrl(name, url, audio, image, fanart, playable, content):
    try:
	print '#~#~#~#~ Start Of Resolve URL!!!!! '
        if '.f4m'in url:
	    print '#~#~#~#~ F4M: ' + url
            label = cleantitle(name)
            ext = url.split('?')[0].split('&')[0].split('|')[0].rsplit('.')[-1].replace('/', '').lower()
            if not ext == 'f4m': raise Exception()
            from resources.lib.libraries.f4mproxy.F4mProxy import f4mProxyHelper
            return f4mProxyHelper().playF4mLink(url, label, None, None,'',image)


        #legacy issue, will be removed later
        if 'afdah.org' in url and not '</source>' in url: url += '<source>afdah</source>'

        if '</source>' in url:
	    print '#~#~#~#~ </source> : ' + url
            source = re.compile('<source>(.+?)</source>').findall(url)[0]
            url = re.compile('(.+?)<source>').findall(url)[0]

            for i in ['_mv', '_tv', '_mv_tv']:
                try: call = __import__('resources.lib.sources.%s%s' % (source, i), globals(), locals(), ['object'], -1).source()
                except: pass

            from resources.lib import sources ; d = sources.sources()

            url = call.get_sources(url, d.hosthdfullDict, d.hostsdfullDict, d.hostlocDict)

            if type(url) == list and len(url) == 1:
                url = url[0]['url']

            elif type(url) == list:
                url = sorted(url, key=lambda k: k['quality'])
                for i in url: i.update((k, '720p') for k, v in i.iteritems() if v == 'HD')
                for i in url: i.update((k, '480p') for k, v in i.iteritems() if v == 'SD')
                q = ['[B]%s[/B] | %s' % (i['source'].upper(), i['quality'].upper()) for i in url]
                u = [i['url'] for i in url]
                select = control.selectDialog(q)
                if select == -1: return
                url = u[select]

            url = call.resolve(url)


        from resources.lib import resolvers
        host = (urlparse.urlparse(url).netloc).rsplit('.', 1)[0].rsplit('.')[-1]
        url = resolvers.request(url)
	print '#~#~#~#~ Resource LIB Res : ' + url

        if type(url) == list and len(url) == 1:
            url = url[0]['url']

        elif type(url) == list:
            url = sorted(url, key=lambda k: k['quality'])
            for i in url: i.update((k, '720p') for k, v in i.iteritems() if v == 'HD')
            for i in url: i.update((k, '480p') for k, v in i.iteritems() if v == 'SD')
            q = ['[B]%s[/B] | %s' % (host.upper(), i['quality'].upper()) for i in url]
            u = [i['url'] for i in url]
            select = control.selectDialog(q)
            if select == -1: return
            url = u[select]

        if url == None: 
			raise Exception()
			exc = Exception()
			print '#~#~#~#~ exception : ' + exc + '#~#~#~#~ exception : ' + url
		
    except:
        return control.infoDialog(control.lang(30705).encode('utf-8'))
        pass


    if playable == 'true':
        item = control.item(path=url)
        print '#~#~#~#~' + url
        return control.resolve(int(sys.argv[1]), True, item)
    else:
        print '#~#~#~#~' + url
        label = cleantitle(name)
        item = control.item(path=url, iconImage=image, thumbnailImage=image)
        item.setInfo( type='Video', infoLabels = {'title': label} )
        control.playlist.clear()
        control.player.play(url, item)

def getSearch():
    addDirectoryItem('%s...' % control.lang(30702).encode('utf-8'), '0', 'searchDirectory', '0', '0', '0', '0', '0', {})
    addDirectoryItem(control.lang(30703).encode('utf-8'), '0', 'clearSearch', '0', '0', '0', '0', '0', {})

    try:
        def search(): return
        result = cache.get(search, 600000000, table='rel_srch')
        for q in result:
                try: addDirectoryItem('%s...' % q, q, 'searchDirectory2', '0', '0', '0', '0', '0', {})
                except: pass
    except:
        pass

    control.directory(int(sys.argv[1]), cacheToDisc=True)


def searchDirectory(query=None):
    if (query == None or query == ''):
        keyboard = control.keyboard('', control.lang(30702).encode('utf-8'))
        keyboard.doModal()
        if not (keyboard.isConfirmed()): return
        query = keyboard.getText()

    if (query == None or query == ''): return

    def search(): return [query]
    result = cache.get(search, 600000000, table='rel_srch')
    def search(): return [x for y,x in enumerate((result + [query])) if x not in (result + [query])[:y]]
    result = cache.get(search, 0, table='rel_srch')


    global global_search ; global_search = []

    def worker(url): global_search.append(str(client.request(url)))

    servers = client.request(phLink)
    servers = str(servers).replace('\n','')
    servers = re.findall('</name><link>(.+?)</link>', servers)
    servers = [urlparse.urlparse(i).netloc for i in servers]
    servers = [phSearch % i for i in servers if not 'mecca' in i]

    threads = []
    for server in servers: threads.append(workers.Thread(worker, server))
    [i.start() for i in threads]
    [i.join() for i in threads]

    urls = global_search ; global_search = []
    urls = [str(i).replace('\n','') for i in urls]
    urls = [re.findall('<link>(.+?)</link>', i)[:30] for i in urls]
    urls = sum(urls, [])

    threads = []
    for url in urls: threads.append(workers.Thread(worker, url))
    [i.start() for i in threads]
    [i.join() for i in threads]

    links = global_search ; global_search = []

    for link in links:
        try:
            link = str(link).replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','')

            try: fanart = re.findall('<fanart>(.+?)</fanart>', link)[0]
            except: fanart = '0'

            try: vip = re.findall('<poster>(.+?)</poster>', link)[0]
            except: vip = ''

            if vip == 'Team Phoenix': vip = ''

            try: content = re.findall('<meta>(.+?)</meta>', link)[0]
            except: content = '0'

            try: tvshow = re.findall('<tvshow>(.+?)</tvshow>', link)[0]
            except: tvshow = '0'

            if content in ['seasons', 'episodes'] and tvshow == '0':
                content = '0'


            dirs = re.compile('<dir>(.+?)</dir>').findall(link)

            for dir in dirs:
                try:
                    data = {}

                    name = re.findall('<name>(.+?)</name>', dir)[0]
                    name = cleantitle(name)

                    if not query.lower() in name.lower() : raise Exception()

                    url = re.findall('<link>(.+?)</link>', dir)[0]

                    try: image = re.findall('<thumbnail>(.+?)</thumbnail>', dir)[0]
                    except: image = '0'

                    try: fanart2 = re.findall('<fanart>(.+?)</fanart>', dir)[0]
                    except: fanart2 = fanart

                    if content =='tvshows':
                        try:
                            title = cleantitle(name).encode('utf-8')
                            data = {'title': title, 'tvshowtitle': title}
                        except:
                            pass

                    if re.search('[a-zA-Z]', vip): name += ' [COLOR orange]%s[/COLOR]' % vip

                    addDirectoryItem(name, url, 'ndmode', image, image, fanart2, '0', content, data)
                except:
                    pass


            items = re.compile('<item>(.+?)</item>').findall(link)

            for item in items:
                try:

                    data = {}

                    name = re.findall('<title>(.+?)</title>', item)[0]
                    name = cleantitle(name)

                    if not query.lower() in name.lower() : raise Exception()

                    url = re.findall('<link>(.+?)</link>', item)[0]

                    try: image = re.findall('<thumbnail>(.+?)</thumbnail>', item)[0]
                    except: image = '0'

                    try: fanart2 = re.findall('<fanart>(.+?)</fanart>', item)[0]
                    except: fanart2 = fanart

                    if content =='movies':
                        try:
                            title = cleantitle(name).encode('utf-8')
                            data = {'title': title}

                            title, year = re.compile('(.+?)[(](\d{4})[)]').findall(name)[0]
                            title = cleantitle(title).encode('utf-8')
                            data = {'title': title, 'year': year}
                        except:
                            pass

                    if re.search('[a-zA-Z]', vip): name += ' [COLOR orange]%s[/COLOR]' % vip

                    if 'sublink' in url:
                        addDirectoryItem(name, url, 62, image, image, fanart2, '0', content, data, isFolder=True)
                    else:
                        addDirectoryItem(name, url, 61, image, image, fanart2, '0', content, data, isFolder=False)
                except:
                    pass
        except:
            pass

    control.directory(int(sys.argv[1]), cacheToDisc=True)


def clearSearch():
    cache.clear('rel_srch')
    control.refresh()

def cleantitle(name):
    name = re.sub('(\.|\_|\(|\[|\s)(Link \d*|link \d*)(\.|\_|\)|\]|$)', '', name)
    name = re.sub('\(\d{4}.+?\d{4}\)$', '', name)
    name = re.sub('\s\[COLOR.+?\].+?\[/COLOR\]|\[/COLOR\]\[COLOR.+?\]\s.+?\[/COLOR\]|\[COLOR.+?\]|\[/COLOR\]', '', name)
    name = re.sub('\s\s+', ' ', name)
    name = name.strip()
    return name

def cleaneptitle(tvshow, name):
    try:
        p = re.compile('(S\d*E\d*)').findall(name)
        p += re.compile('(s\d*e\d*)').findall(name)
        p += re.compile('(Season \d* Episode \d*)').findall(name)
        p += re.compile('(\d*x Episode \d*)').findall(name)
        p += re.compile('(\d*x\d*)').findall(name)
        p = p[0]

        name = name.replace(tvshow, '').replace(p, '')
        name = re.sub('-|:', '', name)
        name = re.sub('\s\s+', ' ', name)
        name = name.strip()

        season = re.compile('(\d*)').findall(p)
        season = [i for i in season if i.isdigit()][0]
        season = '%01d' % int(season)

        episode = re.compile('(\d*)').findall(p)
        episode = [i for i in episode if i.isdigit()][-1]
        episode = '%01d' % int(episode)

        if re.match('[A-Z0-9]', name) == None:
            name = '%s S%02dE%02d' % (tvshow, int(season), int(episode))

        return (name, season, episode)
    except:
        return

'''
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

params=get_params()

url=None
name=None
mode=None
iconimage=None
fanart=None
description=None

playlist=None
fav_mode=None
regexs=None

try:
	mode=int(params["mode"])
except:
	pass
		
if mode == 61 or mode == 'Resolve'	: 
	print '***** PLP Resolve'
	resolveUrl(name, url, audio, image, fanart, playable, content)
elif mode == 62 	: 
	print '***** PLP Sub Dir'
	subDirectory(name, url, audio, image, fanart, playable, tvshow, content)
elif mode == 63 	: 
	print '***** PLP Get Dir'
	getDirectory(name, url, audio, image, fanart, playable, content)
'''