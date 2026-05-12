"""
Соглашение об именовании файлов структур.

━━━ Источники (source) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {Formula}_{mp_id}          →  UC_mp-72
  {Formula}_{cod_id}         →  NaCl_cod-1000041
  {lattice}_{atom}           →  cubic_f_Al      (синтетические macro)

━━━ Производные (generated) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Суффиксы эффектов (через '+' если несколько):
    vac{N}pct   — N% вакансий
    dev{N}pct   — N% отклонений координат
    noise{N}    — N добавленных шумовых ионов

  Финальный суффикс — трёхзначный индекс варианта: _001, _002, ...

━━━ Примеры ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  UC_mp-72.xyz                          # source
  UC_mp-72_vac5pct_001.xyz              # generated, 5% вакансий
  UC_mp-72_vac5pct+dev2pct_001.xyz      # generated, вакансии + отклонения
  UC_mp-72_noise50_002.xyz              # generated, 50 шумовых ионов
  cubic_f_Al_vac10pct_003.xyz           # generated из синтетической macro
"""

import re

# ─── Паттерн разбора имён ─────────────────────────────────────────────────────

_EFFECT_TOKEN = r'(?:vac\d+pct|dev\d+pct|noise\d+)'
_GENERATED_RE = re.compile(
    r'^(.+?)_((' + _EFFECT_TOKEN + r')(?:\+' + _EFFECT_TOKEN + r')*)(?:_(\d{3,}))?$'
)

# Список известных типов решёток (для парсинга имён синтетических структур)
LATTICE_TYPE_KEYS = [
    "cubic_p", "cubic_i", "cubic_f",
    "tetra_p", "tetra_i",
    "ortho_p", "ortho_i", "ortho_f", "ortho_c",
    "hex_p", "trig_r",
    "mono_p", "mono_c",
    "triclinic",
]


# ─── Публичный API ────────────────────────────────────────────────────────────

def is_generated(stem: str) -> bool:
    """True если имя файла соответствует паттерну generated."""
    return _GENERATED_RE.match(stem) is not None


def get_source_stem(stem: str) -> str:
    """
    Возвращает имя исходного (source) файла, убирая суффиксы эффектов.

    'UC_mp-72_vac5pct_001'  →  'UC_mp-72'
    'cubic_f_Al_vac10pct_003'  →  'cubic_f_Al'
    'UC_mp-72'              →  'UC_mp-72'  (source, без изменений)
    """
    m = _GENERATED_RE.match(stem)
    return m.group(1) if m else stem


def parse_effects(stem: str) -> dict:
    """
    Разбирает суффикс эффектов в словарь.

    'UC_mp-72_vac5pct+dev2pct_001'  →  {'vac': 5, 'dev': 2, 'index': 1}
    'UC_mp-72'                       →  {}
    """
    m = _GENERATED_RE.match(stem)
    if not m:
        return {}

    result = {}
    for token in m.group(2).split('+'):
        n = int(re.search(r'\d+', token).group())
        if token.startswith('vac'):
            result['vac'] = n
        elif token.startswith('dev'):
            result['dev'] = n
        elif token.startswith('noise'):
            result['noise'] = n

    if m.group(4):
        result['index'] = int(m.group(4))

    return result


def make_generated_stem(source_stem: str, effects: dict, index: int) -> str:
    """
    Формирует stem производного файла.

    make_generated_stem('UC_mp-72', {'vac': 5}, 1)          →  'UC_mp-72_vac5pct_001'
    make_generated_stem('UC_mp-72', {'vac': 5, 'dev': 2}, 3) →  'UC_mp-72_vac5pct+dev2pct_003'
    """
    parts = []
    if 'vac'   in effects:
        parts.append(f"vac{effects['vac']}pct")
    if 'dev'   in effects:
        parts.append(f"dev{effects['dev']}pct")
    if 'noise' in effects:
        parts.append(f"noise{effects['noise']}")

    if not parts:
        raise ValueError("effects не может быть пустым для generated файла")

    effects_str = '+'.join(parts)
    return f"{source_stem}_{effects_str}_{index:03d}"


def lattice_type_from_stem(stem: str) -> str | None:
    """
    Извлекает тип решётки из имени синтетической macro-структуры.

    'cubic_f_Al_5x5x5'   →  'cubic_f'
    'hex_p_Zn'           →  'hex_p'
    'UC_mp-72'           →  None  (micro, нужен DB)
    """
    source = get_source_stem(stem)
    for lt in LATTICE_TYPE_KEYS:
        if source.startswith(lt):
            return lt
    return None
