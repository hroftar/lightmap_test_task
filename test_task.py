#!/usr/bin/env python
# coding: utf-8

# In[257]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime


# In[259]:


fights_file = 'fights_test.csv'
payers_file = 'payers_test.csv'

fights = pd.read_csv(fights_file, index_col=0)
payers = pd.read_csv(payers_file, index_col=0)

#посчитал и добавил общую сумму платежей для каждого игрока 
id_pay = payers.groupby('player_id')['cost'].sum().reset_index()
fights = fights.merge(id_pay, how='left', on='player_id').set_index(fights.index)
fights.rename(columns={'cost':'total_paid'}, inplace=True)
print(fights.head())


# In[260]:


#создал копию df боев и платежей, чтоб посчитать DAU оттдельно
ft = fights.copy()
ft['event_date'] = pd.to_datetime(ft['event_ts'], unit='s').dt.date

p = payers.copy()
p['event_date'] = pd.to_datetime(p['event_ts'], unit='s').dt.date


# In[261]:


#рассчет DAU и количества уникальных плательщиков за каждый день
#соотношение плательщиков к DAU сохранено как payers_part

#DAU считается как количество уникальных пользователей как игравших матчи,
#так и совершавших покупки для каждого дня 
comb = ft[['player_id', 'event_date']].append(p[['player_id', 'event_date']])
dau = comb.groupby('event_date')['player_id'].nunique().reset_index()
dau.rename(columns={'player_id':'dau'}, inplace=True)

#платившие пользователи считаются как количество уникальных пользователей
#совершавших какую-либо покупку для каждого дня 
pp = p.groupby('event_date')['player_id'].nunique().reset_index()
pp.rename(columns={'player_id':'payers'}, inplace=True)
comb = dau.merge(pp, how='left', on='event_date')
comb['payers_part'] = round(comb['payers']/comb['dau']*100, 2)
dates = comb['event_date'].to_numpy()
payers_part = comb['payers_part'].to_numpy()

print(comb)

fig, ax = plt.subplots(1,1, figsize=(10,5))
ax.plot(dates, payers_part, marker='o')

plt.xlabel('Даты')
plt.ylabel('Процент плательщиков по отношению к DAU, %')
plt.xticks(ticks = np.arange(dates[0], dates[len(dates)-1]+datetime.timedelta(days=1), 1), labels = dates, rotation='vertical')

plt.grid(True)
plt.show()


# In[262]:


#медиана и квартили для каждого игрока
#я тут предположил, что нас интересует сумма убийств на игрока, а не среднее значение
id_kills = fights.groupby('player_id')['kills'].sum().reset_index()
id_kills.rename(columns={'kills':'kill_sum'}, inplace=True)
print(id_kills['kill_sum'].describe())
#или если только квартили
print(id_kills['kill_sum'].quantile([0.25, 0.5, 0.75]))


# In[263]:


#считаем количество киллов по режиму и карте
map_mode_kills = fights.pivot_table(index='map', columns='mode', values='kills', aggfunc='sum')
print(map_mode_kills)


# In[264]:


#считаем среднее и суммарное количество киллов по режиму и карте в разные дни!
date_mapmode_kills = ft.pivot_table(index='event_date', columns=['mode', 'map'],
                                   values='kills', aggfunc=['sum', 'mean'])
date_mapmode_kills['mean'] = date_mapmode_kills['mean'].round(2)
print(date_mapmode_kills)


# In[265]:


#ДОП ЗАДАНИЕ!
#убивают ли платящие игроки чаще? Посчитаем среднее количество убийств
#1. для плательщиков
#2. для неплательщиков
#3. для всей группы пользователей 

#среднее число убийств для плательщика
payers2 = fights.dropna()
aver_payer_score = payers2.groupby('player_id')['kills'].mean().reset_index()['kills'].mean().round(2)

#среднее число убийств для неплательщика
non_payers = fights[fights['total_paid'].isna()]
aver_nonpayer_score = non_payers.groupby('player_id')['kills'].mean().reset_index()['kills'].mean().round(2)

#общее среднее число убийств 
aver_all = fights.groupby('player_id')['kills'].mean().reset_index()['kills'].mean().round(2)

print('Сравнение среднего числа убийств:')
print('Плательщик: ', aver_payer_score)
print('Неплательщик: ', aver_nonpayer_score)
print('Среднее значение: ', aver_all)

#Соответственно, в среднем, платящий игрок убивает реже, чем игрок, который не платит

