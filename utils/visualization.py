import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
from collections import Counter, defaultdict
import os
import re
import emoji

def extract_emojis(text_list):
    all_emojis = []
    for text in text_list:
        all_emojis += [ch for ch in text if ch in emoji.EMOJI_DATA]
    return all_emojis

def show_visuals(df):
    # Use a key to persist "print" state
    if "show_analysis" not in st.session_state:
        st.session_state.show_analysis = True

    # 🔹 Most Active Months by User (Stacked)
    st.subheader("📅 Most Active Users (Monthly)")
    df['month'] = df['datetime'].dt.to_period('M').astype(str)
    monthly_user_df = df.groupby(['month', 'sender']).size().unstack(fill_value=0).sort_index()

    fig1 = px.bar(
        monthly_user_df,
        title="Most Active Months by User",
        labels={"value": "Message Count", "month": "Month"},
    )
    fig1.update_layout(barmode='stack')
    st.plotly_chart(fig1)

    with st.expander("🔍 Monthly Message Breakdown (User Wise)"):
        st.dataframe(monthly_user_df)

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

    # 🔹 Average Words Per Message (per User)
    st.subheader("📏 Average Words Per Message (Per User)")
    df["word_count"] = df["content"].apply(lambda x: len(str(x).split()))
    avg_words = df.groupby("sender")["word_count"].mean().sort_values(ascending=False)

    fig_avg = px.bar(
        x=avg_words.index,
        y=avg_words.values,
        labels={"x": "User", "y": "Avg Words"},
        title="Average Words Per Message",
    )
    st.plotly_chart(fig_avg)

    with st.expander("🔍 View Averages Per User"):
        for user, avg in avg_words.items():
            st.markdown(f"**{user}**: `{avg:.2f}` words/message")

    # 🔹 Word Cloud
    st.subheader("☁️ Word Cloud")
    all_text = " ".join(df["content"].tolist()).lower()
    unwanted_phrases = ["media omitted", "omitted media"]
    for phrase in unwanted_phrases:
        all_text = all_text.replace(phrase, "")
    custom_stopwords = STOPWORDS.union(set(unwanted_phrases))
    wc = WordCloud(stopwords=custom_stopwords, width=800, height=400, background_color="white").generate(all_text)

    st.image(wc.to_image())

    words = re.findall(r'\b\w+\b', all_text)
    word_freq = defaultdict(int)
    for word in words:
        if word not in custom_stopwords:
            word_freq[word] += 1
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    with st.expander("🔍 Top 10 Words in Word Cloud"):
        for i, (word, count) in enumerate(top_words, 1):
            st.markdown(f"**#{i}** `{word}` — {count} times")

    # 🔹 Expand & Print Button
    # st.markdown("---")
    # if st.button("🖨️ Expand All and Print"):
    #     js = """
    #     <script>
    #     const details = Array.from(document.querySelectorAll("details"));
    #     details.forEach(d => d.open = true);
    #     setTimeout(() => { window.print(); }, 500);
    #     </script>
    #     """
    #     st.components.v1.html(js, height=0)
