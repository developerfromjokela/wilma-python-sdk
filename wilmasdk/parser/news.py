#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
import datetime
import bs4


def existenceCheck(dist_item, key):
    return key in dist_item and dist_item[key] is not None


def parseDate(string, date_format):
    try:
        return datetime.datetime.strptime(string, date_format)
    except:
        return None


def optimizeNew(new):
    newNew = {'id': -1, 'limit': {'start': None, 'end': None}, 'topic': None, 'description': None, 'creator': None,
              'created': None, 'content': {'text': None, 'html': None}}
    if existenceCheck(new, 'Id'):
        newNew['id'] = new['Id']
    if existenceCheck(new, 'StartDate'):
        newNew['limit']['start'] = parseDate(new['StartDate'], '%Y-%m-%d')
    if existenceCheck(new, 'EndDate'):
        newNew['limit']['end'] = parseDate(new['EndDate'], '%Y-%m-%d')
    if existenceCheck(new, 'Created'):
        newNew['limit']['created'] = parseDate(new['Created'], '%Y-%m-%d %H:%M')
    if existenceCheck(new, 'ContentHtml'):
        newNew['content']['html'] = new['ContentHtml']
        newNew['content']['test'] = bs4.BeautifulSoup(new['ContentHtml'], 'html.parser').text
    if existenceCheck(new, 'Creator'):
        newNew['creator'] = new['Creator']
    if existenceCheck(new, 'Topic'):
        newNew['topic'] = new['Topic']
    if existenceCheck(new, 'Description'):
        newNew['description'] = new['Description']
    return newNew


def optimizeNews(news):
    newNews = []
    for new in news:
        newNews.append(optimizeNew(new))
    return newNews

