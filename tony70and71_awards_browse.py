from juicer.utils import *
import MySQLdb
import requests

DOMAIN = 'https://en.wikipedia.org'

class Tony70and71Awards(JuicerSpider):

    start_urls = ['https://en.wikipedia.org/wiki/70th_Tony_Awards',
                  'https://en.wikipedia.org/wiki/71st_Tony_Awards',
		  'https://en.wikipedia.org/wiki/54th_Tony_Awards',
                  'https://en.wikipedia.org/wiki/55th_Tony_Awards',
                  'https://en.wikipedia.org/wiki/56th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/57th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/58th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/59th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/60th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/61st_Tony_Awards',
		  'https://en.wikipedia.org/wiki/62nd_Tony_Awards',
		  'https://en.wikipedia.org/wiki/63rd_Tony_Awards',
		  'https://en.wikipedia.org/wiki/64th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/65th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/66th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/67th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/68th_Tony_Awards',
		  'https://en.wikipedia.org/wiki/69th_Tony_Awards']
    name = "tony70and71_awards_browse"

    def __init__(self, *args, **kwargs):
        super(Tony70and71Awards, self).__init__(*args, **kwargs)
        self.URL = 'https://en.wikipedia.org'
        self.query = "insert ignore into wiki_awards_history(award_gid, award_title, category_gid, category_title, year, location, winner_nominee, program_title, role, persons, created_at, modified_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
        self.ceremony_query = 'select category_gid, category_title from award_ceremony_categories where award_id= "25" and category_title like "%s"'
        self.conn = MySQLdb.connect(user="root", host = "localhost",passwd = "ranjan07", db="AWARDS", use_unicode=True)
        self.cur  = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        self.cur.close()

    def wiki_gid(self,url):
        data = requests.get(url).text
        wiki_gi = re.findall('"wgArticleId":(\d+),', data)[0]
        sel = Selector(text=data)
        wikititle = extract_data(sel, '//div[@id="content"]/h1[@id="firstHeading"]//text()')
        wikititle = re.sub('\((.*?)\)','',wikititle)
        wikititle = wikititle.strip()
        if wiki_gi:
            wikigid = 'WIKI' + wiki_gi
            return wikigid,wikititle

    def wiki_gid_table(self, text):
        pattern_ = "%s%s%s"%('%',text,'%')
        self.cur.execute(self.ceremony_query%pattern_)
        text1 = self.cur.fetchall()
        if text1:
            text1 = text1[0]
            if len(text1) == 2:
                return text1[0], text1[1]

    def parse(self,response):
        sel =  Selector(response)
        award_title = 'Tony Award'
        award_gid = 'WIKI54741'
        if '70' in response.url:
            year = '2016'
            location = "Beacon Theatre"
        else:
            year = '2017'
            location = "Radio City Music Hall, Manhattan, New York City"
        nodes = sel.xpath('//table[@class="wikitable"]')
        for nd in nodes:
            heading_nodes = nd.xpath('./tr')[::2]
            award_nodes = nd.xpath('./tr')[1::2]
            for (i,j) in zip (heading_nodes,award_nodes):
                first = i.xpath('./th')
                second = j.xpath('./td')
                if len(first) == len(second):
                    for (f,s) in zip(first,second):
                        category_link, category_link_text = ['']*2
                        category_link = f.xpath('./a/@href').extract()
                        category_link_text = textify(f.xpath('./a/text()').extract())
                        if category_link:
                            category_link = [category_link[0]]
                        if category_link:
                            category_gid = self.wiki_gid(DOMAIN+textify(category_link))
                        else:
                            if category_link_text:
                                category_gid = self.wiki_gid_table(category_link_text)
                        music_awar_list = s.xpath('./ul//li')
                        for i in music_awar_list:
                            winner_type = ''
                            if '<b>' in str(i.xpath('./self::node()')):
                                winner_type = 'winner'
                            else:
                                winner_type = 'nominee'
                            whole_txt = textify(i.xpath('.//text()').extract())
                            program_link, befor_lks, role_link = [],[],[]
                            if ' as ' in whole_txt and u'\u2013' in whole_txt:
                                if winner_type == 'winner':
                                    program_link = i.xpath('./b//i/a[@title]/@href').extract()
                                    befor_lks = i.xpath('./b/i//../preceding-sibling::a/@href').extract()
                                    if ' as ' in whole_txt:
                                        role_link = i.xpath('./b//text()[contains(.," as ")]/following-sibling::a/@href').extract()
                                        if not role_link:
                                            role_link = i.xpath('./b/i/following-sibling::text()').extract()
                                else:
                                    program_link = i.xpath('./i/a[@title]/@href').extract()
                                    if not program_link:
                                        program_link = i.xpath('./i/text()').extract()
                                    befor_lks = i.xpath('./i//preceding-sibling::a/@href').extract()
                                    if not befor_lks:
                                        befor_lks = i.xpath('./i//preceding-sibling::text()').extract()
                                    if ' as ' in whole_txt:
                                        role_link = i.xpath('./text()[contains(.," as ")]/following-sibling::a/@href').extract()
                                        if not role_link:
                                            role_link = i.xpath('./i/following-sibling::text()').extract()
                                        as_text =  i.xpath('./text()[contains(.," as ")]').extract()
                                        role_link.extend(as_text)
                            elif u'\u2013' in whole_txt:
                                if winner_type == 'winner':
                                    program_link = i.xpath('./b/i/a[@title]/@href').extract()
                                else:
                                    program_link = i.xpath('./i/a[@title]/@href').extract()
                                if not program_link:
                                        program_link = i.xpath('./i/text()').extract()
                                another_be = i.xpath('./text()[contains(.,"%s")]'%u"\u2013").extract()
                                if another_be:
                                    befor_lks.extend(another_be)
                                checkcon = i.xpath('./text()[contains(.," and ")]').extract()
                                if checkcon:
                                    befor_lks.extend(checkcon)
                                check_list = ['Best Book of a Musical',
                                            'Best Original Score (Music and/or Lyrics) Written for the Theatre']
                                if winner_type == 'winner':
                                    if year == '2016' and category_link_text in check_list:
                                        befor_an = i.xpath('./b//i/following-sibling::a/@href').extract()
                                        if not befor_an:
                                            befor_an = i.xpath('./b//i/following-sibling::text()').extract()
                                    else:
                                        befor_an = i.xpath('./b//i//../preceding-sibling::a/@href').extract()
                                        if not befor_an:
                                            befor_an = i.xpath('./b//i//../preceding-sibling::text()').extract()
                                else:
                                    if year == '2016' and category_link_text in check_list:
                                        befor_an = i.xpath('./i/following-sibling::a/@href').extract()
                                        if not befor_an:
                                            befor_an = i.xpath('./i/following-sibling::text()').extract()
                                    else:
                                        befor_an = i.xpath('./i//../preceding-sibling::a/@href').extract()
                                        if not befor_an:
                                            befor_an = i.xpath('./i//../preceding-sibling::text()').extract()
                                if befor_an:
                                    befor_lks.extend(befor_an)

                            else:
                                if winner_type == 'winner':
                                    program_link = i.xpath('.//b//a[@title]/@href').extract()
                                else:
                                    program_link = i.xpath('.//a[@title]/@href').extract()
                                if program_link:
                                    program_link = [program_link[0]]
                                else:
                                    if winner_type == 'winner':
                                        program_link = i.xpath('.//b//text()').extract()
                                    else:
                                        program_link = i.xpath('./i/text()').extract()
                            final_persons_withgid,final_programs_withgid, roles_withgid, songswith_gid = [],[],[],[]
                            list_fin = []
                            list_fin.append(('program',set(program_link)))
                            list_fin.append(('person', set(befor_lks)))
                            list_fin.append(('role', set(role_link)))
                            for fper in list_fin:
                                for fpro in fper[1]:
                                    if "/wiki/" in fpro:
                                        wikiwith = self.wiki_gid(DOMAIN+fpro)
                                        if ' and ' in wikiwith[1] and year == '2017':
                                            names = wikiwith[1].split(' and ')
                                            name = names[0].strip()+'{%s}'%wikiwith[0].strip() + '<>' + names[1].strip()+'{%s}'%wikiwith[0].strip()
                                        else:
                                            name = wikiwith[1].strip() + '{%s}' %wikiwith[0].strip()
                                        name = re.sub('\((.*?)\)','',name)
                                        name = name.strip()
                                        if 'program' in fper[0]:
                                            if name: final_programs_withgid.append(name)
                                        if 'person' in fper[0]:
                                            if name: final_persons_withgid.append(name)
                                        if 'role' in fper[0]:
                                            if name: roles_withgid.append(name)
                                    else:
                                        if 'program' in fper[0]: 
                                            if fpro: final_programs_withgid.append(self.clean(fpro, year))
                                        if 'person' in fper[0]:
                                            if fpro: final_persons_withgid.append(self.clean(fpro, year))
                                        if 'role' in fper[0]:
                                            if fpro: roles_withgid.append(self.clean(fpro, year).replace(' / ','<>').replace('/','<>'))
                            final_persons_withgid = [ik for ik in final_persons_withgid if ik != '']
                            final_programs_withgid = [ik for ik in final_programs_withgid if ik != '']
                            roles_withgid = [ik for ik in roles_withgid if ik != '']
                            if final_persons_withgid == []: final_persons_withgi  = ''
                            if final_programs_withgid == []: final_programs_withgid = ''
                            if roles_withgid == []: roles_withgid = ''
                            if songswith_gid == []: songswith_gid = ''
                            program_check = '<>'.join(final_programs_withgid).strip('<>')
                            values  =( (normalize(award_gid)),normalize(award_title),normalize(category_gid[0]),normalize(category_gid[1]),year,normalize(location),normalize(winner_type),normalize(program_check.strip().replace('<><>','<>')),normalize('<>'.join(roles_withgid).replace('others', '').replace('<><>','<>').strip('<>')),normalize('<>'.join(final_persons_withgid).replace('<><>','<>').replace('<>,<>', '<>').replace('<>,', '<>').strip('<>')))
                            self.cur.execute(self.query, values)
                                    
    def clean(self, text1, year):

        text1 = text1.replace(' and ',',')
        text1 = re.sub('\((.*?)\)','',text1)
        txt_lst = []
        if year == '2017':
            txt_lst = text1.split(',')
        else:
            txt_lst.append(text1)
        text_list = []
        for text in txt_lst:
            text = text.replace(' and ','').replace(' as ','').replace(u'\u2013','').strip().replace('<>','').replace('(','').strip().replace('as ','').replace('*Nominees to be determined*','').strip()
            text = re.sub('\((.*?)\)','',text)
            text = text.strip()
            if text:
                text_list.append(text)
        return '<>'.join(text_list)
