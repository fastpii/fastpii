"""
Czech Name Database for PII Detection.

This module contains common Czech first names and surnames with gender classification.
Data sourced from Czech Statistical Office and common naming patterns.

Gender codes:
- 'm' = male
- 'f' = female
"""

# Common Czech male first names (top 100)
MALE_FIRST_NAMES = {
    # Most common male names
    "jan", "josef", "petr", "jaroslav", "jindřich",
    "martin", "vlastimil", "milan", "michal", "tomáš",
    "pavel", "lukáš", "jakub", "jiří", "ondřej",
    "filip", "david", "matěj", "adam", "šimon",
    "marek", "vojtěch", "karel", "stanislav",
    "františek", "antonín", "radoslav",
    "vladimír", "zdeněk", "ivan", "oldřich", "libor",
    "radomír", "rudolf", "jaromír", "vítězslav", "bohumil",
    "miloslav", "bohumir", "václav",
    "bedřich", "ladislav", "vilém", "vladislav",
    "hynek", "boleslav", "dávid", "robert",
    "štefan", "nikoláš", "matyáš", "vít", "štěpán",
    "viktor", "samuel", "jonáš", "daniel", "denis",
    "tobiáš", "benjamín", "matous", "krystof",
    "alexandr", "jáchym", "valentýn", "bogdan",
    "břetislav", "bořivoj", "svatoslav", "mutslav", "svatopluk",
    "božetěch", "hartvik", "budislav", "dobroslav",
    "český", "mojmír", "konrád", "ota",
    "bohuslav", "radovan",
}

# Common Czech female first names (top 100)
FEMALE_FIRST_NAMES = {
    # Most common female names
    "marie", "eva", "jana", "anna", "alena",
    "markéta", "lenka", "tereza", "petra", "katka",
    "michaela", "kateřina", "hanka",
    "adéla", "barbora", "veronika",
    "kristýna", "natálie", "ela", "sofia",
    "amálie", "viktorie", "eliška", "rozálie", "anna",
    "františka", "josefa", "antonie", "karolína",
    "bohumila", "milada", "dagmar", "jarmila",
    "helena", "iva", "jindřiška", "libuše", "radka",
    "zlata", "zuzana", "jitka", "milena", "blanka",
    "daniela", "heda", "suzana", "marcela",
    "daria", "božena", "květoslava", "dáda", "radomila",
    "slavomila", "miloslava", "bohumira", "liběna",
    "růžena", "lidmila", "zdislava",
    "agáta", "bětislava", "božislava", "branislava", "bronislava",
    "časlava", "dálislava", "derislava", "drahomíra", "drahoslava",
    "družoslava", "družislava", "dvořislava", "holoslava", "hostislava",
    "hradislava", "jislava", "křesoslava", "kraslava",
    "ladislava", "luboslava", "ludislava", "ludmila", "milebožena",
}

# Common Czech male surnames (top 100)
MALE_SURNAMES = {
    # Most common surnames
    "novák", "svoboda", "novotný", "dvořák", "černý",
    "procházka", "kučera", "veselý", "horák", "náden",
    "marek", "pospíšil", "holý", "král", "pokorný",
    "růžička", "beneš", "fišer", "sedláček", "kříž",
    "kovář", "větvíčka", "urban", "štajn", "vlk",
    "baláž", "polák", "konečný",
    "malý", "šimek", "kadlec", "mašek", "šmíd",
    "vrabec", "škvára", "šálek", "šmída", "šafařík",
    "bartoš", "kantor", "šnajdr",
    "šulc", "štajf", "sýkora", "kropáč", "kopáč",
    "šenk", "šenkýř", "škvařil", "šmirous", "šplíchal",
    "šťastný", "štefan", "šeiner",
    "šíp", "šín", "toman", "tůma",
    "vacek", "vaněk", "vašák", "vávra", "vojta",
    "vrána", "vrátil", "zeman", "zoubek",
    "žák", "žďárský", "želínský", "žemlička", "ženatý",
    "žert", "žížala", "švec", "šilha",
}

# Common Czech female surnames (top 100) - ending in -ová (married) or masculine form
FEMALE_SURNAMES = {
    # Most common female surnames (-ová endings)
    "nováková", "svobodová", "novotná", "dvořáková", "černá",
    "procházková", "kučerová", "veselá", "horáková", "nádená",
    "marková", "pospíšilová", "holá", "králová", "pokorná",
    "růžičková", "benešová", "fišerová", "sedláčková", "křížová",
    "kovářová", "větvíčková", "urbanová", "štajnová", "vlková",
    "balážová", "poláková", "konečná", "malá",
    "šimková", "kadlcová", "mašková", "šmídová", "vrabcová",
    "škvárová", "šálková", "šafaříková", "bartošová",
    "kantorová", "šnajdrová", "šulcová",
    "štajfová", "sýkorová", "kropáčová", "kopáčová",
    "šenková", "šenkyřová", "škvařilová", "šmirousová", "šplíchalová",
    "šťastná", "štefanová", "šeinerová", "šípová",
    "šínová", "tomanová", "tůmová", "vačková",
    "vaňková", "vašáková", "vávrová", "vojtová",
    "vráňová", "vratilová", "zemanová", "zoubková",
    "žáková", "žďárská", "želínská", "žemličková", "ženatá",
    "žertová", "žížalová", "švecová", "šilhová",
}

# Surname gender patterns
# Female surnames ending in -ová indicate married women
# Female surnames without -ová indicate unmarried women or foreign origin
SURNAME_PATTERNS = {
    "female_married_suffix": "ová",
    "female_married_suffix_alt": ["ova", "ová"],
}

def is_male_name(name: str) -> bool:
    """Check if a first name is typically Czech male."""
    return name.lower() in MALE_FIRST_NAMES

def is_female_name(name: str) -> bool:
    """Check if a first name is typically Czech female."""
    return name.lower() in FEMALE_FIRST_NAMES

def classify_gender_by_firstname(firstname: str) -> str | None:
    """
    Classify gender based on first name.
    
    Returns:
        'm' for male, 'f' for female, None if unknown
    """
    name_lower = firstname.lower().strip()
    
    if name_lower in MALE_FIRST_NAMES:
        return 'm'
    elif name_lower in FEMALE_FIRST_NAMES:
        return 'f'
    else:
        # Fallback: check common suffixes
        if name_lower.endswith('a') or name_lower.endswith('e') or name_lower.endswith('ě'):
            return 'f'  # Most Czech female names end in -a, -e, -ě
        else:
            return 'm'  # Most Czech male names end in consonants
    
def get_name_confidence(name: str) -> float:
    """
    Get confidence score based on name database.
    
    Returns:
        0.95 if in database, 0.75 if common pattern, 0.50 otherwise
    """
    name_lower = name.lower().strip()
    
    if name_lower in MALE_FIRST_NAMES or name_lower in FEMALE_FIRST_NAMES:
        return 0.95
    elif name_lower.endswith('a') or name_lower.endswith('e'):
        return 0.75  # Common female pattern
    elif name_lower[-1] not in 'aeěyi':
        return 0.70  # Likely male (ends in consonant)
    else:
        return 0.50  # Unknown