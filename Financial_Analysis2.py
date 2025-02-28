from openai import OpenAI
import streamlit as st
import yfinance as yf
import pandas_ta as ta
import datetime as datetime
import plotly.graph_objs as go

#a dummy OPEN_API_KEY is set to secrets 
client=OpenAI(api_key=st.secrets["OPEN_API_KEY"])
content_system="You are a financial assistant that will retrieve two tables of financial market data and will summarize the comparative performance in text, in full detail with highlights for each stock and also a conclusion with a markdown output. BE VERY STRICT ON YOUR OUTPUT"


def get_stock_data(ticker, start_date='2024-01-01', end_date='2024-02-01'):
    stock_data=yf.download(ticker, start=start_date, end=end_date)
    return stock_data

st.title('Interactive Financial Stock Market Comperative Analysis Tool')

st.sidebar.header('User Input Options')
selected_stock1=st.sidebar.text_input('Enter Stock Ticker 1', 'AAPL').upper()
selected_stock2=st.sidebar.text_input('Enter Stock Ticker 2', 'GOOG').upper()
#Added date selection
selected_start=st.sidebar.date_input('Enter the start date', datetime.date(2024, 1, 1))
selected_end=st.sidebar.date_input('Enter the end date', datetime.date(2024, 2, 1))


stock_data1=get_stock_data(selected_stock1, selected_start, selected_end)
stock_data2=get_stock_data(selected_stock2, selected_start, selected_end)

#added some technical indicators
stock_data1["sma5"]=ta.sma(stock_data1["Close"], length=5)
stock_data2["sma5"]=ta.sma(stock_data2["Close"], length=5)
stock_data1["sma10"]=ta.sma(stock_data1["Close"], length=10)
stock_data2["sma10"]=ta.sma(stock_data2["Close"], length=10)

#added a candlestick diagram
candlestick1 = go.Candlestick(x=stock_data1.index,
                                 open=stock_data1["Open"],
                                 high=stock_data1["High"],
                                 low=stock_data1["Low"],
                                 close=stock_data1["Close"])
                            

candlestick2 = go.Candlestick(x=stock_data2.index,
                                 open=stock_data1["Open"],
                                 high=stock_data1["High"],
                                 low=stock_data1["Low"],
                                 close=stock_data1["Close"])
                            
fig1=go.Figure()
fig1.add_trace((candlestick1))
fig2=go.Figure()
fig2.add_trace((candlestick2))

#added  a signal functionality for buy or sell stocks
buy=1
sell=1

def trade(row):
    #Buy on Green HA candle when close price crosses sma5
    global buy
    global sell
    if (row['Close'] - row['sma5']) >= 0.01 and row['Close'] > row['Open'] and buy==1 :
       buy=0
       sell=1
       return "BUY AT {}".format(row['Close']) 
       
       
    # Sell on Red HA candle when close price crosses sma5
    if (row['Close'] - row['sma5']) <= -0.01 and  row['Close'] < row['Open'] and sell==1:
       sell=0
       buy=1
       return "SELL AT {}".format(row['Close'])
    


stock_data1['Signal'] = stock_data1.apply(trade, axis=1)
stock_data2['Signal'] = stock_data2.apply(trade, axis=1)

col1, col2 =st.columns(2)

with col1:
    st.subheader(f"Displaying data for: {selected_stock1}")
    st.write(stock_data1)
    st.plotly_chart(fig1)
    chart_type1=st.sidebar.selectbox(f'Select Chart Type for {selected_stock1}', ['Line', 'Bar', "Tech"])
    if chart_type1=="Line":
        st.line_chart(stock_data1["Close"])
    elif chart_type1=="Bar":
        st.bar_chart(stock_data1["Close"])
    elif chart_type1=="Tech":
        st.line_chart(stock_data1[["Close","sma5","sma10"]])

with col2:
    st.subheader(f"Displaying data for: {selected_stock2}")
    st.write(stock_data2)
    st.plotly_chart(fig2)
    chart_type2=st.sidebar.selectbox(f'Select Chart Type for {selected_stock2}', ['Line', 'Bar',"Tech"])
    if chart_type2=="Line":
        st.line_chart(stock_data2["Close"])
    elif chart_type2=="Bar":
        st.bar_chart(stock_data2["Close"])
    elif chart_type2=="Tech":
        st.line_chart(stock_data2[["Close","sma5","sma10"]])

if st.button('Comparative Performance'):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a financial assistant that will retrieve two tables of financial market data and will summarize the comparative performance in text, in full detail with highlights for each stock and also a conclusion with a markdown output. BE VERY STRICT ON YOUR OUTPUT"},
                {"role": "user", "content": f"This is the {selected_stock1} stock data : {stock_data1}, this is {selected_stock2} stock data: {stock_data2}"}
            ]
        )
    st.write(response.choices[0].message.content)

