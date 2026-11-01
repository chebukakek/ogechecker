from pathlib import Path
import streamlit as st

from core.data import load_exam
from core.analysis import build_results, task_statistics, overall_statistics
from ui.dashboard import render_dashboard

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "шаблон.xlsx"

st.set_page_config(
    page_title="Анализ пробного ОГЭ",
    page_icon="📊",
    layout="wide",
)

st.title("Анализ результатов пробного ОГЭ по информатике")
st.write(
    "Учебное приложение для проверки ответов и анализа успешности выполнения заданий."
)

# Скачать готовый шаблон можно сразу с главной страницы.
if TEMPLATE_PATH.exists():
    st.download_button(
        label="Скачать шаблон.xlsx",
        data=TEMPLATE_PATH.read_bytes(),
        file_name="шаблон.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Шаблон содержит листы «Работы» и «Ключи»."
    )
else:
    st.error("Файл шаблона.xlsx не найден. Помести его рядом с app.py.")

with st.expander("Требования к Excel-файлу", expanded=True):
    st.markdown(
        """
        В книге должны быть два листа:

        **Лист «Работы»**
        - `Класс`
        - `Литера`
        - `Фамилия`
        - `Имя`
        - `Отчество`
        - `Вариант`
        - задания `1`–`10`

        **Лист «Ключи»**
        - `Вариант`
        - задания `1`–`10`

        Дополнительные столбцы «Литера» и «Отчество» допускаются.
        Номер варианта в листе «Работы» должен присутствовать на листе «Ключи».
        """
    )

uploaded = st.file_uploader("Загрузи заполненную ведомость", type=["xlsx"])

if uploaded is not None:
    try:
        works, keys = load_exam(uploaded)
        results = build_results(works, keys)
        task_stats = task_statistics(results)
        total_stats = overall_statistics(results, works)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    st.success(
        f"Файл обработан. Ученических записей: {len(works)}; "
        f"проверено ответов: {len(results)}."
    )
    render_dashboard(works, results, task_stats, total_stats)
