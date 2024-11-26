import tkinter as tk
import tkinter.font as tkFont
import speech_recognition as sr
import threading
import sys
import os
from PIL import Image, ImageTk
import subprocess

# Função para abrir a primeira janela
def abrir_janela1():
    janela1 = tk.Toplevel()
    janela1.title("Aplicação de Faturamento")
    janela1.configure(bg="#083f76")
    label = tk.Label(janela1, text="Instruções", font=("Arial", 14),bg="#083f76",fg="white")
    label.pack()
    message = tk.Message(janela1, text="""Grave áqudios no padrão:\n
                         [Quantidade] + [Procedimento]\n
                         para o que for realizado.\n
                         Finalizadas as gravações, feche a janela do gravador e execute as operações no terminal.
                         """,bg="#083f76",fg="white")
    message.pack(padx=20, pady=20)
    janela1.geometry("600x350+100+100")
    label_imagem = tk.Label(janela1, image=imagem_tk,borderwidth=0, highlightthickness=0)
    label_imagem.place(x=0, y=0)
    ####subprocess.run(['python3', 'speech-justino2.py'])
    os.system('python3 onlyrecorderold.py')
    
    os.system('python3 faturamentoGUI.py')
    
    janela1.destroy()
    janela1.update()



# Função para abrir a segunda janela
def abrir_janela2():
    janela2 = tk.Toplevel()
    janela2.title("Faturamento")
    janela2.configure(bg="#083f76")
    label = tk.Label(janela2, text="Instruções", font=("Arial", 14),bg="#083f76",fg="white")
    label.pack()
    message = tk.Message(janela2, text="teste",bg="#083f76",fg="white")
    message.pack(padx=20, pady=20)
    janela2.geometry("600x350+120+120")
    # Criar um widget Label para exibir a imagem
    label_imagem = tk.Label(janela2, image=imagem_tk,borderwidth=0, highlightthickness=0)
    label_imagem.place(x=0, y=0)
    os.system('python3 onlyrecorderold.py')

    os.system('python3 LaudoColposcopia.py')
    
    janela2.destroy()
    janela2.update()

# Função para abrir a 3 janela
def abrir_janela3():
    # Criação da janela principal
    janela = tk.Toplevel()
    janela.title("Exemplo de Texto")

    janela.configure(bg="#083f76")

    # Definindo a geometria da janela (largura x altura + posição x + posição y)
    janela.geometry("1200x300+850+250")  # Altera aqui a posição para onde deseja abrir

    # Criar um widget Label para exibir a imagem
    label_imagem = tk.Label(janela, image=imagem_tk,borderwidth=0, highlightthickness=0)
    label_imagem.place(x=20, y=20)

    # Criação de uma fonte personalizada
    fonte_personalizada = tkFont.Font(family="Arial", size=16)  # Tamanho da fonte 16



    # Criação do widget Text
    #texto = tk.Text(janela, height=12, width=180)
    texto = tk.Text(janela, height=12, width=100, font=fonte_personalizada, bg="#083f76",fg="white", borderwidth=0, highlightthickness=0)
    texto.pack(padx=250, pady=20)
    texto.place(x=250, y=20)

    # Adicionando o texto ao widget Text
    texto.insert(tk.END, """Para registrar um áudio, pressione o botão "Começar Gravação".

Finalizada a citação, pressione o botão "Parar Gravação".

Na janela "Salvar como", escreva um nome para o arquivo de áudio conforme instruido no email.


OBS: caso hajam problemas na gravação, o botão "Cancel" irá descartar o áudio iniciado""")
    
    # Desabilitando o widget Text para novas entradas
    texto.config(state=tk.DISABLED)

    # Iniciando o loop principal
    #janela.mainloop()
    '''
    janela3 = tk.Toplevel()
    janela3.title("O que é isso aqui?")
    janela3.configure(bg="#083f76")
    label = tk.Label(janela3, text="Paraleloooooooooooooooo", font=("Arial", 14),bg="#083f76",fg="white")
    label.pack()
    message = tk.Label(janela3, text="janela pra testar abrir junto à inicial",bg="#083f76",fg="white")
    message.pack(padx=20, pady=20)
    janela3.geometry("600x350+900+140")
    # Criar um widget Label para exibir a imagem
    label_imagem = tk.Label(janela3, image=imagem_tk,borderwidth=0, highlightthickness=0)
    label_imagem.place(x=0, y=0)
    '''
    #os.system('python3 onlywhisper.py')
    os.system('python3 aplicacaoWeb.py')
    
    janela.destroy()
    janela.update()





# Função para reconhecimento de voz
def reconhecer_comando():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8  # O valor padrão é 0.8, reduza para um valor menor
    """non_speaking_duration: Define a duração do silêncio necessário antes de começar a escutar.
    Diminuir esse valor pode iniciar a captação mais rapidamente."""
    recognizer.non_speaking_duration = 0.5  # O valor padrão é 0.5
    
    with sr.Microphone() as source:
        interrupcao = False
        stringEntrada = ""
        #while stringEntrada.upper() != "SAIR":
        while True:
            if interrupcao == False:
                if(stringEntrada.upper() == "SAIR"):
                    #sys.exit()
                    root.destroy()
                    break
                print("Aguardando comando...")
                #audio = recognizer.listen(source)
                
                audio = recognizer.listen(source, phrase_time_limit=8)  # Adiciona timeout e tempo limite
                try:
                    stringEntrada = recognizer.recognize_google(audio, language='pt-BR')
                    print(f"Você disse: {stringEntrada}")
                    if stringEntrada.lower() == "código de faturamento":
                        abrir_janela1()
                    elif stringEntrada.lower() == "preenchimento de pdf":
                        abrir_janela2()
                    elif stringEntrada.lower() == "preenchimento web":
                        abrir_janela3()
                    else:
                        print("Comando não reconhecido.")
                except sr.UnknownValueError:
                    print("Não entendi o comando.")
                except sr.RequestError:
                    print("Erro ao se comunicar com o serviço de reconhecimento de voz.")

# Função para iniciar o reconhecimento de voz em uma thread separada
def iniciar_reconhecimento():
    thread = threading.Thread(target=reconhecer_comando)
    thread.daemon = True
    thread.start()

# Criar a janela principal
root = tk.Tk()
root.title("Aplicação com Comandos de Voz")
root.configure(bg="#083f76")
label = tk.Label(root, text="Aplicações do Fala-Texto", font=("Arial", 14),bg="#083f76",fg="white")
label.pack()
message = tk.Message(root, text='* "Código de Faturamento"\n\n* "Preenchimento de PDF"\n\n* "Preenchimento web"',bg="#083f76",fg="white")
message.pack(padx=20, pady=20)
message2 = tk.Label(root, text="Instrução: Fale a aplicação que você deseja trabalhar \n",bg="#083f76",fg="white")
message2.pack(padx=50, pady=80)
root.geometry("700x400+100+100")

# Carregar a imagem usando PIL
#imagem = Image.open(r"C:\Users\lapsi\Pictures\Screenshots\Projeto (4).png")
imagem = Image.open("Projeto (4).png")
imagem_tk = ImageTk.PhotoImage(imagem)

# Criar um widget Label para exibir a imagem
label_imagem = tk.Label(root, image=imagem_tk,borderwidth=0, highlightthickness=0)
label_imagem.place(x=0, y=0)

# Pelo que testei, não difere colocar antes ou depois do "iniciar reconhecimento".
#abrir_janela3()

# Iniciar o reconhecimento de voz automaticamente
iniciar_reconhecimento()


root.mainloop()
