import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'meiryo'

# データの読み込み
DATA_PATH = 'cr7.csv'
data = pd.read_csv(DATA_PATH)
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# データ処理
data['Minute_Cleaned'] = data['Minute'].str.replace('+', '').astype(float)
data['minute_column'] = data['Minute'].apply(lambda match_time: sum(map(int, match_time.split('+'))) if '+' in match_time else int(match_time))
data['Result'] = data['Result'].apply(lambda x: 'Win' if x[0] > x[-1] else ('Draw' if x[0] == x[-1] else 'Loss'))


# # シーズン選択関数
def show_season_goals(data, selected_season):
    # ヘッダーを設定
    st.header(f'{selected_season} シーズンのゴール数')
    
    # 選択されたシーズンのゴール数を計算
    season_goals = data[data['Season'] == selected_season].shape[0]
    
    # 数値指示器でゴール数を表示
    st.metric(label="ゴール数", value=season_goals)
    st.write('''シーズン別ゴール数のグラフでは、
         CR7が各シーズンにどのようにパフォーマンスを発揮したかがわかります。
         最もゴールが多かったシーズンはどれか、
         時間の経過とともに彼のパフォーマンスがどのように変化したかを視覚的に確認できます。''')


def plot_goals_by_competition(data):
    """
    競技会ごとのゴール数を分析し、バーチャートで表示する。
    """
    st.header('競技会別ゴール数')
    # 競技会選択用のセレクトボックスを追加
    competitions = data['Competition'].unique()
    selected_competitions = st.multiselect('競技会を選択してください:', competitions, default=competitions)
    # 選択された競技会のデータにフィルターをかける
    filtered_data = data[data['Competition'].isin(selected_competitions)]
    # 競技会ごとのゴール数を集計
    goals_by_competition = filtered_data.groupby('Competition').size().sort_values(ascending=False)
    # グラフの描画
    plt.figure(figsize=(12, 6))
    goals_by_competition.plot(kind='bar', color='teal')
    plt.title('Number of Goals by Competition')
    plt.xlabel('Competition')
    plt.ylabel('Goals')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    
    # Streamlitにグラフを表示
    st.pyplot(plt)
    
    st.header('競技会別ゴール数(オプション)')
    order = st.radio("ゴール数の表示順序を選択してください:", ('降順', '昇順'))
    
    # 表示する競技会の数選択
    number_of_competitions = st.slider("表示する競技会の数を選択してください:", 1, len(data['Competition'].unique()), len(data['Competition'].unique()))
    
    # 競技会ごとのゴール数を集計し、ユーザーの選択に応じてソート
    if order == '降順':
        goals_by_competition = data.groupby('Competition').size().sort_values(ascending=False).head(number_of_competitions)
    else:
        goals_by_competition = data.groupby('Competition').size().sort_values(ascending=True).head(number_of_competitions)
    
    # グラフの描画
    plt.figure(figsize=(12, 6))
    goals_by_competition.plot(kind='bar', color='teal')
    plt.title('Goals by Competition')
    plt.xlabel('Competition')
    plt.ylabel('Number of Goals')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    
    # Streamlitにグラフを表示
    st.pyplot(plt)
    




# 'Minute'列处理，加时也考慮する
def convert_minute_to_float(minute):
    if '+' in minute:
        main_minute, extra_time = minute.split('+')
        return float(main_minute) + float(extra_time) / 60  # 加时转换为小数部分
    else:
        return float(minute)

# 应用转换函数
data['Minute_Cleaned'] = data['Minute'].apply(convert_minute_to_float)

# シーズンごとに平均ゴールタイムを計算します。
average_goal_time_by_season = data.groupby('Season')['Minute_Cleaned'].mean()

# プロット機能の追加
def plot_average_goal_time_by_season(average_goal_time_by_season):
    """
    シーズンごとの平均ゴールタイムをバーチャートで表示します。ユーザーはグラフの色を選択できます。
    """
    st.header('シーズン別平均ゴールタイム')
    
    # グラフの色を選択
    color = st.color_picker('グラフの色を選択してください:', '#563d7c')

    # 表示する最大シーズン数を選択
    max_seasons = st.slider('表示する最大シーズン数:', 1, len(average_goal_time_by_season), len(average_goal_time_by_season))
    
    # 選択された最大シーズン数に基づいてデータをフィルタリング
    filtered_data = average_goal_time_by_season.tail(max_seasons)

    plt.figure(figsize=(12, 6))
    filtered_data.plot(kind='bar', color=color)
    plt.title('Average Goal Times by Season')
    plt.xlabel('Season')
    plt.ylabel('Average Goal')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    st.pyplot(plt)




def plot_assists_by_player(data):
    """
    選手ごとのアシスト数を集計し、バーチャートで表示します。ユーザーは表示する選手の数とグラフの色を選択できます。
    """
    st.header('トップアシスト提供選手')
    
    # 表示する選手の数を選択
    number_of_players = st.slider('表示する選手の数を選択してください:', min_value=1, max_value=20, value=10)
    
    # グラフの色を選択
    color = st.color_picker('グラフの色を選択してください:', '#ff5733')
    
    # アシスト数を選手ごとに集計
    assists_by_player = data['Goal_assist'].value_counts().head(number_of_players)
    
    # プロット
    plt.figure(figsize=(12, 6))
    assists_by_player.plot(kind='bar', color=color)
    plt.title('Top Assist Providers')
    plt.xlabel('Player')
    plt.ylabel('Number of Assists')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    st.pyplot(plt)


def show_assist_players_list(data):
    """
    助攻队员名单とその助攻数を表示します。ユーザーは表示する名单の数を選択できます。
    """
    st.header('アシストリストとアシスト数')
    # 表示する名单の数を選択
    number_to_display = st.slider('表示する名单の数:', min_value=1,
                                  max_value=len(data['Goal_assist'].unique()), value=10, step=1)
    # アシスト数を選手ごとに集計
    assists_by_player = data['Goal_assist'].value_counts().head(number_to_display)
    # DataFrameに変換して、より良い表示をする
    assists_df = assists_by_player.reset_index()
    assists_df.columns = ['Player', 'Number of Assists']
    # Streamlitで表を表示
    st.table(assists_df)



def plot_goals_per_club(data):
    """
    各クラブごとの得点数を表示し、円グラフまたは棒グラフで表示するオプションをユーザーに提供します。
    """
    st.header('CR7 の各クラブごとの得点数')
    # 表示形式の選択
    chart_type = st.radio("表示形式を選択してください:", ('円グラフ', '棒グラフ'))
    # 各クラブごとの得点数を集計
    goals_by_club = data['Club'].value_counts()
    if chart_type == '円グラフ':
        # 円グラフの作成
        plt.figure(figsize=(10, 6))
        plt.pie(goals_by_club, labels=goals_by_club.index, autopct='%1.1f%%', startangle=140)
        plt.title('Goals for Clubs', fontsize=20)
    else:
        # 棒グラフの作成
        plt.figure(figsize=(12, 6))
        goals_by_club.plot(kind='bar', color='orange')
        plt.title('Goals for Clubs')
        plt.xlabel('Clubs')
        plt.ylabel('Goals')
        plt.xticks(rotation=45)
    st.pyplot(plt)



def plot_favorite_victims(data):
    """
    CR7の好きな「相手」トップ10をバーチャートで表示し、
    ユーザーは表示する「相手」の数を選択でき、
    また、各バー上の得点数を表示するかどうかを選択できます。
    """
    st.header('CR7 の得意な相手トップ')
    # ユーザーに表示する犠牲者の数を選択させる
    number_of_victims = st.slider('表示するチームの数:', min_value=1, max_value=20, value=10)
    # 得点数を表示するかどうか
    show_values = st.checkbox('得点数を表示する')
    # データ処理
    favorite_victims = data['Opponent'].value_counts().sort_values(ascending=False).head(number_of_victims)
    # プロット
    plt.figure(figsize=(12, 8))
    favorite_victims.plot(kind='bar', color='magenta')
    plt.title('Top Favorite Opponents')
    plt.xlabel('Opponent')
    plt.ylabel('Goals')
    plt.xticks(rotation=45)
    # 得点数を表示するオプションが選択されている場合、各バー上に得点数を表示
    if show_values:
        for index, value in enumerate(favorite_victims):
            plt.text(index, value, str(value), ha='center', va='bottom')
    st.pyplot(plt)





def plot_goals_by_time_quarter(data):
    """
    ユーザーが選択したマッチの四半期ごとにCR7の得点を表示します。
    """
    st.header('マッチの四半期ごとのCR7の得点分布')
    # ユーザーが四半期を選択
    quarter_selection = st.selectbox(
        "表示する四半期を選択してください:",
        ('最初の25分', '26分から47分', '48分から74分', '75分から終了まで')
    )
    # 四半期ごとのデータフィルタリング
    if quarter_selection == '最初の25分':
        filtered_data = data.query('minute_column <= 25')
        title = 'マッチ開始から25分以内のCR7の得点'
    elif quarter_selection == '26分から47分':
        filtered_data = data.query('minute_column > 25 and minute_column <= 47')
        title = '26分から47分の間のCR7の得点'
    elif quarter_selection == '48分から74分':
        filtered_data = data.query('minute_column > 47 and minute_column <= 74')
        title = '48分から74分の間のCR7の得点'
    else:
        filtered_data = data.query('minute_column > 74')
        title = '75分から終了までのCR7の得点'
    # グラフの描画
    plt.figure(figsize=(14, 7))
    sns.countplot(x=filtered_data['minute_column'])
    plt.xticks(rotation=45, ha='center')
    plt.xlabel('Times')
    plt.ylabel('Goals')
    plt.title(title, fontsize=20)
    st.pyplot(plt)



def plot_goals_by_playing_position(data):
    """
    各プレー位置ごとの得点数をバーチャートで表示し、
    ユーザーは得点数の表示順序を選択でき、
    各バー上の得点数を表示するかどうかを選択できます。
    """
    st.header('プレー位置別得点数')
    # 表示順序の選択
    order = st.radio("得点数の表示順序:", ('降順', '昇順'))
    # 得点数を表示するかどうか
    show_values = st.checkbox('各バー上の得点数を表示する')
    # データ処理
    goals_by_position = data.groupby('Playing_Position').size()
    if order == '昇順':
        goals_by_position = goals_by_position.sort_values(ascending=True)
    else:
        goals_by_position = goals_by_position.sort_values(ascending=False)
    # プロット
    plt.figure(figsize=(10, 6))
    goals_by_position.plot(kind='bar', color='lightgreen')
    plt.title('Goals By Playing Position')
    plt.xlabel('Position')
    plt.ylabel('Goals')
    plt.xticks(rotation=45)
    
    # 各バー上の得点数を表示するオプションが選択されている場合、得点数を表示
    if show_values:
        for index, value in enumerate(goals_by_position):
            plt.text(index, value, str(value), ha='center')
    st.pyplot(plt)



def plot_goals_by_type(data):
    """
    ゴールのタイプ別に得点数を分析し、バーチャートで表示します。
    ユーザーはデータの表示順序を選択でき、各バー上に得点数を表示するかどうかを選択できます。
    """
    st.header('ゴールのタイプ別得点数')
    # 表示順序の選択
    order = st.radio("データの表示順序:", ('降順', '昇順'))
    # 得点数を表示するかどうか
    show_values = st.checkbox('各バー上に得点数を表示する')
    # データ処理
    goals_by_type = data['Type'].value_counts()
    if order == '昇順':
        goals_by_type = goals_by_type.sort_values(ascending=True)
    else:
        goals_by_type = goals_by_type.sort_values(ascending=False)
    # プロット
    plt.figure(figsize=(10, 6))
    sns.barplot(x=goals_by_type.index, y=goals_by_type.values, palette='viridis')
    plt.title('Goal Type')
    plt.xlabel('Type')
    plt.ylabel('Goals')
    plt.xticks(rotation=45)
    
    # 各バー上に得点数を表示するオプションが選択されている場合、得点数を表示
    if show_values:
        for index, value in enumerate(goals_by_type.values):
            plt.text(index, value, str(value), ha='center', va='bottom')
        
    st.pyplot(plt)



def plot_data(data):
    chart_option = st.radio(
        "表示したいデータを選択してください:",
        ('重要な試合でのゴール数', '勝敗ごとのゴール数', 'ホームvsアウェイのゴール数')
    )
    if chart_option == '重要な試合でのゴール数':
        # 重要な試合でのゴール数の処理とプロット
        important_matches = data[data['Competition'].str.contains('Champions League Final') | data['Opponent'].str.contains('FC Barcelona')]
        goals_in_important_matches = important_matches.groupby('Season').size()
        plt.figure(figsize=(10, 6))
        goals_in_important_matches.plot(kind='bar', color='gold')
        plt.title('Goals Scored In Important Games')
        for index, value in enumerate(goals_in_important_matches):
            plt.text(index, value, str(value), ha='center')
    elif chart_option == '勝敗ごとのゴール数':
        # 勝敗ごとのゴール数の処理とプロット
        data['Result'] = data['Result'].apply(lambda x: 'Win' if x[0] > x[-1] else ('Draw' if x[0] == x[-1] else 'Loss'))
        goals_result = data['Result'].value_counts()
        plt.figure(figsize=(10, 6))
        goals_result.plot(kind='bar', color=['green', 'gray', 'red'])
        plt.title('Goals Per Win&Loss')
        for index, value in enumerate(goals_result):
            plt.text(index, value, str(value), ha='center')
    else:
        # ホームvsアウェイのゴール数の処理とプロット
        home_away_goals = data['Venue'].value_counts()
        plt.figure(figsize=(10, 6))
        home_away_goals.plot(kind='bar', color=['darkblue', 'orange'])
        plt.title('Home vs. Away Goals')
        for index, value in enumerate(home_away_goals):
            plt.text(index, value, str(value), ha='center')
    plt.xlabel('Types')
    plt.ylabel('Goals')
    plt.xticks(rotation=45)
    st.pyplot(plt)

# 最後実行
if __name__ == '__main__':
    data = pd.read_csv(DATA_PATH)
    # 目録
    analysis_options = [
        'ホーム',
        'シーズン別得点数',
        '競技会別ゴール数',
        'シーズン別平均ゴールタイム',
        'アシスト提供選手について',
        'CR7の各クラブごとの得点数',
        'マッチの四半期ごとのCR7の得点分布',
        '様々なゴールタイプ分布'
        # 其他分析部分的标题...
    ]
    selected_analysis = st.sidebar.selectbox('分析のセクションを選択してください:', analysis_options)
    
    if selected_analysis == 'ホーム':
        st.title('CR7 パフォーマンス分析')
        st.write("""
        ### CR7(クリスティアーノ・ロナウド）の得点データ分析
        このウェブアプリは、サッカー選手CR7の得点データを分析し、彼のパフォーマンスの様々な側面を探るためのものです。
        さまざまな角度からCR7の得点能力を可視化します。
        """)
        
        st.markdown("""
        ### 概要
        サッカー界のスーパースター、CR7(クリスティアーノ・ロナウド）の得点データを深く掘り下げることを目的としています。データを通じて、彼のパフォーマンスの多様な側面を探ります。以下の分析セクションが含まれています：
        - **シーズン別得点数**: CR7が各シーズンに記録した得点数を分析します。彼のキャリアを通じての得点能力の変化を探ります。
        
        - **競技会別ゴール数**: CR7が異なる競技会でどのように得点しているかを見てみます。どの競技会で彼が最も支配的であるかを理解します。
        
        - **シーズン別平均ゴールタイム**: 各シーズンでのCR7の得点が平均的にどのタイミングで起こるかを分析します。彼の得点が試合のどの段階で多く発生するかを見ます。
        
        - **アシスト提供選手について**: CR7の得点に貢献したアシスト提供選手を探ります。彼と最も化学反応を起こしている選手は誰かを見ます。
        
        - **CR7の各クラブごとの得点数**: CR7がキャリアを通じて所属した各クラブでの得点数を比較します。どのクラブで彼が最も輝いていたかを分析します。
        
        - **マッチの四半期ごとのCR7の得点分布**: 試合のどの時間帯にCR7が得点する傾向があるかを見ます。彼の得点が集中している試合の四半期を特定します。
        
        - **様々なゴールタイプ分布**: CR7の得点がどのようなタイプのものであるかを分析します(例：ペナルティキック、フリーキック、ヘディングなど）。彼の得点能力の多様性を探ります。
        """)
        st.write('詳しくは左側からの目録でお選びください')
        url='https://cdn.worldvectorlogo.com/logos/cr7.svg'
        st.image(url,caption='CR7')
    
    elif selected_analysis == 'シーズン別得点数':
        st.header('シーズン別得点数')
        # シーズン選択用のセレクトボックスを設定
        selected_season = st.selectbox('シーズンを選択してください:', data['Season'].unique())
        # 選択されたシーズンのゴール数を表示
        show_season_goals(data, selected_season)
        st.header('全シーズン得点数')
        goals_by_season = data.groupby('Season').size()
        plt.figure(figsize=(12, 6))
        goals_by_season.plot(kind='bar', color='skyblue')
        plt.title('Goals by Season')
        plt.xlabel('Season')
        plt.ylabel('Number of Goals')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--')
        st.pyplot(plt)
    # データの読み込みと前処理はすでに完了しているものとします
    elif selected_analysis == '競技会別ゴール数':
        plot_goals_by_competition(data)
        '''
        CR7はその卓越した得点能力で知られていますが、彼の得点がどの競技会で特に際立っているかを見てみましょう。この分析では、
        CR7が参加したさまざまな競技会(リーグ戦、国内カップ、チャンピオンズリーグなど）での得点数を比較します。
        競技会ごとの得点数を分析することで、CR7がどの大会で最も影響力を発揮しているか、また、
        特定の競技会における彼のパフォーマンスがそのキャリアやチームへの影響をどのように反映しているかを理解できます。
        例えば、チャンピオンズリーグでの得点数が多い場合、CR7が欧州の舞台で非常に強力であることを示しています。また、
        国内リーグやカップ戦での得点数も、彼の一貫性とチームへの貢献度を示す指標となります。
        この分析を通じて、CR7の得点分布を詳しく見て、彼のキャリアの中で特に印象的なパフォーマンスを振り返ることができます。
        '''
    elif selected_analysis =='シーズン別平均ゴールタイム':
        plot_average_goal_time_by_season(average_goal_time_by_season)

        st.markdown('''
                    ### シーズン別平均ゴールタイム分析
                    このセクションでは、CR7が各シーズンに記録したゴールの平均時間を分析します。ゴールが試合のどの段階で多く発生するかを理解することは、CR7のプレースタイルとチーム戦略に関する洞察を提供します。
                    - **分析の目的**: CR7の得点パターンを時間軸で捉え、彼が試合のどの時間帯に最も得点効率が高いかを明らかにします。
                    
                    - **方法**: 各シーズンのCR7によるゴールの記録を集計し、発生した試合時間を基に平均値を算出します。
                    
                    - **洞察の可能性**: 特定のシーズンで平均ゴールタイムが早い場合、CR7が試合開始直後から積極的に得点を狙っていることが示唆されます。逆に、平均ゴールタイムが遅い場合、試合終盤に強さを発揮する傾向にあるかもしれません。
                    
                    この分析を通じて、CR7の得点がチームの勝利にどのように貢献しているか、また、彼のプレースタイルがシーズンによってどのように変化しているかを探ります。
                    """)
                    ''')
    
    
    elif selected_analysis =='アシスト提供選手について':
        plot_assists_by_player(data)
        show_assist_players_list(data)
        
        st.markdown("""
                    ### アシスト提供選手についての分析

                    CR7(クリスティアーノ・ロナウド)の輝かしい得点記録の背後には、彼を支えるチームメイトの存在があります。このセクションでは、CR7の得点に貢献したアシスト提供選手を詳しく見ていきます。特定の選手からのアシストがCR7の得点にどの程度影響を与えているのか、また、彼と最も相性の良い選手は誰なのかを分析します。
                    - **分析の目的**: CR7へのアシスト提供選手の中で、特に目立つ貢献をした選手を特定し、CR7との連携の強さを探ります。
                    
                    - **方法**: CR7の得点に直接関連するアシストのデータを集計し、提供選手ごとのアシスト数を分析します。
                    
                    - **洞察の可能性**: 特定の選手からのアシストが多い場合、その選手とCR7との間に強い化学反応があることを示しています。チーム戦略やフォーメーションの中で、これらの選手をどのように活用すれば、さら
                    """)
        
        
        
    elif selected_analysis =='CR7の各クラブごとの得点数':
        plot_goals_per_club(data)
    
    elif selected_analysis == 'マッチの四半期ごとのCR7の得点分布':
        
        def convert_extra_time(match_time):
            match_time_parts = match_time.split('+')
            if len(match_time_parts) == 2:
                return int(match_time_parts[0])+ int (match_time_parts[1])
            else:
                return int(match_time)
        data['minute_column'] = data['Minute'].apply(convert_extra_time)
        plot_goals_by_time_quarter(data)
    
        st.markdown('''
                    ### マッチの四半期ごとのCR7の得点分布分析
                    CR7(クリスティアーノ・ロナウド)の得点能力は、試合のあらゆる段階で発揮されます。しかし、彼が試合のどの時間帯に最も得点するのか、そのパターンを理解することは、彼のプレースタイルと戦術的な貢献を深く理解する上で非常に有益です。このセクションでは、試合時間を四半期（前半の前半、前半の後半、後半の前半、後半の後半)に分け、それぞれの時間帯でのCR7の得点分布を分析します。
                    - **分析の目的**: CR7が試合の各四半期にどのように得点しているかを明らかにし、彼の得点が試合の流れや戦術にどのように影響を与えているかを探ります。
                    
                    - **方法**: CR7の得点記録を時間帯ごとに分類し、各四半期での得点数を集計します。
                    
                    - **洞察の可能性**: 特定の四半期に得点数が集中している場合、CR7が試合の特定の段階で特に危険であること、またはチームがその時間帯に攻撃的になる傾向があることを示唆しています。逆に、得点が時間帯に均等に分布している場合、CR7の一貫性と試合を通じての脅威を反映しています。
                    
                    この分析を通じて、CR7の得点パターンと試合中の活躍のタイミングに関する洞察を得ることができます。また、相手チームの守備戦略や、CR7をいかに抑えるかについての重要な情報も提供します。
                    ''')
    
    
    elif selected_analysis =='様々なゴールタイプ分布':
        
        plot_goals_by_playing_position(data)
        
        plot_favorite_victims(data)
        
        plot_goals_by_type(data)
        
        plot_data(data)
        st.write("""
        #### 分析のポイント
        - **プレー位置別得点数分析**: ある特定のプレー位置で得点数が特に多い場合、CR7がその位置で非常に効果的であることを示しています。また、複数の位置で均等に得点している場合、彼の多様性と攻撃における適応能力の高さを反映しています。
        
        - **CR7の好きな犠牲者**:特定のチームに対する得点数が多い場合、それはCR7がそのチームの守備スタイルに対して特に有効である、または心理的な優位性を持っていることを示している可能性があります。この分析は、CR7がなぜ特定のチームに対して高い得点率を誇るのか、その背景にある要因を明らかにする手がかりを提供します。
        
        - **ホームvsアウェイ**: ホームスタジアムとアウェイでの試合で、CR7の得点パターンに違いはあるか
        
        - **様々なゴールタイプ分布**:もし特定のタイプのゴールが多い場合、それはCR7がその得点手段において特に優れていることを示しています。また、ゴールのタイプが多様であればあるほど、CR7の攻撃オプションの幅広さと、異なる状況において得点できる能力を反映しています。
        
        CR7がどのようにして相手の守備を打ち破り、様々な方法でゴールを決めるのかについての洞察を得ることができます。また、彼の得点手段の多様性が、なぜ彼を世界のトッププレーヤーの一人にしているのかを理解する手がかりとなります。
        """)
    
