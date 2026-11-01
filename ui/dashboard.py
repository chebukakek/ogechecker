import pandas as pd
import plotly.express as px
import streamlit as st

from core.analysis import student_statistics


def render_dashboard(works, results, task_stats, total_stats):
    """Отображает сводные показатели, аналитику заданий и таблицы."""

    st.subheader("Общие результаты")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ученических работ", total_stats["Работ"])
    c2.metric("Правильных ответов", total_stats["Правильных"])
    c3.metric("Успешность", f'{total_stats["Успешность, %"]}%')
    c4.metric("Пропусков", total_stats["Пропусков"])

    st.subheader("Успешность выполнения заданий")
    chart = px.bar(
        task_stats,
        x="№ задания",
        y="Успешность, %",
        range_y=[0, 100],
        text="Успешность, %",
        labels={
            "№ задания": "Номер задания",
            "Успешность, %": "Правильных ответов, %",
        },
        hover_data=["Работ", "Правильных", "Неправильных", "Пропусков"],
    )
    chart.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
    )
    chart.update_layout(
        xaxis_title="Номер задания",
        yaxis_title="Правильных ответов, %",
    )
    st.plotly_chart(chart, use_container_width=True)

    st.subheader("Статистика по заданиям")
    st.dataframe(task_stats, hide_index=True, use_container_width=True)

    st.subheader("Задания с наименьшей успешностью")
    hardest = task_stats.sort_values(
        ["Успешность, %", "№ задания"],
        ascending=[True, True],
    ).head(3)
    st.dataframe(
        hardest[
            ["№ задания", "Успешность, %", "Неправильных", "Пропусков"]
        ],
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Результаты ученических работ")
    students = student_statistics(results)
    st.dataframe(students, hide_index=True, use_container_width=True)

    st.subheader("Ответы, требующие внимания")
    wrong_or_blank = results[
        (results["Балл"] == 0)
    ][
        ["Класс", "ФИО", "Вариант", "№ задания", "Ответ", "Ключ", "Пропуск"]
    ]
    st.dataframe(wrong_or_blank, hide_index=True, use_container_width=True)

    st.download_button(
        "Скачать статистику по заданиям (CSV)",
        data=task_stats.to_csv(
            index=False, sep=";", encoding="utf-8-sig"
        ).encode("utf-8-sig"),
        file_name="статистика_по_заданиям.csv",
        mime="text/csv",
    )

    st.download_button(
        "Скачать результаты по ученикам (CSV)",
        data=students.to_csv(
            index=False, sep=";", encoding="utf-8-sig"
        ).encode("utf-8-sig"),
        file_name="результаты_учеников.csv",
        mime="text/csv",
    )

    with st.expander("Методика и ограничения автоматической проверки"):
        st.markdown(
            """
            - Программа начисляет 1 балл за точное совпадение ответа с ключом.
            - Регистр букв и внешние пробелы не учитываются.
            - Пустой ответ учитывается отдельно как пропуск.
            - Допустимые альтернативные формы ответа необходимо заранее учесть
              в алгоритме или проверить вручную.
            - Низкая успешность в конкретной выборке указывает на затруднение
              этой группы, но не доказывает объективную сложность задания.
            - Для исследования используйте обезличенные данные.
            """
        )
