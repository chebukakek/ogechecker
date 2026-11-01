import pandas as pd

from .data import TASKS


def compare_answer(answer, key):
    """
    Упрощённая проверка: точное совпадение после удаления внешних
    пробелов и приведения к нижнему регистру.
    """
    normalized_answer = str(answer).strip().lower()
    normalized_key = str(key).strip().lower()

    if not normalized_answer:
        return 0, True

    return int(normalized_answer == normalized_key), False


def build_results(works, key_map):
    """Создаёт таблицу, в которой одна строка соответствует одному ответу."""
    records = []

    for row_index, work in works.iterrows():
        variant = work["Вариант"]
        if variant not in key_map:
            raise ValueError(
                f"Не найден ключ для варианта «{variant}» "
                f"(строка Excel {row_index + 2})."
            )

        for number in TASKS:
            answer = work[str(number)]
            key = key_map[variant][number - 1]
            point, blank = compare_answer(answer, key)

            name_parts = [
                work.get("Фамилия", ""),
                work.get("Имя", ""),
                work.get("Отчество", ""),
            ]
            fio = " ".join(part for part in name_parts if part).strip()

            records.append({
                "Строка": row_index + 2,
                "Класс": work.get("Класс", ""),
                "Литера": work.get("Литера", ""),
                "ФИО": fio,
                "Вариант": variant,
                "№ задания": number,
                "Ответ": answer,
                "Ключ": key,
                "Балл": point,
                "Пропуск": blank,
            })

    return pd.DataFrame(records)


def task_statistics(results):
    """Статистика выполнения заданий по всей выбранной выборке."""
    stats = results.groupby("№ задания").agg(
        Работ=("Балл", "size"),
        Правильных=("Балл", "sum"),
        Пропусков=("Пропуск", "sum"),
    ).reset_index()

    stats["Неправильных"] = (
        stats["Работ"] - stats["Правильных"] - stats["Пропусков"]
    )
    stats["Успешность, %"] = (
        100 * stats["Правильных"] / stats["Работ"]
    ).round(1)

    return stats


def overall_statistics(results, works):
    """Общие показатели по загруженным ученическим работам."""
    total_answers = len(results)
    correct = int(results["Балл"].sum())
    blanks = int(results["Пропуск"].sum())
    wrong = total_answers - correct - blanks

    return {
        "Работ": len(works),
        "Проверено ответов": total_answers,
        "Правильных": correct,
        "Неправильных": wrong,
        "Пропусков": blanks,
        "Успешность, %": round(
            100 * correct / total_answers, 1
        ) if total_answers else 0,
    }


def student_statistics(results):
    """Сводная таблица баллов и пропусков по каждой работе."""
    if results.empty:
        return pd.DataFrame()

    return (
        results.groupby(
            ["Строка", "Класс", "Литера", "ФИО", "Вариант"],
            dropna=False,
        )
        .agg(
            Баллы=("Балл", "sum"),
            Пропуски=("Пропуск", "sum"),
        )
        .reset_index()
        .sort_values(["Класс", "Литера", "ФИО"])
    )
