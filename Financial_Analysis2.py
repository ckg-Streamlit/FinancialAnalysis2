from openai import OpenAI
import streamlit as st
import yfinance as yf

client=OpenAI(api_key=st.secrets["OPEN_API_KEY"])
content_system="You are a financial assistant that will retrieve two tables of financial market data and will summarize the comparative performance in text, in full detail with highlights for each stock and also a conclusion with a markdown output. BE VERY STRICT ON YOUR OUTPUT"


def get_stock_data(ticker, start_date='2024-01-01', end_date='2024-02-01'):
    stock_data=yf.download(ticker, start=start_date, end=end_date)
    return stock_data

st.title('Interactive Financial Stock Market Comperative Analysis Tool')

st.sidebar.header('User Input Options')
selected_stock1=st.sidebar.text_input('Enter Stock Ticker 1', 'AAPL').upper()
selected_stock2=st.sidebar._text_input('Enter Stock Ticker 2', 'GOOG').upper()

stock_data1=get_stock_data(selected_stock1)
stock_data2=get_stock_data(selected_stock2)

col1, col2 =st.columns(2)

with col1:
    st.subheader(f"Displaying data for: {selected_stock1}")
    st.write(stock_data1)
    chart_type1=st.sidebar.selectbox(f'Select Chart Type for {selected_stock1}', ['Line', 'Bar'])
    if chart_type1=="Line":
        st.line_chart(stock_data1["Close"])
    elif chart_type1=="Bar":
        st.bar_chart(stock_data1["Close"])

with col2:
    st.subheader(f"Displaying data for: {selected_stock2}")
    st.write(stock_data2)
    chart_type2=st.sidebar.selectbox(f'Select Chart Type for {selected_stock2}', ['Line', 'Bar'])
    if chart_type2=="Line":
        st.line_chart(stock_data2["Close"])
    elif chart_type1=="Bar":
        st.bar_chart(stock_data2["Close"])

if st.button('Comparative Performance'):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a financial assistant that will retrieve two tables of financial market data and will summarize the comparative performance in text, in full detail with highlights for each stock and also a conclusion with a markdown output. BE VERY STRICT ON YOUR OUTPUT"},
                {"role": "user", "content": f"This is the {selected_stock1} stock data : {stock_data1}, this is {selected_stock2} stock data: {stock_data2}"}
            ]
        )
    st.write(response.choices[0].message.content)

