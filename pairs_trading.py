import plotguy
import yfinance as yf

import numpy as np
import statsmodels.api as sm

import datetime

import itertools
import multiprocessing as mp

import random

import warnings
warnings.filterwarnings(
    "ignore",
    message=r".*Converting to PeriodArray/Index representation will drop timezone information.*",
    category=UserWarning,
)

from futu import *
import requests

py_filename = os.path.basename(__file__).replace('.py', '')

data_folder = 'data'
backtest_output_folder = 'backtest_output'
secondary_data_folder = 'secondary_data'

if not os.path.isdir(data_folder): os.mkdir(data_folder)
if not os.path.isdir(backtest_output_folder): os.mkdir(backtest_output_folder)
if not os.path.isdir(secondary_data_folder): os.mkdir(secondary_data_folder)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1024)

def get_hist_data(code_list, market, start_date, end_date, freq):
    start_date_int = int(start_date.replace('-', ''))
    end_date_int = int(end_date.replace('-', ''))

    df_dict = {}

    for code in code_list:

        file_path = os.path.join(data_folder, code + '_' + freq + '.parquet')

        if not os.path.isfile(file_path) or update_data:

            if market == 'HK':
                my_ticker = yf.Ticker(code)
                df = my_ticker.history(start=start_date, end=end_date)
                time.sleep(1)

                df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                df = df[df['Volume'] > 0]
                df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
                df.to_parquet(file_path)
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' successfully get data from data source',
                      code)

            elif market == 'US':
                my_ticker = yf.Ticker(code)
                df = my_ticker.history(start=start_date, end=end_date)
                time.sleep(1)

                df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                df = df[df['Volume'] > 0]
                df = df.rename(
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
                df.to_parquet(file_path)
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' successfully get data from data source',
                      code)
        else:
            ### read data from hdd ###
            df = pd.read_parquet(file_path)

            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' successfully read data', code)

        df_dict[code] = df

    return df_dict

def benchmark_get_hist_data(benchmark_code_list, benchmark_market, start_date, end_date, benchmark_freq):
    start_date_int = int(start_date.replace('-', ''))
    end_date_int = int(end_date.replace('-', ''))

    benchmark_df_dict = {}

    for benchmark_code in benchmark_code_list:

        file_path = os.path.join(data_folder, benchmark_code + '_' + freq + '.parquet')

        if not os.path.isfile(file_path) or update_data:
            ### harddisk no file, get data from server ###

            if benchmark_market == 'HK':
                my_ticker = yf.Ticker(benchmark_code)
                benchmark_df = my_ticker.history(start=start_date, end=end_date)
                time.sleep(1)

                benchmark_df = benchmark_df[['Open', 'High', 'Low', 'Close', 'Volume']]
                benchmark_df = benchmark_df[benchmark_df['Volume'] > 0]
                benchmark_df = benchmark_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
                benchmark_df.to_parquet(file_path)
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' successfully get data from data source',
                      benchmark_code)

            elif benchmark_market == 'US':
                my_ticker = yf.Ticker(benchmark_code)
                benchmark_df = my_ticker.history(start=start_date, end=end_date)
                time.sleep(1)

                benchmark_df = benchmark_df[['Open', 'High', 'Low', 'Close', 'Volume']]
                benchmark_df = benchmark_df[benchmark_df['Volume'] > 0]
                benchmark_df = benchmark_df.rename(
                    columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
                benchmark_df.to_parquet(file_path)
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' successfully get data from data source',
                      benchmark_code)
        else:
            ### read data from hdd ###
            benchmark_df = pd.read_parquet(file_path)

            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' successfully read data', benchmark_code)


        benchmark_df_dict[benchmark_code] = benchmark_df

    return benchmark_df_dict


def get_hk_lot_size(code_list):
    lot_size_dict = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    for code in code_list:
        clean_code = code.split('.')[0].zfill(5)
        url = f"http://qt.gtimg.cn/q=r_hk{clean_code}"
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200 and '~' in resp.text:
                parts = resp.text.split('~')
                # 騰訊數據第 46 欄為每手股數
                lot_size = int(parts[46]) if len(parts) > 46 and parts[46].isdigit() else 100
                lot_size_dict[code] = lot_size
            else:
                lot_size_dict[code] = 100
        except Exception:
            lot_size_dict[code] = 100
    return lot_size_dict


def get_sec_profile(code_list, market, sectype, initial_capital, start_date, end_date):
    sec_profile = {}
    lot_size_dict = {}

    if market == 'HK':
        if sectype == 'STK':
            lot_size_dict = get_hk_lot_size(code_list)
    elif market == 'US':
        if sectype == 'STK':
            for code in code_list:
                lot_size_dict[code] = 1

    sec_profile['lot_size_dict'] = lot_size_dict
    sec_profile['market'] = market
    sec_profile['sectype'] = sectype
    sec_profile['initial_capital'] = initial_capital

    if sectype == 'STK':
        if market in ['HK', 'US']:
            sec_profile['commission_rate'] = 0.03 * 0.01
            sec_profile['min_commission'] = 3
            sec_profile['platform_fee'] = 15

    return sec_profile


def get_all_para_combination(
        para_dict, df_dict,benchmark_df_dict, sec_profile,
        freq, start_date, end_date,
        data_folder, backtest_output_folder,
        py_filename, run_mode,
        summary_mode, file_format
):
    intraday = False if freq == '1D' else True

    keys, values = zip(*para_dict.items())
    all_para_combination = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

    print('number of para_combination', len(all_para_combination))

    output_folder = backtest_output_folder

    for reference_index, para_combination in enumerate(all_para_combination):
        code = para_combination['code']
        df = df_dict[code]
        combined_dict = {**df_dict, **benchmark_df_dict}
        
        merged_df = pd.concat(combined_dict, axis=1)
        merged_df = merged_df.dropna().copy()
        merged_df.columns = [f"{c[0]}_{c[1]}" for c in merged_df.columns]

        merged_df['open']   = merged_df[f"{code}_open"]
        merged_df['high']   = merged_df[f"{code}_high"]
        merged_df['low']    = merged_df[f"{code}_low"]
        merged_df['close']  = merged_df[f"{code}_close"]
        merged_df['volume'] = merged_df[f"{code}_volume"]

        para_combination['start_date']      = start_date
        para_combination['end_date']        = end_date

        para_combination['data_folder']     = data_folder
        para_combination['output_folder']   = output_folder
        para_combination['sec_profile']     = sec_profile
        para_combination['freq']            = freq
        para_combination['para_dict']       = para_dict
        para_combination['df']              = merged_df

        para_combination['py_filename']     = py_filename
        para_combination['run_mode']        = run_mode
        para_combination['summary_mode']    = summary_mode
        para_combination['file_format']     =  file_format

        para_combination['intraday']        = intraday
        para_combination['reference_index'] = reference_index

    return all_para_combination


def backtest(para_combination):
    # Use a copy so parameter iterations don't mutate the shared DataFrame
    df = para_combination['df'].copy()

    start_date      = para_combination['start_date']
    end_date        = para_combination['end_date']
    data_folder     = para_combination['data_folder']
    output_folder   = para_combination['output_folder']
    sec_profile     = para_combination['sec_profile']
    freq            = para_combination['freq']
    para_dict       = para_combination['para_dict']
    py_filename     = para_combination['py_filename']
    run_mode        = para_combination['run_mode']
    summary_mode    = para_combination['summary_mode']
    file_format     = para_combination['file_format']
    intraday        = para_combination['intraday']
    reference_index = para_combination['reference_index']

    ################# strategy specific #################
    code            = para_combination['code']
    benchmark_code  = para_combination['benchmark_code']
    long_short      = para_combination['long_short']
    entry_threshold      = para_combination['entry_threshold']
    exit_threshold       = para_combination['exit_threshold']
    rolling_window       = para_combination['rolling_window']
    stop_loss_threshold  = para_combination['stop_loss_threshold']
    hedge_ratio_window   = para_combination['hedge_ratio_window']

    ###################### sec_profile ####################
    market = sec_profile['market']
    sectype = sec_profile['sectype']
    initial_capital = sec_profile['initial_capital']
    lot_size_dict = sec_profile['lot_size_dict']
    lot_size = lot_size_dict[code]

    if sectype == 'STK':
        commission_rate = sec_profile['commission_rate']
        min_commission = sec_profile['min_commission']
        platform_fee = sec_profile['platform_fee']

    ################# Strategy Logic #################
    # Rolling OLS: log(close) = α + β·log(benchmark_close)
    log_close = np.log(df[f'{code}_close'])
    log_bench = np.log(df[f'{benchmark_code}_close'])

    rolling_hr = pd.Series(np.nan, index=df.index)
    for j in range(hedge_ratio_window, len(df)):
        y = log_close.iloc[j - hedge_ratio_window:j]
        X = sm.add_constant(log_bench.iloc[j - hedge_ratio_window:j])
        try:
            model = sm.OLS(y, X).fit()
            rolling_hr.iloc[j] = model.params.iloc[1]
        except Exception:
            pass

    df['hedge_ratio'] = rolling_hr.ffill()
    para_combination['hedge_ratio'] = df['hedge_ratio'].mean()

    # Log-price spread and Z-score
    df['spread'] = log_close - df['hedge_ratio'] * log_bench
    df['spread_mean'] = df['spread'].rolling(rolling_window).mean().shift(1)
    df['spread_std']  = df['spread'].rolling(rolling_window).std().shift(1)
    df['z_score']     = (df['spread'] - df['spread_mean']) / df['spread_std']

    # Entry/Exit booleans (.fillna(False) prevents truth-value ambiguity during warmup)
    if long_short == 'long':
        df['trade_logic'] = (df['z_score'].shift(1) < -entry_threshold).fillna(False)
    elif long_short == 'short':
        df['trade_logic'] = (df['z_score'].shift(1) > entry_threshold).fillna(False)

    df['close_logic'] = (df['z_score'].abs() <= exit_threshold).fillna(False)
    df['stop_loss']   = (df['z_score'].abs() > stop_loss_threshold).fillna(False)

    ####### initialization #######
    df['action'] = ''
    df['num_of_share'] = 0
    df['open_price'] = np.nan
    df['close_price'] = np.nan
    df['realized_pnl'] = np.nan
    df['unrealized_pnl'] = 0.0
    df['net_profit'] = 0.0
    df['equity_value'] = float(initial_capital)
    df['mdd_dollar'] = 0.0
    df['mdd_pct'] = 0.0
    df['commission'] = 0.0
    df['logic'] = None

    open_date = datetime.now().date()
    open_price = 0.0
    net_profit = 0.0
    num_of_share = 0
    num_of_trade = 0
    equity_value = float(initial_capital)
    realized_pnl = 0.0
    unrealized_pnl = 0.0
    commission = 0.0
    last_realized_capital = float(initial_capital)

    for i, row in df.iterrows():
        now_date  = i.date()
        now_open  = row['open']
        now_high  = row['high']
        now_low   = row['low']
        now_close = row['close']

        trade_logic     = bool(row['trade_logic'])
        close_logic     = bool(row['close_logic'])
        stop_loss_cond  = bool(row['stop_loss'])
        last_index_cond = (df.index[-1] == i)

        if trade_logic:
            df.at[i, 'logic'] = 'trade_logic'

        ########## commission ##########
        if sectype == 'STK':
            if num_of_share > 0:
                commission = num_of_share * now_close * commission_rate
                if commission < min_commission:
                    commission = min_commission
                commission += platform_fee
                commission *= 2
            else:
                commission = 0.0

        ###### equity value #########
        if long_short == 'long':
            unrealized_pnl = num_of_share * (now_close - open_price)
        elif long_short == 'short':
            unrealized_pnl = num_of_share * (open_price - now_close)

        equity_value = last_realized_capital + unrealized_pnl
        net_profit = equity_value - initial_capital

        if (num_of_share == 0) and trade_logic:
            num_of_lot = int(last_realized_capital // (lot_size * now_close))
            num_of_share = num_of_lot * lot_size
            if num_of_share > 0:
                open_price = now_close
                open_date  = now_date
                df.at[i, 'action'] = 'open'
                df.at[i, 'open_price'] = open_price

        elif (num_of_share > 0) and (close_logic or stop_loss_cond or last_index_cond):
            realized_pnl = unrealized_pnl - commission
            unrealized_pnl = 0.0
            last_realized_capital += realized_pnl
            num_of_share = 0
            num_of_trade += 1

            if close_logic:
                df.at[i, 'action'] = 'close_logic'
            elif stop_loss_cond:
                df.at[i, 'action'] = 'stop_loss'
            elif last_index_cond:
                df.at[i, 'action'] = 'last_index'

            df.at[i, 'close_price']  = now_close
            df.at[i, 'realized_pnl'] = realized_pnl
            df.at[i, 'commission']   = commission

        ####### record every row #######
        df.at[i, 'equity_value']   = float(equity_value)
        df.at[i, 'num_of_share']   = num_of_share
        df.at[i, 'unrealized_pnl'] = float(unrealized_pnl)
        df.at[i, 'net_profit']     = float(net_profit)

    if summary_mode:
        df = df[df['action'] != '']

    save_path = plotguy.generate_filepath(para_combination)
    print(save_path)

    # Ensure 'date' column exists for plotguy
    if 'date' not in df.columns:
        df = df.reset_index().rename(columns={'Date': 'date', 'index': 'date'})

    df.to_parquet(save_path)


if __name__ == '__main__':

    start_date         = '2024-01-01'
    end_date           = '2026-01-01'

    ### The stock you buy ###
    market             = 'HK' # HK or US
    freq               = '1D' # Daily

    ### Only for the pair ###
    benchmark_market   = 'HK'
    benchmark_freq     = '1D'

    sectype            = 'STK'
    initial_capital    = 100000
    run_mode           = 'backtest'
    summary_mode       = False
    file_format        = 'parquet'

    mp_mode            = True
    read_only          = False
    update_data        = True

    num_of_core        = 16

    # code_list           = ['0939.HK']
    # benchmark_code_list = ['1398.HK']
    code_list           = ['PEP']
    benchmark_code_list = ['KO']

    para_dict = {
        'code'                : code_list,
        'benchmark_code'      : benchmark_code_list,
        'entry_threshold'     : [0.5, 1, 1.5, 2, 2.5],
        'exit_threshold'      : [0.5, 1, 1.5, 2, 2.5],
        'stop_loss_threshold' : [3,5,7,9],
        'hedge_ratio_window'  : [126, 252, 504],
        'long_short'          : ['long', 'short'],
        'rolling_window'      : [15, 30, 60, 90, 150, 250],
    }



    df_dict = get_hist_data(code_list, market,start_date, end_date,freq)
    benchmark_df_dict = benchmark_get_hist_data(benchmark_code_list, benchmark_market,start_date, end_date,freq)

    sec_profile = get_sec_profile(code_list, market,sectype, initial_capital,start_date, end_date)
    all_para_combination = get_all_para_combination(
        para_dict, df_dict,benchmark_df_dict, sec_profile,
        freq, start_date, end_date,
        data_folder, backtest_output_folder,
        py_filename, run_mode,
        summary_mode, file_format)

    t1 = datetime.now()

    if not read_only:
        if mp_mode:
            pool = mp.Pool(processes=num_of_core)
            pool.map(backtest, all_para_combination)
            pool.close()
        else:
            for para_combination in all_para_combination:
                backtest(para_combination)

    t2 = datetime.now()

    print(((t2 - t1) / 60).seconds, 'mins')

    plotguy.generate_backtest_result(
        all_para_combination=all_para_combination,
        number_of_core=num_of_core
    )

    app = plotguy.plot(mode='equity_curves',
                       all_para_combination=all_para_combination,
                       number_of_curves=30)

    app.run_server(port=random.randint(8000, 9999))
