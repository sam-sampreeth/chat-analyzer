import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
from collections import Counter, defaultdict
import os
import tempfile
import re
import emoji
from utils.pdf_report import save_plot_as_image, generate_pdf_report
import copy

def extract_emojis(text_list):
    all_emojis = []
    for text in text_list:
        all_emojis += [ch for ch in text if ch in emoji.EMOJI_DATA]
    return all_emojis

def show_visuals(df):
    plots = []

    with tempfile.TemporaryDirectory() as tmpdir:
        # 🔹 Most Active Months by User (Stacked)
        st.subheader("📅 Most Active Months by User")
        df['month'] = df['datetime'].dt.to_period('M').astype(str)
        monthly_user_df = df.groupby(['month', 'sender']).size().unstack(fill_value=0).sort_index()

        fig1 = px.bar(
            monthly_user_df,
            title="Most Active Months by User",
            labels={"value": "Message Count", "month": "Month"},
        )
        fig1.update_layout(barmode='stack')
        st.plotly_chart(fig1)

        with st.expander("🔍 View Monthly Message Breakdown by User"):
            st.dataframe(monthly_user_df)

        fig1_pdf = copy.deepcopy(fig1)
        fig1_pdf.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="black")
        p1 = os.path.join(tmpdir, "month_stacked.png")
        fig1_pdf.write_image(p1)
        plots.append(("Most Active Months by User", p1))

        # 🔹 Most Active Hours by User (Stacked)
        st.subheader("⏰ Most Active Hours by User")
        df["hour"] = df["datetime"].dt.hour
        hourly_user_df = df.groupby(['hour', 'sender']).size().unstack(fill_value=0).sort_index()

        fig2 = px.bar(
            hourly_user_df,
            title="Most Active Hours by User",
            labels={"value": "Message Count", "hour": "Hour (0–23)"},
        )
        fig2.update_layout(barmode='stack')
        st.plotly_chart(fig2)

        with st.expander("🔍 View Hourly Breakdown by User"):
            st.dataframe(hourly_user_df)

        fig2_pdf = copy.deepcopy(fig2)
        fig2_pdf.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="black")
        p2 = os.path.join(tmpdir, "hour_stacked.png")
        fig2_pdf.write_image(p2)
        plots.append(("Most Active Hours by User", p2))

        # 🔹 Most Active Users
        st.subheader("👥 Most Active Users")
        user_freq = df['sender'].value_counts()
        fig3 = px.bar(
            x=user_freq.index,
            y=user_freq.values,
            labels={"x": "User", "y": "Messages"},
            title="Most Active Users",
        )
        st.plotly_chart(fig3)

        with st.expander("🔍 View User Data"):
            for user, count in user_freq.items():
                st.markdown(f"**{user}**: {count} messages")

        fig3_pdf = copy.deepcopy(fig3)
        fig3_pdf.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="black")
        p3 = os.path.join(tmpdir, "user_freq.png")
        fig3_pdf.write_image(p3)
        plots.append(("Most Active Users", p3))

        # 🔹 Top Emojis
        st.subheader("😂 Top Emojis")
        emojis = extract_emojis(df["content"].tolist())
        emoji_freq = Counter(emojis).most_common(10)

        if not emoji_freq:
            st.info("No emojis found in chat.")
        else:
            cols = st.columns(5)
            for i, (emoji_char, count) in enumerate(emoji_freq[:5]):
                with cols[i]:
                    st.markdown(f"<div style='font-size:40px'>{emoji_char}</div>", unsafe_allow_html=True)
                    st.markdown(f"`{count}` times")
            with st.expander("🔍 View All Emoji Data"):
                for i, (emoji_char, count) in enumerate(emoji_freq, 1):
                    st.markdown(f"**#{i}** {emoji_char} — {count} times")

        # 🔹 Word Cloud
        st.subheader("☁️ Word Cloud")
        all_text = " ".join(df["content"].tolist()).lower()
        unwanted_phrases = ["media omitted", "omitted media"]
        for phrase in unwanted_phrases:
            all_text = all_text.replace(phrase, "")
        custom_stopwords = STOPWORDS.union(set(unwanted_phrases))
        wc = WordCloud(stopwords=custom_stopwords, width=800, height=400, background_color="white").generate(all_text)

        fig4 = wc.to_image()
        wc_path = os.path.join(tmpdir, "wordcloud.png")
        fig4.save(wc_path)
        st.image(fig4)
        plots.append(("Word Cloud", wc_path))

        words = re.findall(r'\b\w+\b', all_text)
        word_freq = defaultdict(int)
        for word in words:
            if word not in custom_stopwords:
                word_freq[word] += 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        with st.expander("🔍 Top 10 Words in Word Cloud"):
            for i, (word, count) in enumerate(top_words, 1):
                st.markdown(f"**#{i}** `{word}` — {count} times")

        # 🔹 PDF Report
        most_active_month = monthly_user_df.sum(axis=1).idxmax() if not monthly_user_df.empty else "N/A"
        most_active_user = df['sender'].value_counts().idxmax() if not df.empty else "N/A"
        stats_text = f"""
Total Messages: {len(df)}
Users Involved: {df['sender'].nunique()}
Most Active User: {most_active_user}
Most Active Month: {most_active_month}
"""

        pdf_path = os.path.join(tmpdir, "report.pdf")
        generate_pdf_report(plots, stats_text, output_path=pdf_path)

        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF Report", f, file_name="chat_report.pdf", mime="application/pdf")
