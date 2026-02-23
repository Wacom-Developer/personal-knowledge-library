# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom. All rights reserved.
from typing import NewType, List, Dict

#  ---------------------------------------- Type definitions -----------------------------------------------------------
LanguageCode = NewType("LanguageCode", str)
LocaleCode = NewType("LocaleCode", str)
# ------------------------------------------------ Language codes ------------------------------------------------------
EN_US: LocaleCode = LocaleCode("en_US")
JA_JP: LocaleCode = LocaleCode("ja_JP")
DE_DE: LocaleCode = LocaleCode("de_DE")
BG_BG: LocaleCode = LocaleCode("bg_BG")
FR_FR: LocaleCode = LocaleCode("fr_FR")
IT_IT: LocaleCode = LocaleCode("it_IT")
ES_ES: LocaleCode = LocaleCode("es_ES")
EN: LanguageCode = LanguageCode("en")
DE: LanguageCode = LanguageCode("de")
BG: LanguageCode = LanguageCode("bg")
JA: LanguageCode = LanguageCode("ja")
FR: LanguageCode = LanguageCode("fr")
IT: LanguageCode = LanguageCode("it")
ES: LanguageCode = LanguageCode("es")
# ----------------------------------------------------------------------------------------------------------------------
SUPPORTED_LOCALES: List[LocaleCode] = [JA_JP, EN_US, DE_DE, BG_BG, IT_IT]
SUPPORTED_LANGUAGES: List[LanguageCode] = [JA, EN, DE, BG, IT]
NEL_SUPPORTED_LOCALES: List[LocaleCode] = [EN_US, DE_DE, JA_JP]
NEL_SUPPORTED_LANGUAGES: List[LanguageCode] = [EN, DE, JA]
FULL_TEXT_SEARCH_LOCALES: List[LocaleCode] = [JA_JP, EN_US, DE_DE, BG_BG, IT_IT]
FULL_TEXT_SEARCH_LANGUAGES: List[LanguageCode] = [JA, EN, DE, BG, IT]
VECTOR_SEARCH_LOCALES: List[LocaleCode] = [JA_JP, EN_US, DE_DE, BG_BG, IT_IT]
VECTOR_SEARCH_LANGUAGES: List[LanguageCode] = [JA, EN, DE, BG, IT]

LANGUAGE_LOCALE_MAPPING: Dict[LanguageCode, LocaleCode] = dict(list(zip(SUPPORTED_LANGUAGES, SUPPORTED_LOCALES)))
LOCALE_LANGUAGE_MAPPING: Dict[LocaleCode, LanguageCode] = dict(list(zip(SUPPORTED_LOCALES, SUPPORTED_LANGUAGES)))

__all__ = [
    # Type definitions
    "LanguageCode",
    "LocaleCode",
    # Locale codes
    "EN_US",
    "JA_JP",
    "DE_DE",
    "BG_BG",
    "FR_FR",
    "IT_IT",
    "ES_ES",
    # Language codes
    "EN",
    "DE",
    "BG",
    "JA",
    "FR",
    "IT",
    "ES",
    # Mappings
    "SUPPORTED_LOCALES",
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_LOCALE_MAPPING",
    "LOCALE_LANGUAGE_MAPPING",
]
