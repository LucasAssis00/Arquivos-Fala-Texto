#print("Hello world!")
br_number_system = {
    'zero': 0,
    'um': 1,
    'uma': 1,
    'dois': 2,
    'duas': 2,
    'tres': 3,
    'quatro': 4,
    'cinco': 5,
    'seis': 6,
    'sete': 7,
    'oito': 8,
    'nove': 9,
    'dez': 10,
    'onze': 11,
    'doze': 12,
    'treze': 13,
    'catorze': 14,
    'quinze': 15,
    'dezesseis': 16,
    'dezessete': 17,
    'dezoito': 18,
    'dezenove': 19,
    'vinte': 20,
    'trinta': 30,
    'quarenta': 40,
    'cinquenta': 50,
    'sessenta': 60,
    'setenta': 70,
    'oitenta': 80,
    'noventa': 90,
    'cem': 100,
    'cento': 100,
    #'mil': 1000,
    #'milhão': 1000000,
    #'bilhão': 1000000000,
    #'ponto': '.'

}

decimal_words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']


"""
function to form numeric multipliers for million, billion, thousand etc.

input: list of strings
return value: integer
"""


def number_formation(number_words):
    numbers = []
    for number_word in number_words:
        numbers.append(br_number_system[number_word])
#    if len(numbers) == 4:
#        return (numbers[0] * numbers[1]) + numbers[2] + numbers[3]
    if len(numbers) == 3:
        return numbers[0] + numbers[1] + numbers[2]
    elif len(numbers) == 2:
        return numbers[0] + numbers[1]
    else:
        return numbers[0]




"""
function to return integer for an input `number_sentence` string
input: string
output: int or double or None
"""
def word_to_num(number_sentence):
    if type(number_sentence) is not str:
        raise ValueError("Type of input is not string! Please enter a valid number word (eg. \'two million twenty three thousand and forty nine\')")

    number_sentence = number_sentence.replace('-', ' ')
    number_sentence = number_sentence.lower()  # converting input to lowercase

    if(number_sentence.isdigit()):  # return the number if user enters a number string
        return int(number_sentence)

    split_words = number_sentence.strip().split()  # strip extra spaces and split sentence into words

    clean_numbers = []
    clean_decimal_numbers = []

    # removing and, & etc.
    for word in split_words:
        if word in br_number_system:
            clean_numbers.append(word)

    # Error message if the user enters invalid input!
    if len(clean_numbers) == 0:
        raise ValueError("No valid number words found! Please enter a valid number word (eg. two million twenty three thousand and forty nine)")

    # Error if user enters million,billion, thousand or decimal point twice
    if clean_numbers.count('thousand') > 1 or clean_numbers.count('million') > 1 or clean_numbers.count('billion') > 1 or clean_numbers.count('point')> 1:
        raise ValueError("Redundant number word! Please enter a valid number word (eg. two million twenty three thousand and forty nine)")

    # separate decimal part of number (if exists)
    if clean_numbers.count('point') == 1:
        clean_decimal_numbers = clean_numbers[clean_numbers.index('point')+1:]
        clean_numbers = clean_numbers[:clean_numbers.index('point')]

    billion_index = clean_numbers.index('billion') if 'billion' in clean_numbers else -1
    million_index = clean_numbers.index('million') if 'million' in clean_numbers else -1
    thousand_index = clean_numbers.index('thousand') if 'thousand' in clean_numbers else -1

    if (thousand_index > -1 and (thousand_index < million_index or thousand_index < billion_index)) or (million_index>-1 and million_index < billion_index):
        raise ValueError("Malformed number! Please enter a valid number word (eg. two million twenty three thousand and forty nine)")

    total_sum = 0  # storing the number to be returned

    if len(clean_numbers) > 0:
        # hack for now, better way TODO
        if len(clean_numbers) == 1:
                total_sum += br_number_system[clean_numbers[0]]

        else:
            if billion_index > -1:
                billion_multiplier = number_formation(clean_numbers[0:billion_index])
                total_sum += billion_multiplier * 1000000000

            if million_index > -1:
                if billion_index > -1:
                    million_multiplier = number_formation(clean_numbers[billion_index+1:million_index])
                else:
                    million_multiplier = number_formation(clean_numbers[0:million_index])
                total_sum += million_multiplier * 1000000

            if thousand_index > -1:
                if million_index > -1:
                    thousand_multiplier = number_formation(clean_numbers[million_index+1:thousand_index])
                elif billion_index > -1 and million_index == -1:
                    thousand_multiplier = number_formation(clean_numbers[billion_index+1:thousand_index])
                else:
                    thousand_multiplier = number_formation(clean_numbers[0:thousand_index])
                total_sum += thousand_multiplier * 1000

            if thousand_index > -1 and thousand_index != len(clean_numbers)-1:
                hundreds = number_formation(clean_numbers[thousand_index+1:])
            elif million_index > -1 and million_index != len(clean_numbers)-1:
                hundreds = number_formation(clean_numbers[million_index+1:])
            elif billion_index > -1 and billion_index != len(clean_numbers)-1:
                hundreds = number_formation(clean_numbers[billion_index+1:])
            elif thousand_index == -1 and million_index == -1 and billion_index == -1:
                hundreds = number_formation(clean_numbers)
            else:
                hundreds = 0
            total_sum += hundreds

    # adding decimal part to total_sum (if exists)
    if len(clean_decimal_numbers) > 0:
        decimal_sum = get_decimal_sum(clean_decimal_numbers)
        total_sum += decimal_sum

    return total_sum


def edit_text_in_terminal(text):
    # Cria a janela principal
    main_window = tk.Tk()
    main_window.withdraw()  # Oculta a janela principal

    # Ajusta o tamanho da janela (largura e altura)
    main_window.geometry("1000x2000")  # Aumenta a janela para ficar mais larga


    # Configura a caixa de diálogo com o texto inicial, ajustando a fonte
    novo_texto = simpledialog.askstring(
        "Editar Procedimento", "                        Edite o procedimento abaixo:                        ",
        initialvalue=text,
        parent=main_window
    )

    # Fecha a janela principal após a entrada
    main_window.destroy()

    return novo_texto

def selecionar_procedimento(iezimo, possibilidades, transcricao_original):
    def confirmar_selecao(event=None):
        opcao_index = opcao_var.get()
        if opcao_index == 3:  # Caso seja "Reescrever procedimento"
            reescrever_procedimento()
        else:
            result.set(opcao_index)
            janela_selecao.destroy()

    def reescrever_procedimento():
        def salvar_reescrita():
            novo_texto = text_widget.get("1.0", "end-1c")
            result.set(novo_texto)
            janela_reescrita.destroy()
            janela_selecao.destroy()

        # Janela para reescrever o procedimento
        janela_reescrita = tk.Toplevel(janela_selecao)
        janela_reescrita.title("Reescrever Procedimento")

        label_reescrever = tk.Label(janela_reescrita, text="Reescreva o procedimento:")
        label_reescrever.pack(pady=5)

        text_widget = tk.Text(janela_reescrita, wrap="word", width=60, height=10, font=("Arial", 12))
        text_widget.insert("1.0", transcricao_original)
        text_widget.pack(padx=10, pady=10)

        botao_salvar = tk.Button(janela_reescrita, text="Salvar", command=salvar_reescrita)
        botao_salvar.pack(pady=5)

    # Janela de seleção
    janela_selecao = tk.Tk()
    janela_selecao.title(f"{iezimo+1}º Procedimento")

    instrucao = tk.Label(janela_selecao, text=f"O {iezimo+1}º procedimento citado corresponde à:")
    instrucao.pack(pady=10)

    # Variável para armazenar a seleção
    opcao_var = tk.IntVar(value=0)  # Seleção inicial (índice 0)

    # Opções com Radiobuttons
    for idx, procedimento in enumerate(possibilidades):
        tk.Radiobutton(
            janela_selecao, text=f"{idx}. {procedimento[0]}", variable=opcao_var, value=idx
        ).pack(anchor="w", padx=20)

    # Opção adicional para reescrever o procedimento
    tk.Radiobutton(
        janela_selecao, text="3. Reescrever procedimento", variable=opcao_var, value=3
    ).pack(anchor="w", padx=20)

    # Botão e atalho para confirmar seleção
    botao_confirmar = tk.Button(janela_selecao, text="Confirmar", command=confirmar_selecao)
    botao_confirmar.pack(pady=5)
    janela_selecao.bind("<Return>", confirmar_selecao)  # Atalho para pressionar Enter

    result = tk.StringVar()

    janela_selecao.mainloop()

    return result.get()


def save_variables(Quantidade, Custo, Procedimento, Somatudo):
    j = 1
    while os.path.exists(f'resumo{j}.csv'):
        j += 1
    file = open(f'resumo{j}.csv', "w")

    
    #Quantidade = repr(Quantidade)
    #Custo = repr(Custo)
    #Procedimento = repr(Procedimento)
    Somatudo = repr(Somatudo)

    file.write("Quantidade\tCusto\tProcedimento\n")

    for i in range(len(Quantidade)):
        Quantidade[i] = repr(Quantidade[i])
        Custo[i] = repr(Custo[i])
        Procedimento[i] = repr(Procedimento[i])
        file.write(Quantidade[i] + "\t" + Custo[i] + "\t" + Procedimento[i] + "\n")
    
    file.write("Custo(s) Total(is):\tR$" + Somatudo)
    file.close

    print(f'Arquivo salvo como resumo{j}.csv')

def merge(list1, list2, list3):
 
    merged_list = tuple(zip(list1, list2, list3))
    return merged_list

import whisper
model = whisper.load_model("small")

import tkinter as tk
from tkinter import simpledialog



def transcricao(arquivo):
	result = model.transcribe(arquivo, language = 'Portuguese')
	texto = result["text"].upper()
	return texto

#texto = result["text"].replace(",", "")
#texto = texto.replace(".", "")
#texto = texto.upper()

import pandas as pd

df = pd.read_csv('tabela_consulta2.csv', sep=',')

df['Valor'] = df['Valor'].replace(',','',regex=True)
df['Valor'] = df['Valor'].replace('\.','',regex=True)
df['Valor'] = df['Valor'].str.extract('(\d+)', expand=False)


#for i in df['Valor']:
#  i.replace(".","")
df['Valor'] = df['Valor'].astype(float)/100

from time import sleep
import subprocess
from thefuzz import fuzz, process
from unidecode import unidecode
import os
directory = os.getcwd()
wav_files = []

for file_path in os.listdir(directory):
    # check if current file_path is a file
    if file_path.endswith('.wav'):
    #if os.path.isfile(os.path.join(files, file_path)):
        # add filename to list
        wav_files.append(file_path)
wav_files = sorted(wav_files, key=lambda t: -os.stat(t).st_mtime)
#print(wav_files)
#indexed_list = [f'{index}: {value}' for index, value in enumerate(wav_files)]
for index, value in enumerate(wav_files):
    print(f'{index}:\t{value}')
#print(indexed_list)
i = input('Escolha o(s) indice(s) do(s) arquivo(s) de áudio que você deseja: \nEx: 0 ou 0-4\n')
#print(wav_files[int(i)])
i = i.split("-")
if(len(i)>1):
    #print(f'{i[0]}~{i[1]}')
    i = range(int(i[0]), int(i[1])+1)

print('a')

print()
print()




quantidade = []
transcricoesProced = []

for j in i:
    #print(j)
    text5 = unidecode(transcricao(wav_files[int(j)]))
    
    x = text5.split()
    print(x)
    beginning_phrase = []
    remaining_phrase = []
    #i = 0
    valor = 0
    excluir = 0

    #for item in x:
    #    print(item)
    for word in x:
        if word == 'e':
            # Ignora a palavra 'e' e continua para a próxima
            continue
        try:
            # Tenta converter a palavra em um número
            number = word_to_num(word)
            # Se for um número, adiciona ao valor total
            valor += number
            excluir += 1
        except ValueError:
            # Se não for um número, interrompe a iteração
            break


    beginning_phrase.append(" ".join(x[:excluir]))
    remaining_phrase.append(" ".join(x[excluir:]))


    for item in beginning_phrase:
        if item == '':
            print('até aqui blz...')
            #print(f'Ocorreu um erro referente ao item "{x[a]}", reescreva-o corretamente:\n')
            x = " ".join(x)
            #input(f'Ocorreu um erro referente ao item "{x}", reescreva-o corretamente:\n(Pressione "Enter" para continuar)')
            print(f'Ocorreu um erro referente ao item "{x}", reescreva-o corretamente:\n(Pressione "Enter" para continuar)')
            correcao = edit_text_in_terminal(x)
            correcao = correcao.split()
            print(f"após correção: {x}")
    ###
            i = 0
            valor = 0
            excluir = 0

            while i < len(correcao):
                #
                current_word = correcao[i]
                next_word = ""

                if i < len(correcao) - 1:
                    next_word = correcao[i + 1]

                i += 1

                try:
                    if correcao[i-1] == 'e':
                        pass
                    elif word_to_num(current_word):
                        valor += word_to_num(current_word)
                        print(valor)
                    excluir+=1
                except ValueError:
                    break
            beginning_ajuste = " ".join(correcao[:excluir])
            #beginning_ajuste = valor
            #beginning_phrase.append(" ".join(item[:excluir]))
            remaining_ajuste = " ".join(correcao[excluir:])
            #remaining_ajuste = " ".join(correcao)
            print('~')
            print(f"palavras pra separar: {excluir}")
            print(f"parte numérica pós ajuste: {beginning_ajuste}")
            print(f"parte procedimento pós ajuste: {remaining_ajuste}")
            beginning_phrase = beginning_ajuste
            remaining_phrase = remaining_ajuste
            print(';)')
            #remaining_phrase.append(" ".join(item[excluir:]))

    print(f"beggining - {beginning_phrase}")
    print(f"remaining - {remaining_phrase}")

    if(isinstance(beginning_phrase, str)):
        print("V")
        pass
    else:
        print("F")
        beginning_phrase = " ".join(beginning_phrase)

    teste = word_to_num(beginning_phrase)
    print(teste)
    quantidade.append(teste)
    transcricoesProced.append(remaining_phrase)



print(quantidade)

#print(f"Verificação parte inicial: {beginning_phrase}")
print(f"Verificação parte final: {transcricoesProced}")



procedimento = []
custo = []



a=0
#esse "a" é pra acessar a posição no array transcricoesProced, pra procurar no csv cada valor do a-ésimo procedimento
for item in transcricoesProced:
  #procedimento.append(process.extractOne(transcricoesProced[a], df.loc[:,'Descricao'], scorer=fuzz.ratio)[0])
  possibilidades = process.extract("".join(item), df.loc[:,'Descricao'], scorer=fuzz.ratio, limit = 3)
  nomes_proced = [item[0] for item in possibilidades]
  #print(nomes_proced)
  print("miaau")
  
  ajuste = selecionar_procedimento(a, possibilidades, item)
  '''
  print(f"O {a+1}º procedimento citado corresponde à:\n")
  for j in range (3):
      print(f"{j}.\t{possibilidades[j][0]}")
  print("3.\tReescrever procedimento")
  ajuste = input()
  '''

  if ajuste == '0' or ajuste == '1' or ajuste == '2':
      #print(f"miaau\t{possibilidades[int(ajuste)][0]}\tauauau")
      procedimento.append(possibilidades[int(ajuste)][0])
      custo.append('{:.2f}'.format(df.loc[df.Descricao == procedimento[a], 'Valor'].item() * quantidade[a]))

      #print(f"u.u\tVerificação procedimentos: {procedimento}")
      #print(f"u.u\tVerificação custos: {custo}")

  #elif ajuste == "3":
  else:
      '''
      gambiarra = "".join(transcricoesProced[a])
      troca = edit_text_in_terminal(gambiarra)
      '''
      troca = ajuste
      procedimento.append(process.extractOne(troca, df.loc[:,'Descricao'], scorer=fuzz.ratio)[0])
      #procedimento[a] = process.extractOne(troca, df.loc[:,'Descricao'], scorer=fuzz.ratio)[0]
      custo.append('{:.2f}'.format(df.loc[df.Descricao == procedimento[a], 'Valor'].item() * quantidade[a]))
      #custo[a] = '{:.2f}'.format(df.loc[df.Descricao == procedimento[a], 'Valor'].item() * quantidade[a])
  
  a += 1
sleep(1)


print(f"Verificação procedimentos: {procedimento}")
print(f"Verificação custos: {custo}")



print()
print(quantidade)
print()
print(procedimento)
print()
print(custo)
print()
print()

for i in range(len(quantidade)):
    print(quantidade[i], '\t', custo[i], '\t\t', procedimento[i])
somatudo=0
for precos in custo:
    somatudo += float(precos)
somatudo = '{:.2f}'.format(somatudo)
print(f'total:\tR$ {somatudo}')
print()
save_variables(quantidade, custo, procedimento, somatudo)
print("=)")
print(merge(procedimento, quantidade, custo))
print("=)")
print("---------------------------------------------")
print()
print('Para executar mais operações, voltar à interface gráfica\nCaso queira encerrar a operação, feche a janela da interface gráfica ou pressione "Ctrl+C".')
