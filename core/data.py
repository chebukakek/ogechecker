import pandas as pd

TASKS = tuple(range(1, 11))

WORK_REQUIRED = [
    "Класс", "Фамилия", "Имя", "Вариант",
    *[str(number) for number in TASKS],
]
KEY_REQUIRED = ["Вариант", *[str(number) for number in TASKS]]


def normalize_cell(value):
    """Преобразует значение ячейки Excel в строку."""
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip()


def _normalize_columns(frame):
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def load_exam(uploaded_file):
    """
    Загружает книгу Excel с двумя листами:
    «Работы» — ответы учеников;
    «Ключи» — правильные ответы по вариантам.
    """
    try:
        works = pd.read_excel(
            uploaded_file, sheet_name="Работы", dtype=object
        )
        keys = pd.read_excel(
            uploaded_file, sheet_name="Ключи", dtype=object
        )
    except Exception as error:
        raise ValueError(
            "Не удалось прочитать Excel-файл. Проверь, что в нём есть "
            "листы «Работы» и «Ключи»."
        ) from error

    works = _normalize_columns(works)
    keys = _normalize_columns(keys)

    missing_work = [column for column in WORK_REQUIRED if column not in works.columns]
    missing_key = [column for column in KEY_REQUIRED if column not in keys.columns]

    if missing_work:
        raise ValueError(
            "На листе «Работы» отсутствуют столбцы: "
            + ", ".join(missing_work)
        )
    if missing_key:
        raise ValueError(
            "На листе «Ключи» отсутствуют столбцы: "
            + ", ".join(missing_key)
        )

    work_columns = [
        column for column in
        ["Класс", "Литера", "Фамилия", "Имя", "Отчество", "Вариант"]
        if column in works.columns
    ] + [str(number) for number in TASKS]

    for column in work_columns:
        works[column] = works[column].map(normalize_cell)

    keys["Вариант"] = keys["Вариант"].map(normalize_cell)
    for number in TASKS:
        keys[str(number)] = keys[str(number)].map(normalize_cell)

    # Удаляем только полностью пустые строки ученической таблицы.
    identity_columns = ["Фамилия", "Имя", "Вариант"]
    works = works[
        works[identity_columns].apply(
            lambda row: any(value != "" for value in row), axis=1
        )
    ].copy()

    keys = keys[keys["Вариант"] != ""].copy()

    if works.empty:
        raise ValueError("На листе «Работы» не найдено ученических записей.")
    if keys.empty:
        raise ValueError("На листе «Ключи» не найдено ни одного варианта.")
    if keys["Вариант"].duplicated().any():
        duplicates = keys.loc[
            keys["Вариант"].duplicated(keep=False), "Вариант"
        ].unique()
        raise ValueError(
            "На листе «Ключи» повторяются варианты: "
            + ", ".join(duplicates)
        )

    key_map = {
        row["Вариант"]: [row[str(number)] for number in TASKS]
        for _, row in keys.iterrows()
    }

    for variant, answers in key_map.items():
        empty_tasks = [
            str(index + 1) for index, answer in enumerate(answers)
            if answer == ""
        ]
        if empty_tasks:
            raise ValueError(
                f"В ключе варианта «{variant}» не заполнены задания: "
                + ", ".join(empty_tasks)
            )

    missing_variants = sorted(set(works["Вариант"]) - set(key_map))
    if missing_variants:
        raise ValueError(
            "Для следующих вариантов нет ключей: "
            + ", ".join(missing_variants)
        )

    return works.reset_index(drop=True), key_map
