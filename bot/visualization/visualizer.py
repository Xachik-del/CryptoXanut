import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from datetime import datetime
import os

def plot_chart(df, symbol, timeframe, indicators=True):
    """
    Создает график свечей с индикаторами
    
    Args:
        df (pd.DataFrame): DataFrame с данными
        symbol (str): Торговая пара
        timeframe (str): Таймфрейм
        indicators (bool): Показывать ли индикаторы
    """
    # Создаем директорию для графиков если её нет
    if not os.path.exists('charts'):
        os.makedirs('charts')
    
    # Подготовка данных для mplfinance
    df_plot = df.copy()
    df_plot.index = pd.to_datetime(df_plot.index)
    
    # Настройка стиля
    mc = mpf.make_marketcolors(up='g', down='r',
                              edge='inherit',
                              wick='inherit',
                              volume='in')
    s = mpf.make_mpf_style(marketcolors=mc)
    
    # Создание дополнительных графиков для индикаторов
    add_plots = []
    
    if indicators:
        # EMA
        add_plots.append(mpf.make_addplot(df_plot['ema8'], color='blue', width=0.7, panel=0))
        add_plots.append(mpf.make_addplot(df_plot['ema13'], color='orange', width=0.7, panel=0))
        add_plots.append(mpf.make_addplot(df_plot['ema21'], color='purple', width=0.7, panel=0))
        
        # Bollinger Bands
        add_plots.append(mpf.make_addplot(df_plot['bb_upper'], color='gray', width=0.7, panel=0))
        add_plots.append(mpf.make_addplot(df_plot['bb_lower'], color='gray', width=0.7, panel=0))
        
        # RSI
        add_plots.append(mpf.make_addplot(df_plot['rsi'], color='purple', width=0.7, panel=1))
        
        # MACD
        add_plots.append(mpf.make_addplot(df_plot['macd'], color='blue', width=0.7, panel=2))
        add_plots.append(mpf.make_addplot(df_plot['macd_signal'], color='red', width=0.7, panel=2))
        
        # Volume
        add_plots.append(mpf.make_addplot(df_plot['volume'], type='bar', color='gray', panel=3))
    
    # Настройка размеров панелей
    figsize = (15, 10)
    panel_ratios = (3, 1, 1, 1) if indicators else (1,)
    
    # Создание имени файла
    safe_symbol = symbol.replace("/", "_").replace(":", "_")
    filename = f'charts/{safe_symbol}_{timeframe}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'


    
    # Создание графика
    fig, axes = mpf.plot(df_plot,
                        type='candle',
                        style=s,
                        title=f'\n{symbol} - {timeframe}',
                        ylabel='Цена',
                        volume=True,
                        addplot=add_plots if indicators else None,
                        figsize=figsize,
                        panel_ratios=panel_ratios,
                        returnfig=True)
    
    # Сохранение графика
    fig.savefig(filename)
    plt.close(fig)
    
    return filename

def plot_signal(df, symbol, timeframe, signal_type, entry_price, stop_loss, take_profit):
    """
    Создает график с отметкой сигнала
    
    Args:
        df (pd.DataFrame): DataFrame с данными
        symbol (str): Торговая пара
        timeframe (str): Таймфрейм
        signal_type (str): Тип сигнала ('ПОКУПКА' или 'ПРОДАЖА')
        entry_price (float): Цена входа
        stop_loss (float): Уровень стоп-лосса
        take_profit (float): Уровень тейк-профита
    """
    # Создаем директорию для графиков если её нет
    if not os.path.exists('charts'):
        os.makedirs('charts')
    
    # Подготовка данных
    df_plot = df.copy()
    df_plot.index = pd.to_datetime(df_plot.index)
    
    # Настройка стиля
    mc = mpf.make_marketcolors(up='g', down='r',
                              edge='inherit',
                              wick='inherit',
                              volume='in')
    s = mpf.make_mpf_style(marketcolors=mc)
    
    # Создание дополнительных графиков
    add_plots = []
    
    # Добавление уровней входа, стоп-лосса и тейк-профита
    entry_line = pd.Series(entry_price, index=df_plot.index)
    sl_line = pd.Series(stop_loss, index=df_plot.index)
    tp_line = pd.Series(take_profit, index=df_plot.index)
    
    add_plots.append(mpf.make_addplot(entry_line, color='blue', width=1, panel=0))
    add_plots.append(mpf.make_addplot(sl_line, color='red', width=1, panel=0))
    add_plots.append(mpf.make_addplot(tp_line, color='green', width=1, panel=0))
    
    # Создание имени файла
    safe_symbol = symbol.replace("/", "_").replace(":", "_")
    filename = f'charts/{safe_symbol}_{signal_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

    
    # Создание графика
    fig, axes = mpf.plot(df_plot,
                        type='candle',
                        style=s,
                        title=f'\n{symbol} - {timeframe}\n{signal_type} @ {entry_price}',
                        ylabel='Цена',
                        volume=True,
                        addplot=add_plots,
                        figsize=(15, 10),
                        returnfig=True)
    
    # Сохранение графика
    fig.savefig(filename)
    plt.close(fig)
    
    return filename 