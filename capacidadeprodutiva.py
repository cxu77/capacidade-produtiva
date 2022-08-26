import numpy as np
import pandas as pd
import calendar
from datetime import date 
import streamlit as st
import requests
from io import BytesIO
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

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
            descontos[i] = 0.
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
        if descontos[i] > 0 and calendar.weekday(date.today().year, monthnumber, i+1) % 7 == 0 and descontos[i] != 5:
          descontos[i] += -pinicio
    
    return descontos

def desc_fim(descontos, pfim, horas, monthnumber):
    for i in range(len(descontos)):
        if descontos[i] > 0 and calendar.weekday(date.today().year, monthnumber, i+1) % 7 != 5 and descontos[i] != 5:
            descontos[i] += -pfim

    return descontos

def desc_fimsem(descontos, psem, horas, monthnumber):
    for i in range(len(descontos)):
        if descontos[i] > 0 and calendar.weekday(date.today().year, monthnumber, i+1) % 7 == 5 and descontos[i] != 5:
            descontos[i] += -psem
            
    return descontos

def desc_admpip(descontos, adm, monthnumber):
    for i in range(len(descontos)):
        if descontos[i] > 0 and descontos[i] != 5:
            descontos[i] += -adm
    
    return descontos

def desc_4turnos(descontos, monthnumber):
    for i in range(len(descontos)):
        if calendar.weekday(date.today().year, monthnumber, i+1) % 7 < 5 and descontos[i] > 0 and descontos[i] !=5:
            descontos[i] -= 1
        else:
            descontos[i] -= 2

# leitura dos arquivos necessários
url = "https://raw.githubusercontent.com/cxu77/capacidade-produtiva/main/bases-capacidade-produtiva.xlsx"
r = requests.get(url).content
adm_pip = pd.read_excel(BytesIO(r), sheet_name= 'PIP')
adm_pip = adm_pip.sort_values(by = ['LINHAS'])
feriados = pd.read_excel(BytesIO(r), sheet_name= 'Feriados')
preventivas = pd.read_excel(BytesIO(r), sheet_name= 'Preventiva')
preventivas = preventivas.sort_values(by = ['LINHAS'])

# codigo fonte

# criacao do aplicativo web


st.title('Capacidade Produtiva')
st.text('Aplicativo para estudos sobre capacidade produtiva')
st.header('Calendário')

#inserção do mês e escolha de opções de linhas
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


#criação de variaveis auxiliares

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
capacidade = np.zeros(no_linhas)
gap_horas = np.zeros(no_linhas)
necess = np.zeros(no_linhas)
hdo = np.zeros(no_linhas)
cal_linhas = []

for i in range(no_linhas):
    capacidade[i] = adm_pip.iloc[:,5].values[indices[i]]
    inicio_mes, dias_mes = cal_mensal(no_mes)
    descontos = np.ones(dias_mes)*horas_disponiveis[i]
    descontos = desc_preventivas(descontos, no_mes, preventivas.iloc[:,3:].values[2*indices[i]:2+2*indices[i]])
    descontos = desc_feriados(descontos, no_mes, len(feriados), feriados.iloc[:,1:].values, adm_pip.iloc[:,4].values[indices[i]], adm_pip.iloc[:,2].values[indices[i]])
    descontos = desc_inv(descontos, adm_pip.iloc[:,4].values[indices[i]], no_mes)
    if turnos[i] < 4:
        descontos = desc_inicio(descontos, len(feriados), feriados.iloc[:,1:].values, adm_pip.iloc[:,2].values[indices[i]], horas_disponiveis[i], no_mes)
        descontos = desc_fim(descontos, adm_pip.iloc[:,3].values[indices[i]], horas_disponiveis[i], no_mes)
        descontos = desc_fimsem(descontos, adm_pip.iloc[:,4].values[indices[i]], horas_disponiveis[i], no_mes)
        descontos = desc_domingos(descontos, no_mes)
        descontos = desc_admpip(descontos, adm_pip.iloc[:,1].values[indices[i]], no_mes)
    #else:
        #descontos = desc_4turnos(descontos, no_mes)
        
    #sum1 = np.count_nonzero(descontos == -1)
    #sum2 = 2*np.count_nonzero(descontos == -2)
    #sum3 = 3*np.count_nonzero(descontos == -3)

    hdo[i] = sum(filter(lambda x: x>=0, descontos))
    necess[i] = 1000*demanda[i]/capacidade[i]
    c_produtiva[i] = hdo[i]*capacidade[i]/1000
    gap_horas[i] = hdo[i] - necess[i]
    cal_linhas.append(descontos)



if "LB04" in selecao and "LB09" in selecao:
    index_lb04 = selecao.index("LB04")
    index_lb09 = selecao.index("LB09")
    max_index = max(index_lb04, index_lb09)
    min_index = min(index_lb04, index_lb09)
    for j in range(len(cal_linhas[0])):
        k = gap_horas[max_index]
        if cal_linhas[max_index][j] > 0 and k - cal_linhas[max_index][j] < 0:
            break
        else:
            gap_horas[max_index] -= cal_linhas[max_index][j]
            cal_linhas[max_index][j] = 0
    
    for i in range(j, len(cal_linhas[min_index])):
        if cal_linhas[min_index][i] > 0:
            gap_horas[min_index] -= cal_linhas[min_index][i]
            cal_linhas[min_index][i] = -4
 

for i in range(len(gap_horas)):
    if gap_horas[i] < 0:
        index = np.argmax(gap_horas)
        if turnos[i] < turnos[index]:
            for j in range(len(cal_linhas[0])):
                if cal_linhas[i][j] > 0 and cal_linhas[index][j] > 0 and gap_horas[index] > 0:
                    cal_linhas[i][j] += 5*capacidade[index]/capacidade[i]
                    cal_linhas[index][j] -= 5 
                    gap_horas[index] -= 5
                    gap_horas[i] += cal_linhas[i][j]
                    if gap_horas[i] >= 0:
                        break
                        
                        
        elif turnos[i] == turnos[index]:
            for j in range(len(cal_linhas[0])):
                if cal_linhas[i][j] > 0 and cal_linhas[index][j] > 0 and cal_linhas[index][j] !=5 and gap_horas[index] > 0:    
                    k = (3-turnos[i])*5*capacidade[index]/capacidade[i]
                    p = cal_linhas[i][j]
                    if k == 0: 
                        k = 1*capacidade[index]/capacidade[i]
                    cal_linhas[i][j] += k
                    if cal_linhas[i][j] > 24:
                        cal_linhas[i][j] = 24
                    cal_linhas[index][j] -= 5
                    if cal_linhas[index][j] < 0:
                        cal_linhas[index][j] = 0
                    gap_horas[index] -= 5
                    gap_horas[i] += cal_linhas[i][j] - p
                    if gap_horas[i] >= 0:
                        break
                        
        else:
            for j in range(len(cal_linhas[0])):
                if cal_linhas[i][j] > 0 and cal_linhas[index][j] > 0 and gap_horas[index] > 0:
                    k =  (3-turnos[index])*5*capacidade[index]/capacidade[i]
                    p = cal_linhas[i][j]
                    if k == 0:
                        k = 1*capacidade[index]/capacidade[i]
                    cal_linhas[i][j] += k
                    if cal_linhas[i][j] > 24:
                        cal_linhas[i][j] = 24
                    cal_linhas[index][j] -= 5
                    if cal_linhas[index][j] < 0:
                        cal_linhas[index][j] = 0
                    gap_horas[i] += cal_linhas[i][j] - p
                    gap_horas[index] -= 5   
                    if gap_horas[i] >= 0:
                        break
                                        
for i in range(0, no_linhas):
    if gap_horas[i] < 0:
        for j in range(len(cal_linhas[0])):
            if cal_linhas[i][j] == 0:
                cal_linhas[i][j] = horas_disponiveis[i] - adm_pip.iloc[:,3].values[indices[i]] - adm_pip.iloc[:,2].values[indices[i]] - adm_pip.iloc[:,1].values[indices[i]]
                gap_horas[i] += cal_linhas[i][j]
                if gap_horas[i] >= 0:
                    break           

nome_colunas = []
for i in range(len(cal_linhas[0])):
    nome_colunas.append(str(i+1) + "/" + str(no_mes) + "/" + str(date.today().year))

cal = pd.DataFrame(cal_linhas)
cal.columns = nome_colunas
cal = cal.round(2)
cal['Linhas'] = selecao
coluna1 = cal.pop('Linhas')
cal.insert(0, 'Linhas', coluna1)
cal.replace(-1, "FERIADO", inplace=True)
cal.replace(-2, "PREV", inplace=True)
cal.replace(-3, "INV", inplace = True)
cal.replace(-4, 0, inplace = True)
gb = GridOptionsBuilder.from_dataframe(cal)
gb.configure_columns(column_names=nome_colunas, editable = True, groupable = True, precision = 1)
#gb.configure_auto_height()
go = gb.build()  
results = AgGrid(data = cal, reload_data = False, gridOptions = go, enable_enterprise_modules=True)
agregado = pd.DataFrame.from_dict(results["data"])
agregado = agregado.groupby(['Linhas']).sum()
#agregado['Horas'] = agregado.sum(axis=1)
#agregado['Necessario'] = necess
#agregado['HDO'] = hdo
#agregado['Gap_Calculado'] = gap_horas
#agregado['Gap Horas'] = agregado['Gap_Calculado'] + ((agregado['Horas'] - agregado['Necessario']) - agregado['Gap_Calculado'])
#agregado['Gap Dias'] = agregado['Gap Horas']/24
#agregado['Gap Horas'] = agregado['Gap Horas'].round(2)
#agregado['Gap Dias'] = agregado['Gap Dias'].round(0)
#result_agregado = agregado[['Linhas', 'Gap Horas', 'Gap Dias']]
#agregado['Linhas'] = selecao
#coluna1 = agregado.pop('Linhas')
#agregado.insert(0,'Linhas', coluna1)
st.write("Gap (em horas e em dias)")
#gb = GridOptionsBuilder.from_dataframe(agregado["data"])
#gb.configure_columns(columns_names =[], groupable=True, value=True, enableRowGroup=True, editable=False)
#go = gb.build()
st.dataframe(agregado)
#st.dataframe(result_agregado)    
