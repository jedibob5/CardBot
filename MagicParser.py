import scrython


def parse_magic_card(card_name):
    try:
        card = scrython.cards.Named(fuzzy=card_name)
        return parse_slack_response(card)
    except:
        return "Sorry, card not found!"


def parse_slack_response(card):
    try:
        card_text = card.oracle_text()
    except KeyError:
        card_text = ""
    try:
        flavor_text_raw = card.flavor_text().split('\n')
        flavor_text = []
        for line in flavor_text_raw:
            line = "_" + line + '_'
            flavor_text.append(line)
        flavor_text = '\n'.join(flavor_text)
    except KeyError:
        flavor_text = ""
    if 'Creature' in card.type_line() or 'Vehicle' in card.type_line():
        pt = card.power() + '/' + card.toughness()
    else:
        pt = ""
    if card.mana_cost():
        mana_cost = card.mana_cost()
    else:
        mana_cost = ""
    if 'Planeswalker' in card.type_line():
        loyalty = "Loyalty: " + card.loyalty()
    else:
        loyalty = ""

    response = """
{imageurl}
*{cardname}* {mana_cost}
{type_line}
{oracle_text}
{flavor_text}
{PT}{loyalty}
    """.format(
        cardname=card.name(),
        mana_cost=mana_cost,
        type_line=card.type_line(),
        oracle_text=card_text,
        flavor_text=flavor_text,
        PT=pt,
        loyalty=loyalty,
        imageurl=card.image_uris(image_type='normal')
    )
    return response
    # response = list()
    # response.append("*" + card.name() + "*")
    # if card.mana_cost:
    #     response.append(" " + card.mana_cost())
    # response.append('\n')
    # response.append(card.type)
    # response.append('\n')
    # response.append(card.text + '\n')
    # if card.flavor:
    #     response.append("_" + card.flavor + "_" + '\n')
    # if "Creature" in card.type or "Vehicle" in card.subtypes:
    #     response.append(card.power + "/" + card.toughness)
    # if "Planeswalker" in card.type:
    #     response.append("Starting Loyalty: " + card.loyalty)
    # return "".join(response)
