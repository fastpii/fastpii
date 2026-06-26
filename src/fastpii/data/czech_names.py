"""
Czech Name Database for PII Detection.

This module contains common Czech first names and surnames with gender classification.
Data sourced from Czech Statistical Office and common naming patterns.

Gender codes:
- 'm' = male
- 'f' = female
"""

class CzechNamesDatabase:
    MALE_SURNAMES: set[str] = {
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

    FEMALE_SURNAMES: set[str] = {
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

    MALE_FIRST_NAMES: set[str] = {
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

    FEMALE_FIRST_NAMES: set[str] = {
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

    SURNAME_PATTERNS: dict[str, object] = {
        "female_married_suffix": "ová",
        "female_married_suffix_alt": ["ova", "ová"],
    }

    def is_male_name(self, name: str) -> bool:
        return name.lower() in self.MALE_FIRST_NAMES

    def is_female_name(self, name: str) -> bool:
        return name.lower() in self.FEMALE_FIRST_NAMES

    def classify_gender_by_firstname(self, firstname: str) -> str | None:
        name_lower = firstname.lower().strip()

        if name_lower in self.MALE_FIRST_NAMES:
            return 'm'
        elif name_lower in self.FEMALE_FIRST_NAMES:
            return 'f'
        else:
            if name_lower.endswith('a') or name_lower.endswith('e') or name_lower.endswith('ě'):
                return 'f'
            else:
                return 'm'

    def get_name_confidence(self, name: str) -> float:
        name_lower = name.lower().strip()

        if name_lower in self.MALE_FIRST_NAMES or name_lower in self.FEMALE_FIRST_NAMES:
            return 0.95
        elif name_lower.endswith('a') or name_lower.endswith('e'):
            return 0.75
        elif name_lower[-1] not in 'aeěyi':
            return 0.70
        else:
            return 0.50


DEFAULT_NAMES = CzechNamesDatabase()

MALE_SURNAMES = DEFAULT_NAMES.MALE_SURNAMES
FEMALE_SURNAMES = DEFAULT_NAMES.FEMALE_SURNAMES
MALE_FIRST_NAMES = DEFAULT_NAMES.MALE_FIRST_NAMES
FEMALE_FIRST_NAMES = DEFAULT_NAMES.FEMALE_FIRST_NAMES

def is_male_name(name: str) -> bool:
    return DEFAULT_NAMES.is_male_name(name)

def is_female_name(name: str) -> bool:
    return DEFAULT_NAMES.is_female_name(name)

def classify_gender_by_firstname(firstname: str) -> str | None:
    return DEFAULT_NAMES.classify_gender_by_firstname(firstname)

def get_name_confidence(name: str) -> float:
    return DEFAULT_NAMES.get_name_confidence(name)