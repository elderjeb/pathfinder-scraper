import requests
from lxml import html


def get_effects(spell_content):
    spell_content = spell_content.replace('saving Throw', 'Saving Throw').replace('Spell-Resistance',
                                                                                  'Spell Resistance').replace(
        'Target restrictions', 'Target Restrictions').replace('Fortitudenegates', 'Fortitude negates').replace(
        'target restrictionsselected', 'Target Restrictions selected')
    keywords = ['Duration', 'Saving Throw', 'Spell Resistance', 'Target Restrictions']
    effects = dict.fromkeys(keywords, '')
    for idx, k in enumerate(keywords):
        start = spell_content.find(k)
        end = -2
        for fidx, fk in enumerate(keywords):
            if fidx > idx:
                end = spell_content.find(fk)
                if end == -1:
                    end = -2
                else:
                    break
        if end == -2 and not (start == -1):
            effects[k] = spell_content[start:].replace(k + ' ', '').replace(';', '').replace('\n', '').replace('\r', '')
        else:
            effects[k] = spell_content[start:end].replace(k + ' ', '').replace(';', '').replace('\n', '').replace('\r',
                                                                                                                  '')
    return effects


def get_valid_targets(target_restrictions):
    target_keywords = ['barrier', 'burst', 'cone', 'line', 'personal', 'selected']
    if target_restrictions == '':
        target_keywords = dict.fromkeys(target_keywords, 'X')
    else:
        target_restrictions = target_restrictions.lower()
        target_keywords = dict.fromkeys(target_keywords, '')
        for k, v in target_keywords.items():
            if target_restrictions.find(k) >= 0:
                target_keywords[k] = 'X'
    return target_keywords


def get_saves(save_str):
    save_str = save_str.lower()
    save_types = dict.fromkeys(['fortitude', 'reflex', 'will'], '')
    if save_str != 'none':
        for k, v in save_types.items():
            if save_str.find(k) >= 0:
                save_types[k] = save_str.replace(k + ' ', '')
    return save_types


def convert_list_elements(elem):
    if type(elem) == html.HtmlElement:
        return elem.text_content().replace(' ', '')
    else:
        return elem.replace(' ', '')


def convert_list_to_dict(lst):
    if type(lst[0]) != html.HtmlElement or lst[0] == ' ':
        lst = lst[1:]
    lst = [convert_list_elements(l) for l in lst]
    if '/' in lst:
        for i in range(0, lst.count('/')):
            idx = lst.index('/')
            l1 = lst[:idx-1]
            l2 = list()
            l2.append(lst[idx-1] + lst[idx] + lst[idx + 1])
            l3 = lst[idx+2:]
            lst = l1 + l2 + l3
    res_dct = {lst[i]: int(lst[i + 1].replace(' ', '').replace(',', '')) for i in range(0, len(lst), 2)}
    return res_dct


def get_min_level(levels_dict):
    bardacle_level = 10
    if is_bardacle_spell(levels_dict):
        bard_level = 10
        oracle_level = 10
        if 'bard' in levels_dict.keys():
            bard_level = levels_dict['bard']
        if 'cleric/oracle' in levels_dict.keys():
            oracle_level = levels_dict['cleric/oracle']
        bardacle_level = min(bard_level, oracle_level)
    else:
        bardacle_level = min(levels_dict.values())
    return bardacle_level


def is_bardacle_spell(levels_dict):
    return 'bard' in levels_dict or 'cleric/oracle' in levels_dict or 'cleric/oracle' in levels_dict
    

with open('words.csv', 'w') as file:
    wordHeadings = 'URL|Name|Category|School|Level|Bardacle Spell|Duration|Fortitude|Reflex|Will|Spell ' \
                   'Resistance|Barrier|Burst|Cone|Line|Personal|Selected|Description|Boost\n '
    wordLine = '{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}\n'
    url = 'https://www.d20pfsrd.com/magic/variant-magic-rules/words-of-power/effect-words/'
    page = requests.get(url)
    file.write(wordHeadings)
    tree = html.fromstring(page.content)
    subpages = tree.xpath('//div[@class="ogn-childpages"]/ul/li/a')
    total = len(subpages)
    index = 1
    for sp in subpages:
        print('' + str(index) + '/' + str(total))
        index = index + 1
        spellUrl = sp.items()[0][1]
        spellPage = requests.get(spellUrl)
        spellTree = html.fromstring(spellPage.content)
        name = spellTree.xpath('.//h1')
        school = spellTree.xpath('//div[@class="article-content"]//p/b[contains(text(),'
                                 '"School")]/following-sibling::*[1]')
        levels = convert_list_to_dict(spellTree.xpath('//div[@class="article-content"]//p[1]/b[contains(text(),'
                                                      '"Level")]/following-sibling::node()'))
        effect = spellTree.xpath('.//div[@class="article-content"]//p[text() = "EFFECT"]/following-sibling::p[1]')
        description = spellTree.xpath(
            './/div[@class="article-content"]//p[text() = "DESCRIPTION"]/following-sibling::p[1]')
        boost = spellTree.xpath('.//b[contains(text(),"Boost")]/parent::p')
        name = name[0].text_content().replace('Light Light', 'Light (light)')
        school = school[0].text_content()
        category = name[name.find('(') + 1:name.find(')')]
        bardacle_spell = ''
        if is_bardacle_spell(levels):
            bardacle_spell = 'X'
        spell_level = get_min_level(levels)
        name = name[:name.find('(') - 1]
        effect = get_effects(effect[0].text_content())
        description = description[0].text_content().replace('\n', '')
        if len(boost) == 0:
            boost = ''
        else:
            boost = boost[0].text_content().replace('Boost: ', '')
        saves = get_saves(effect['Saving Throw'])
        targets = get_valid_targets(effect['Target Restrictions'])
        # print(wordLine.format(name, type, effect['Duration'], saves['fortitude'], saves['reflex'], saves['will'],
        # effect['Spell Resistance'], targets['barrier'], targets['burst'], targets['cone'], targets['line'],
        # targets['personal'], targets['selected'], description, boost))
        file.write(wordLine.format(spellUrl, name, category, school, spell_level, bardacle_spell, effect['Duration'],
                                   saves['fortitude'], saves['reflex'], saves['will'], effect['Spell Resistance'],
                                   targets['barrier'], targets['burst'], targets['cone'], targets['line'],
                                   targets['personal'], targets['selected'], description, boost))
