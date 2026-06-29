_REGION_LOADER_MODULES: dict[str, str] = {
    "cz": "fastpii.countries.cz.patterns",
    "pl": "fastpii.countries.pl.patterns",
    "de": "fastpii.countries.de.patterns",
    "fr": "fastpii.countries.fr.patterns",
}

_LOADER_CLASS_NAMES: dict[str, str] = {
    "cz": "CzechPatternLoader",
    "pl": "PolishPatternLoader",
    "de": "GermanPatternLoader",
    "fr": "FrenchPatternLoader",
}


def get_region_loaders() -> dict[str, type]:
    import importlib
    result: dict[str, type] = {}
    for code, module_path in _REGION_LOADER_MODULES.items():
        mod = importlib.import_module(module_path)
        loader_cls = getattr(mod, _LOADER_CLASS_NAMES[code], None)
        if loader_cls is not None:
            result[code] = loader_cls
    return result
