import requests
import re
from lxml import html


def get_spell_tree(url):
    return html.fromstring(requests.get(url).content)


def get_effects(spell_content):
    spell_content = spell_content.replace('saving Throw', 'Saving Throw').replace('Spell-Resistance',
                                                                                  'Spell Resistance').replace(
        'Target restrictions', 'Target Restrictions').replace('Fortitudenegates', 'Fortitude negates').replace(
        'target restrictionsselected', 'Target Restrictions selected')
    keywords = ['Range', 'Target', 'Duration', 'Saving Throw', 'Spell Resistance', 'Target Restrictions']
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


def the_replacer(elem):
    if type(elem) == html.HtmlElement:
        elem = elem.text_content()
    return elem.replace(' ', '').replace(',', '').replace(';', '').replace('(', '').replace(')', '').replace('[', '')\
               .replace(']', '').replace('*', '').replace('unchained', '').replace('mesmeris', '')


def the_lesser_replacer(elem):
    if type(elem) == html.HtmlElement:
        elem = elem.text_content()
    return elem.strip()


def convert_list_elements(elem):
    if type(elem) == html.HtmlElement:
        return elem.text_content().replace(' ', '').replace(',', '').replace(';', '')\
                                  .replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    else:
        return elem.replace(' ', '').replace(',', '').replace(';', '')\
                                    .replace('(', '').replace(')', '').replace('[', '').replace(']', '')


def convert_list_to_dict(lst):
    lst = [the_replacer(x) for x in lst if the_replacer(x) != '']
    if '/' in lst:
        for i in range(0, lst.count('/')):
            idx = lst.index('/')
            l1 = lst[:idx-1]
            l2 = list()
            l2.append(lst[idx-1] + lst[idx] + lst[idx + 1])
            l3 = lst[idx+2:]
            lst = l1 + l2 + l3
    res_dct = {lst[i]: int(lst[i + 1]) for i in range(0, len(lst), 2)}
    return res_dct


def get_school_and_level(lst):
    lst = [the_replacer(x) for x in lst if the_replacer(x) != '']
    regex = re.compile('.*[a-zA-Z]+\d.*')
    lst = [l for l in lst if regex.match(l) is None]
    lvlidx = lst.index('Level')
    if 'Bloodline' in lst:
        lst.remove('Bloodline')
    if 'ElementalSchool' in lst:
        lst.remove('ElementalSchool')
    if 'Domain' in lst:
        didx = lst.index('Domain')
    else:
        didx = len(lst)
    if 'Subdomain' in lst:
        sdidx = lst.index('Subdomain')
    else:
        sdidx = len(lst)
    if 'Domainsubdomain' in lst:
        dsdidx = lst.index('Domainsubdomain')
    else:
        dsdidx = len(lst)
    if 'Domainsubdomains' in lst:
        dsdsidx = lst.index('Domainsubdomains')
    else:
        dsdsidx = len(lst)
    if 'Domainssubdomains' in lst:
        dssdsidx = lst.index('Domainssubdomains')
    else:
        dssdsidx = len(lst)
    school = get_school_and_subtypes(lst[1:lvlidx])
    levels = get_levels(lst[lvlidx+1:min(didx, sdidx, dsdidx, dsdsidx, dssdsidx)])
    return {'school': school, 'levels': levels}
    
    
def get_school_and_subtypes(lst):
    school = lst[0]
    subtypes = lst[1:]
    return {'school': school, 'subtypes': subtypes}


def get_levels(lst):
    if '/' in lst:
        for i in range(0, lst.count('/')):
            idx = lst.index('/')
            l1 = lst[:idx-1]
            l2 = list()
            l2.append(lst[idx-1] + lst[idx] + lst[idx + 1])
            l3 = lst[idx+2:]
            lst = l1 + l2 + l3
    res_dct = {lst[i]: int(lst[i + 1]) for i in range(0, len(lst), 2)}
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


def get_casting_time_and_components(lst):
    lst = [the_lesser_replacer(x) for x in lst if the_lesser_replacer(x) != '']
    ret_dict = {'Components': '', 'Casting Time': ''}
    if 'Components' in lst:
        cidx = lst.index('Components')
        ret_dict['Components'] = ''.join(lst[cidx + 1:])
        lst = lst[:cidx]
    if 'Casting Time' in lst:
        cidx = lst.index('Casting Time')
        ret_dict['Casting Time'] = ' '.join(lst[cidx + 1:])
        
    return ret_dict
    

def is_bardacle_spell(levels_dict):
    return 'bard' in levels_dict or 'cleric/oracle' in levels_dict or 'cleric/oracle/warpriest' in levels_dict
    
    
def is_wizard_spell(lst):
    lst = [the_lesser_replacer(x) for x in lst if the_lesser_replacer(x) != '']
    return 'sorcerer/wizard' in lst


