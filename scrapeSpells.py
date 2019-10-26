import requests
import util
from lxml import html

with open('spells.psv', 'w') as file:
    wordHeadings = 'URL|Name|School|Subtype|Level|Casting Time|Components|Range|' \
                   'Target|Duration|Fortitude|Reflex|Will|Spell Resistance|Description|Parsing Error\n'
    wordLine = '{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|\n'
    errorLine = '{}|{}||||||||||||||{}\n'
    url = 'https://www.d20pfsrd.com/magic/all-spells/'
    # url = 'https://www.d20pfsrd.com/magic/all-spells/d/'
    start = 'https://www.d20pfsrd.com/magic/all-spells/w/windy-escape/'
    started = True
    page = requests.get(url)
    file.write(wordHeadings)
    tree = html.fromstring(page.content)
    subpages = tree.xpath('//li[@class="page new parent"]/a')
    total = len(subpages)
    index = 1
    for sp in subpages:
        spellUrl = sp.items()[0][1]
        if not started and spellUrl != start:
            index = index + 1
            continue
        else:
            started = True
        spellTree = util.get_spell_tree(spellUrl)
        name = spellTree.xpath('.//h1')
        name = name[0].text_content().replace('Light Light', 'Light (light)')
        if name == 'Charm Fey':
            file.write(errorLine.format(spellUrl, name, 'See Charm Person, but for Fey'))
            continue
        if 'I-I' in name:
            file.write(errorLine.format(spellUrl, name, 'Advanced Versions: Skipping for now'))
            continue
        if name == 'Locksight' or name == 'Peace Bond' or name == 'Undeath Inversion' or \
           name == 'Windy Escape':
            file.write(errorLine.format(spellUrl, name, 'They bunged up the levels and I cannot deal'))
            continue
        if name == 'Lucky Number' or name == 'Mathematical Curse' or name == 'Marionette Possession' or \
           name == 'Necromantic Burden' or name == 'Release Fury' or name == 'Riding Possession' or \
           name == 'Shining Scales' or name == 'Passwall':
            file.write(errorLine.format(spellUrl, name, 'Don\'t even get me started on how bad this page is...'))
            continue
        if index % 100 == 0:
            print('' + str(index) + '/' + str(total) + ' (' + name + ')')
        index = index + 1
        lesser = spellTree.xpath('//*[contains(text(),"Lesser")]')
        greater = spellTree.xpath('//*[contains(text(),"Greater")]')
        communal = spellTree.xpath('//*[contains(text(),"Communal")]')
        major = spellTree.xpath('//*[contains(text(),"' + name + ', Major")]')
        advanced = spellTree.xpath('//*[contains(text(),"' + name + 'I") or contains(text(), "' + name + ' II")]')
        mass = spellTree.xpath('//*[contains(text(),"Mass")]')
        functionsAs = spellTree.xpath('//*[contains(text(), "This spell functions as") or contains(text(), ' \
                                      '"it functions as")]/a[1]')
        pathOfNumbers = spellTree.xpath('//*[contains(text(),"The Path of Numbers")]')
        if len(pathOfNumbers) > 0:
            file.write(errorLine.format(spellUrl, name, 'The Path of Numbers is poorly formatted...'))
            continue
        if len(functionsAs) > 0:
            file.write(errorLine.format(spellUrl, name, 'This spell functions as ' + functionsAs[0].text_content()))
            continue
        if len(lesser) > 0 or len(greater) > 0 or len(communal) > 0 or len(mass) > 0 or len(advanced) or len(major) > 0:
            file.write(errorLine.format(spellUrl, name, 'Has Greater/Lesser/Communal/Mass/Advanced/Major: Skipping'))
            continue
        school_levels = spellTree.xpath('//div[@class="article-content"]//p[b[contains(text(),"School")]][1]/node()')
        if not util.is_wizard_spell(school_levels):
            file.write(errorLine.format(spellUrl, name, 'Not a Wizard Spell'))
            continue
        school_levels = util.get_school_and_level(school_levels)
        school = school_levels['school']
        levels = school_levels['levels']
        casting = spellTree.xpath('//div[@class="article-content"]//p[text() = "CASTING"]/following-sibling::p['
                                  '1]/node()')
        casting = util.get_casting_time_and_components(casting)
        if 'Casting Time' in casting:
            castingTime = casting['Casting Time']
        else:
            castingTime = ''
        if 'Components' in casting:
            components = casting['Components']
        else:
            components = ''

        effect = spellTree.xpath('.//div[@class="article-content"]//p[text() = "EFFECT" or text() = '
                                 '"EFFECTS"]/following-sibling::p[1]')
        
        description = spellTree.xpath(
            './/div[@class="page-center"]//p[text() = "DESCRIPTION"]/following-sibling::p[1]')
        description = description[0].text_content().replace('\n', '')
        boost = spellTree.xpath('.//b[contains(text(),"Boost")]/parent::p')
        subtypes = ', '.join(school['subtypes'])
        school = school['school']
        wizard_spell = ''
        if util.is_wizard_spell(levels):
            wizard_spell = 'X'
        spell_level = util.get_min_level(levels)
        if '(' in name:
            name = name[:name.find('(') - 1]
        if len(effect) == 0:
            effect = ''
        else:
            effect = effect[0].text_content()
        effect = util.get_effects(effect)
        saves = util.get_saves(effect['Saving Throw'])
        targets = util.get_valid_targets(effect['Target Restrictions'])
        # print(wordLine.format(name, type, effect['Duration'], saves['fortitude'], saves['reflex'], saves['will'],
        # effect['Spell Resistance'], targets['barrier'], targets['burst'], targets['cone'], targets['line'],
        # targets['personal'], targets['selected'], description, boost))

        # wordHeadings = 'URL|Name|School|Subtype|Wizard Spell|Level|Casting Time|Verbal|Somatic|Material|Focus|Range|'\
        #                'Target|Duration|Fortitude|Reflex|Will|Spell Resistance|Description\n '
        line = wordLine.format(spellUrl, name, school, subtypes, spell_level, castingTime, components,
                               effect['Range'], effect['Target'], effect['Duration'],
                               saves['fortitude'], saves['reflex'], saves['will'], effect['Spell Resistance'],
                               description).replace('ﬃ', 'ffi').replace('ﬂ', 'fl').replace('′', '')
        # print(spellUrl)
        # print(name)
        # print(school)
        # print(subtypes)
        # print(wizard_spell)
        # print(spell_level)
        # print(effect['Range'])
        # print(effect['Target'])
        # print(effect['Duration'])
        # print(saves['fortitude'])
        # print(saves['reflex'])
        # print(saves['will'])
        # print(effect['Spell Resistance'])
        # print(description)
        # print(line)
        file.write(line)
