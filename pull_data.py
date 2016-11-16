"""
Pull Data - some methods for pulling data out.

Author: Ian Robertson
"""

import datetime
import logging
import os
from bs4 import BeautifulSoup
import requests


def get_site(url, filename):
    """Pulls out the html from a site, and saves it."""
    logging.info('getting {}'.format(url))
    r = requests.get(url)

    t = r.text
    logging.debug('First 100: {}'.format(t[0:100]))

    with open(filename, 'w') as f:
        f.write(t)
        logging.info('Written to file!')


def birthday_clue(wp):
    """Gets a birthday clue based on a WikiParse object

    Parameters
    ----------
    wp : WikiParse
        The wiki parse object
    """
    if wp.bday:
        day_of_month = int(wp.bday.strftime('%d'))
        if day_of_month in (1, 21, 31):
            day_suffix = 'st'
        elif day_of_month in (2, 22):
            day_suffix = 'nd'
        elif day_of_month in (3, 23):
            day_suffix = 'rd'
        else:
            day_suffix = 'th'
        birthday = '{} {}{}, {}'.format(
            wp.bday.strftime('%B'),
            day_of_month,
            day_suffix,
            wp.bday.strftime('%Y'))
        return 'Born ' + birthday
    else:
        return None


class WikiParse():
    """Parses out some info from a wiki page!"""
    
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.soup = BeautifulSoup(f.read(), 'html5lib')
        self._get_infobox()
        self._get_name()
        self._get_image_url()
        self._get_bday()
        self._get_gender()
        self._second_sentence()
        self._get_imdb()
            
    def _get_infobox(self):
        """Grabs infobox"""
        try:
            self.infobox = self.soup.find('table', {'class': 'infobox'})
        except:
            self.infobox = None
            
    def _get_name(self):
        """Grabs the name and whether it's interesting"""
        try:
            nn = self.infobox.find('span', {'class': 'nickname'}).text
            self.nickname = nn
        except AttributeError:
            self.nickname = None

        try:
            self.commonName = self.soup.find(id='firstHeading').text
        except:
            #No main heading????
            self.commonName = None
    
    def _get_image_url(self):
        """Tries to grab an image"""
        try:
            self.imageURL = self.infobox.find('img')['src']
        except:
            self.imageURL = None

    def _get_bday(self):
        """Tries to grab a birthday"""
        try:
            bday_string = self.infobox.find('span', {'class': 'bday'}).text
            self.bday = datetime.datetime.strptime(bday_string, '%Y-%m-%d')
        except:
            self.bday = None

    def _get_gender(self):
        """Tries to grab a gender based on categories"""
        female = ['female', 'actress', 'women']
        male = ['male', 'actor', 'men']
        full_text = self.soup.get_text().lower()
        count_female = full_text.count(' she ') + full_text.count(' her ')
        count_male = full_text.count(' he ') + full_text.count(' his ')

        try:
            #Grabs the text in catlinks id
            catlinks = self.soup.find(id='catlinks').text.lower()
            if any(s in catlinks for s in female):
                self.gender = 'F'
            elif any(s in catlinks for s in male):
                self.gender = 'M'
            else:
                try:
                    ratio_male = float(count_male) / float(count_female)
                except:
                    ratio_male = 1
                if ratio_male > 2:
                    self.gender = 'M'
                elif ratio_male < 0.5:
                    self.gender = 'F'
                else:
                    self.gender = None
        except:
            self.gender = None

    def _second_sentence(self):
        """Second sentence is usually an easy one"""
        t = self.soup.find(id='mw-content-text')

        #Kills the IPA span because it can have periods
        try:
            t.find(class_='IPA').decompose()
        except:
            pass
        tt = '\n'.join([p.text for p in t.find_all('p')])
        self.second_sentence = tt.split('.')[1].strip()
    

    def _get_imdb(self):
        """
        Tries to grab an IMDB link - gets last a href tag matching 
        www.imdb.com/name.
        """
        a_list = self.soup.find_all('a')
        self.imdb_url = None
        for link in a_list:
            try:
                href = link['href']
            except:
                href = ''
            if 'www.imdb.com/name' in href:
                self.imdb_url = href

        if self.imdb_url:
            filename = os.path.join('files', 'imdb', self.imdb_url.replace('/',
                '_'))
            if not os.path.isfile(filename):
                get_site(self.imdb_url, filename)
            with open(filename) as f:
                self.imdb_soup = BeautifulSoup(f.read(), 'html5lib')

    

    def __repr__(self):
        return '<Wiki Parse {0}>'.format(self.commonName)

    def __str__(self):
        attrs = vars(self)
        st = 'Parsing:\n'
        for at in attrs:
            if at not in ['infobox', 'soup', 'imdb_soup']:
                st += '  {0}: {1}\n'.format(at, attrs[at])
        return st


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    urls = [
        'https://en.wikipedia.org/wiki/Michael_Caine',
        'https://en.wikipedia.org/wiki/Melissa_McCarthy',
        'https://en.wikipedia.org/wiki/Sarah_Jessica_Parker',
        'https://en.wikipedia.org/wiki/Jerry_Seinfeld',
        'https://en.wikipedia.org/wiki/Leonardo_DiCaprio',
        'https://en.wikipedia.org/wiki/Sia_Furler',
        'https://en.wikipedia.org/wiki/Matthew_Perry',
        'https://en.wikipedia.org/wiki/Diana,_Princess_of_Wales',
        'https://en.wikipedia.org/wiki/Elizabeth_II',
        'https://en.wikipedia.org/wiki/Donald_Trump',
        'https://en.wikipedia.org/wiki/Harrison_Ford',
        'https://en.wikipedia.org/wiki/Roman_Polanski',
        'https://en.wikipedia.org/wiki/Jack_Nicholson',
        'https://en.wikipedia.org/wiki/Arnold_Schwarzenegger',
        'https://en.wikipedia.org/wiki/Tina_Fey',
        'https://en.wikipedia.org/wiki/Sarah_Palin'
    ]
    for url in urls:
        filename = os.path.join('files', url.replace('/', '_'))
        if not os.path.isfile(filename):
            get_site(url, filename)
        p = WikiParse(filename)
        print(p)
        print(birthday_clue(p))
