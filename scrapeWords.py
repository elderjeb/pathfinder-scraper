import requests
import util
from lxml import html

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
        levels = util.convert_list_to_dict(spellTree.xpath('//div[@class="article-content"]//p[1]/b[contains(text(),'
                                                      '"Level")]/following-sibling::node()'))
        effect = spellTree.xpath('.//div[@class="article-content"]//p[text() = "EFFECT"]/following-sibling::p[1]')
        description = spellTree.xpath(
            './/div[@class="article-content"]//p[text() = "DESCRIPTION"]/following-sibling::p[1]')
        boost = spellTree.xpath('.//b[contains(text(),"Boost")]/parent::p')
        name = name[0].text_content().replace('Light Light', 'Light (light)')
        school = school[0].text_content()
        category = name[name.find('(') + 1:name.find(')')]
        bardacle_spell = ''
        if util.is_bardacle_spell(levels):
            bardacle_spell = 'X'
        spell_level = util.get_min_level(levels)
        name = name[:name.find('(') - 1]
        effect = util.get_effects(effect[0].text_content())
        description = description[0].text_content().replace('\n', '')
        if len(boost) == 0:
            boost = ''
        else:
            boost = boost[0].text_content().replace('Boost: ', '')
        saves = util.get_saves(effect['Saving Throw'])
        targets = util.get_valid_targets(effect['Target Restrictions'])
        # print(wordLine.format(name, type, effect['Duration'], saves['fortitude'], saves['reflex'], saves['will'],
        # effect['Spell Resistance'], targets['barrier'], targets['burst'], targets['cone'], targets['line'],
        # targets['personal'], targets['selected'], description, boost))
        file.write(wordLine.format(spellUrl, name, category, school, spell_level, bardacle_spell, effect['Duration'],
                                   saves['fortitude'], saves['reflex'], saves['will'], effect['Spell Resistance'],
                                   targets['barrier'], targets['burst'], targets['cone'], targets['line'],
                                   targets['personal'], targets['selected'], description, boost))