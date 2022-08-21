# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import calendar
from datetime import date 
import streamlit as st

# funcoes
# criaçao do calendario mensal
def cal_mensal(monthnumber):
    return calendar.monthrange(date.today().year, monthnumber)

# descontos
def desc_preventivas(descontos, monthnumber, prev_datas):
    for i in range (0,2):
        if prev_datas[i][0] == monthnumber:
            k = len(descontos) - prev_datas[i][1]
            if k > 7:
                for j in range(0,7):
                    descontos[prev_datas[i][1] + j] = -2
                        
                descontos[prev_datas[i][1] + j] = 5
            else:
                for j in range(0,k):
                    descontos[prev_datas[i][1] + j] = -2
                        
        elif prev_datas[i][2] == monthnumber:
            for j in range(0, prev_datas[i][3]):
                descontos[j] = -2
            descontos[prev_datas[i][3] + j-1] = 5
            
    return descontos
                
def desc_domingos(descontos, monthnumber):
    for i in range(len(descontos)):
        if calendar.weekday(date.today().year, monthnumber, i+1) % 7 == 6:
            descontos[i] = 0
    return descontos

def desc_feriados(descontos, monthnumber, tam, feriado_datas, psem, pinicio):
    for i in range(0,tam):
        if feriado_datas[i][1] == monthnumber:
            descontos[feriado_datas[i][2]-1] = -1
            if feriado_datas[i][2] - 2 >= 0:
                descontos[feriado_datas[i][2] - 2] += -psem
                if feriado_datas[i][2] <= len(descontos) - 1:
                    descontos[feriado_datas[i][2]] += -pinicio
            else:
                descontos[feriado_datas[i][2]] += -pinicio
    return descontos            
        
def desc_inv(descontos, psem, monthnumber):
        if descontos[-1] > 0 and calendar.weekday(date.today().year, monthnumber, len(descontos)) % 7 != 6:
            descontos[-1] = -3
            descontos[-2] += -psem
        elif descontos[-1] < 0 and calendar.weekday(date.today().year, monthnumber, len(descontos)) % 7 != 6:
            descontos[-2] = -3
        else:
            descontos[-2] = -3
            descontos[-3] += -psem
        
        return descontos
    
def desc_inicio(descontos, tam, feriado_datas, pinicio, horas, monthnumber):
    for i in range(0, tam):
        if descontos[0] > 0 and feriado_datas[i][1] == monthnumber - 1 and feriado_datas[i][2] == calendar._monthlen(date.today().year, monthnumber-1):
            descontos[0] += -pinicio
            
    for i in range(len(descontos)):
        if descontos[i] > 0 and calendar.weekday(date.today().year, monthnumber, i+1) % 7 == 0:
          descontos[i] += -pinicio
    
    return descontos

def desc_fim(descontos, pfim, horas, monthnumber):
    for i in range(len(descontos)):
        if descontos[i] > 0 and calendar.weekday(date.today().year, monthnumber, i+1) % 7 != 5:
            descontos[i] += -pfim

    return descontos

def desc_fimsem(descontos, psem, horas, monthnumber):
    for i in range(len(descontos)):
        if descontos[i] > 0 and calendar.weekday(date.today().year, monthnumber, i+1) % 7 == 5:
            descontos[i] += -psem
            
    return descontos

def desc_admpip(descontos, adm, monthnumber):
    for i in range(len(descontos)):
        if descontos[i] > 0 :
            descontos[i] += -adm
    
    return descontos

# leitura dos arquivos necessários

adm_pip = pd.read_excel(r'P:\LYS\Pastas\Projeto - Automatização\bases_capacidade_produtiva.xlsx', sheet_name= 'PIP')
adm_pip = adm_pip.sort_values(by = ['Linhas'])
feriados = pd.read_excel(r'P:\LYS\Pastas\Projeto - Automatização\bases_capacidade_produtiva.xlsx', sheet_name= 'FERIADOS')
preventivas = pd.read_excel(r'P:\LYS\Pastas\Projeto - Automatização\bases_capacidade_produtiva.xlsx', sheet_name= 'PREVENTIVA')
preventivas = preventivas.sort_values(by = ['Linhas'])

# codigo fonte

# criacao do aplicativo web


st.title('Capacidade Produtiva')
st.text('Aplicativo para estudos sobre capacidade produtiva')
st.header('Calendário')

no_mes = st.number_input("Insira o número do mês: ", min_value = 1, max_value = 12, format = '%d')
q1 = "Selecione as linhas em que deseja calcular a capacidade:"
opcoes = adm_pip.iloc[:,0].values
selecao = st.multiselect(q1,opcoes)
linhas = []
indices = []
no_linhas = len(selecao)
print(no_linhas)
for i in range(no_linhas):
    linhas.append(selecao[i])
    for j in range(len(opcoes)):
        if selecao[i] == opcoes[j]:
            indices.append(j)

print(linhas, indices)

turnos = np.zeros(no_linhas)
horas_disponiveis = np.zeros(no_linhas)
demanda = np.zeros(no_linhas)
col1, col2 = st.columns(2)    

with col1:
    with st.form("inputs-de-demanda"):
        for i in range(len(selecao)):
            demanda[i] = st.number_input('Demanda (ton) da linha ' + selecao[i] + ':', min_value = 0)
        envio_1 = st.form_submit_button('Enviar')
with col2:
    with st.form('inputs-de-turnos'):
        for i in range(len(selecao)):
            turnos[i] = st.number_input('Turno da linha ' + selecao[i] + ':', min_value = 1, format = '%d')
            turnos[i] = int(turnos[i])
        envio_2 = st.form_submit_button('Enviar')



for i in range(0, no_linhas):
    if turnos[i] == 1:
        horas_disponiveis[i] = 8
    elif turnos[i] == 2:
        horas_disponiveis[i] = 18
    elif turnos[i] == 3:
        horas_disponiveis[i] = 23
    else:
        horas_disponiveis[i] = 24

c_produtiva = np.zeros(no_linhas)
gap_horas = np.zeros(no_linhas)
hdo = np.zeros(no_linhas)
cal_linhas = []

for i in range(no_linhas):
    capacidade = adm_pip.iloc[:,5].values[indices[i]]
    inicio_mes, dias_mes = cal_mensal(no_mes)
    descontos = np.ones(dias_mes)*horas_disponiveis[i]
    descontos = desc_preventivas(descontos, no_mes, preventivas.iloc[:,3:].values[:2+2*indices[i]])
    descontos = desc_feriados(descontos, no_mes, len(feriados), feriados.iloc[:,1:].values, adm_pip.iloc[:,4].values[indices[i]], adm_pip.iloc[:,2].values[indices[i]])
    descontos = desc_inv(descontos, adm_pip.iloc[:,4].values[indices[i]], no_mes)
    if turnos[i] != 4:
        descontos = desc_inicio(descontos, len(feriados), feriados.iloc[:,1:].values, adm_pip.iloc[:,2].values[indices[i]], horas_disponiveis[i], no_mes)
        descontos = desc_fim(descontos, adm_pip.iloc[:,3].values[indices[i]], horas_disponiveis[i], no_mes)
        descontos = desc_fimsem(descontos, adm_pip.iloc[:,4].values[indices[i]], horas_disponiveis[i], no_mes)
        descontos = desc_domingos(descontos, no_mes)
        descontos = desc_admpip(descontos, adm_pip.iloc[:,1].values[indices[i]], no_mes)
    
    hdo[i] = sum(descontos) + (descontos == -1).sum() + 2*(descontos == -2).sum() + 3*(descontos == -3).sum()
    c_produtiva[i] = hdo[i]*capacidade/1000
    gap_horas[i] = 1000*(c_produtiva[i] - demanda[i])/capacidade
    cal_linhas.append(descontos)

for i in range(len(gap_horas)):
    if gap_horas[i] < 0:
        index = np.argmax(gap_horas)
        if turnos[i] < turnos[index]:
            for j in range(len(cal_linhas[0])):
                if cal_linhas[i][j] > 0 and gap_horas[index] > 0:
                    cal_linhas[i][j] += 6
                    cal_linhas[index][j] -= 6 
                    gap_horas[index] -= 6
                    gap_horas[i] += 6
                    if gap_horas[i] >= 0:
                        break
                        
                        
        elif turnos[i] == turnos[index]:
            for j in range(len(cal_linhas[0])):
                if cal_linhas[i][j] > 0 and gap_horas[index] > 0:
                    k = 24 - cal_linhas[i][j]
                    cal_linhas[i][j] += k
                    cal_linhas[index][j] -= k 
                    gap_horas[index] -= k
                    gap_horas[i] += k
                    if gap_horas[i] >= 0:
                        break
                        
        else:
            for j in range(len(cal_linhas[0])):
                if cal_linhas[i][j] > 0 and gap_horas[index] > 0:
                    k =  24 - cal_linhas[i][j]
                    cal_linhas[i][j] += k
                    cal_linhas[index][j] -= 6
                    gap_horas[i] += k
                    gap_horas[index] -= 6   
                    if gap_horas[i] >= 0:
                        break
                    
                        
for i in range(no_linhas):
    st.write('Calendário da linha ' + selecao[i])
    st.write('Gap de horas: %.2f' % gap_horas[i])
    st.write(cal_linhas[i])
