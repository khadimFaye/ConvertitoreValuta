import os
import sys
import random
import requests
import time
from requests.exceptions import ConnectionError

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel,MDIcon
from kivymd.uix.button import MDFlatButton,MDFillRoundFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDFadeSlideTransition
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty,NumericProperty
from kivymd.uix.tab import MDTabs,MDTabsBase
from kivymd.uix.list import TwoLineAvatarIconListItem,IconLeftWidget
from kivy.properties import Clock
from kivy.uix.widget import WidgetException
from typing import List,Union

from valutaFlex import ValutaFlex
conv = ValutaFlex()

# from kivymd.uix.list import Ic
class Tab1(MDFloatLayout,MDTabsBase):
    DEFAULT_CURRENCY_CODE0 = StringProperty('XOF')
    DEFAULT_CURRENCY_CODE1 = StringProperty('EUR')
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #crea un istnaza di CustumContent ()
        self.custum_content = CustomContent()
        #che la funzione che inizializza la lista delle valute 
        self.custum_content.init_currency_list()
       
    def init_lista_delle_valute(self,instance):
        
        '''
        SELETTORE DI VALUTA
        ----------------------
        QUESTA FUNZIONE PERMETTE DI VISUALIZZARE E SELEZIONARE LE VALUTE DISPONIBILI PER LA CONVERSIONE
           '''
        self.app = MDApp.get_running_app().root.get_screen('home') #accedi allo schermo currente
        self.app.current_instance.append(instance) #aggiungi\ l' istanza del bottone premouto alla lista [current_instance] in modo da individuare quale dei de campi [input1 input2 ] vuoi cambiare
        #questo blocco di codice crea un apre l'MDDialog che conterra le valute disponibili da selezionare
        try:

            self.dialog = MDDialog(
                title ='lista valute',
                type = 'custom',
                content_cls = self.custum_content,
                md_bg_color = (24/255,24/255,24/255))
        except WidgetException:
            pass
        
        def open_dialog():
            self.dialog.open()   
            # print(type(self.dialog))

        # time.sleep(0.3)
        open_dialog()

    def swap_currency(self):
        #scambia le valute selezionate
        self.ids.currency_code1.text,self.ids.currency_code0.text = (self.ids.currency_code0.text,self.ids.currency_code1.text)


    def convertoValue1_to_Value2(self,val):
        parent = val.parent # accedi all parent del input che contiene il valore che vogliamo convertire
        for i in parent.children:
            if isinstance(i,MDLabel)==True:
                #il valore da convertire : 
               
                SOURCE = val.text
                CURRENCY_TARGET = self.ids.val2

                #i codici di riferimento delle valute selezionate da convertire:
                currency_code0,currency_code1 = (i,self.ids.currency_code1)
                #il risultato della request manda al nostro API
                try:

                    RESULT = conv.converti(From=currency_code0.text,to=currency_code1.text,value=float(SOURCE))
                    if RESULT!=False:
                        #se la request è andata a buon fine
                        value =  str(round(float(RESULT[0]),2))
                        if len(value)>3:
                            CURRENCY_TARGET.text=f'{round(float(RESULT[0]),2):2,}'
                        else:
                            CURRENCY_TARGET.text=f'{round(float(RESULT[0]),2)}'
                except ValueError as e:
                    print(str(e))
                        
                  

class Tab2 (MDFloatLayout,MDTabsBase):
    #THE DEFAULT VALUE OF THE DISPLAY AND STC -->LIST TO SORE THE SUMM WE WANT TO  EVALUATE
    DEFAULT_VALUE = StringProperty('00')
    SUB_DSP = StringProperty('')
    SYMB = ['-','C','+/-','+','*','=','/','%']
    STC = []
    OP = []
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        '''
        TAB2 é LA CLASSE CHE USIAMO PER IMPLEMENTARE LA PARTE DELLA CALCOLATRICE
        '''

    def Evaluate(self,button):
        #ottieni lo screen corrente che e accecdi al display_label [che che é il label di cui verra assegnato i valori dei tasti premuti ] :
        #manda allo schermo il numero che contiene ogni tasto premuto implemetando la logica della calcolatrice
        CRS = MDApp.get_running_app().root.get_screen('home')
        display_label = CRS.ids.tab2.ids.display
        #se il dislay_label == 00 che é il valore di default oppure sui numeri inseriti cè gia il punto decimale (.)
        if display_label.text =='00' or display_label.text=='' and button.text in self.SYMB or '.' in display_label.text:
            #se il tasto premuto non é uguale al tasto decimale che si trova gia sui numeri inseriti
            if button.text not in self.SYMB:
                #aggiorna il display_label con i valori dei tasti premuti se é display_label = a 0 o = a 00
                if display_label.text =='0' or display_label.text=='00':
                    if button.text!='.':
                        display_label.text=button.text
                    else:
                        display_label.text+=button.text
                #altrimenti aggiugni i valori dei tasti al display_label a sequenze
                else:
                    if '.'  in display_label.text:
                        if button.text!='.':
                            display_label.text+=button.text
                    
            

       # se le condizioni del primo if non é soddisfatto ese gui questo blocco di codice
        else:
            if button.text not in self.SYMB:
                if display_label.text =='00':
                   if button.text!='.':
                    display_label.text=button.text
                else:
                    display_label.text+=button.text


        if display_label.text !='00' :#and button.text in ['+','-','*','/',]:
            if button.text == '+' or button.text=='-' or button.text=='*' or button.text =='/' and display_label.text!='00':
                try:

                    self.STC.append(''.join(display_label.text.split(button.text)).strip())
                    #estrare  l'operatore e spoastarlo nella lista dei operatore selezionati
                    #per tenere traccia le operazione aritmetiche
                    self.OP.append(button.text)
                    #sposta il primo valore inserito - nella lista - dei valori da sommare quando contengono [uno di questi  simbolo (+,*,/,-)]
                    self.SUB_DSP = f"{float(''.join(self.STC[-1]))} {''.join(self.OP[-1])}"
                    #azzera il display --> None ['']
                    display_label.text = ''
                except Exception as e:
                    pass

            #procediamo col il secondo valore che andremmo ad accoppiare con il primo valore salvato nella lista [STC]
        if display_label.text:
            NUMB2 = display_label.text # <--- eccolo qui [il valore che va sommato con il primo ]
            #se il pulsante [=] é premuto - assicura che [display_label non é None] e controlla se OP [la lista che contiene gli operatori]
            # contiene l'operatore che desideri in questo caso é [+]
            if display_label.text!='':
                if button.text =='=' and self.OP:
                    if display_label.text!='' and ''.join(self.OP[-1]) == '+':

                        def SUM():
                            #creazione di due oggetti di tipo float()  [A,B] e avranno come valori [il primo valore e il secondo valore che utente inserisce ]
                            #aggiugni B nella lista STC
                            A = float(''.join(self.STC[-1]))
                            B = float(''.join(NUMB2.split(button.text)))

                            self.STC.append(str(B))
                            #aggiorno il sub_display label [SUB_DSP]
                            self.SUB_DSP += f" {''.join(self.STC[-1])} {button.text}"
                            #e per finire l'operazione sommiamo i valori
                            somma  = round(A+B,2)
                            print(A,B,self.STC)
                            display_label.text = ''
                            display_label.text = str(somma)

                        SUM()
                    if display_label.text!='' and ''.join(self.OP[-1]) == '-':

                        def SOTRAZIONE():
                            #creazione di due oggetti di tipo float()  [A,B] e avranno come valori [il primo valore e il secondo valore che utente inserisce ]
                            #aggiugni B nella lista STC
                            A = float(''.join(self.STC[-1]))
                            B = float(''.join(NUMB2.split(button.text)))

                            self.STC.append(str(B))
                            #aggiorno il sub_display label [SUB_DSP]
                            self.SUB_DSP += f" {''.join(self.STC[-1])} {button.text}"
                            #e per finire l'operazione sommiamo i valori
                            somma  = round(A-B,2)
                            print(A,B,self.STC)
                            display_label.text = ''
                            display_label.text = str(somma)

                        SOTRAZIONE()

                    if display_label.text!='' and ''.join(self.OP[-1]) == '*':

                        def MULTIPLICAZIONE():
                            #creazione di due oggetti di tipo float()  [A,B] e avranno come valori [il primo valore e il secondo valore che utente inserisce ]
                            #aggiugni B nella lista STC
                            A = float(''.join(self.STC[-1]))
                            B = float(''.join(NUMB2.split(button.text)))

                            self.STC.append(str(B))
                            #aggiorno il sub_display label [SUB_DSP]
                            self.SUB_DSP += f" {''.join(self.STC[-1])} {button.text}"
                            #e per finire l'operazione sommiamo i valori
                            somma  = round(A*B,2)
                            print(A,B,self.STC)
                            display_label.text = ''
                            display_label.text = str(somma)

                        MULTIPLICAZIONE()

                    if display_label.text!='' and ''.join(self.OP[-1]) == '/':

                        def DIVISIONE():
                            #creazione di due oggetti di tipo float()  [A,B] e avranno come valori [il primo valore e il secondo valore che utente inserisce ]
                            #aggiugni B nella lista STC
                            A = float(''.join(self.STC[-1]))
                            B = float(''.join(NUMB2.split(button.text)))

                            self.STC.append(str(B))
                            #aggiorno il sub_display label [SUB_DSP]
                            self.SUB_DSP += f" {''.join(self.STC[-1])} {button.text}"
                            #e per finire l'operazione sommiamo i valori
                            somma  = round(A/B,2)
                            print(A,B,self.STC)
                            display_label.text = ''
                            display_label.text = str(somma)

                        DIVISIONE()

                #cancellare i numri inseriri con il tasto [C]
        if display_label.text!='' or display_label.text!='00':
            if button.text == 'C':
                if display_label.text is not None and display_label.text!='00':
                    print('not nunnnnn')

                    STACK = list(display_label.text)
                    if STACK!=[]:
                        STACK.remove(STACK[-1])
                        display_label.text = ''.join(STACK)
                        self.SUB_DSP = ''
                    else:
                        display_label.text = self.DEFAULT_VALUE
                        

class Home(MDScreen):
    current_instance = []
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        grid = self.ids.tab1.ids.tst
        
            
        for i in range(1,10):

            buttons = MDFlatButton(
                text = str(i),
                theme_text_color = 'Custom',
                text_color = 'white',
                md_bg_color = (24/255,24/255,24/255, 0.75),size_hint = (1,1),
                on_press = lambda x:self.Type(x)
                )
            grid.add_widget(buttons)

        # AGGIUGNI I BOTTONI  RESTANTI [0] [.] [DELET BUTTON ]
        zero = MDFlatButton(
                text = str(0),
                theme_text_color = 'Custom',
                text_color = 'white',
                md_bg_color = (24/255,24/255,24/255, 0.75),size_hint = (1,1),
                on_press = lambda x:self.Type(x)
                )

        punto = MDFlatButton(
                text = str('.'),
                theme_text_color = 'Custom',
                text_color = 'white',
                md_bg_color = (24/255,24/255,24/255, 0.75),size_hint = (1,1),
                height = 250,
                on_press = lambda x:self.Type(x)
                )
        Del_Button = MDFlatButton(
                text = str('C'),
                theme_text_color = 'Custom',
                text_color = 'white',
                md_bg_color = (24/255,24/255,24/255, 0.75),size_hint = (1,1),
                height = 250,
                on_press = lambda x: self.Type(x))
        grid.add_widget(zero)
        grid.add_widget(punto)
        grid.add_widget(Del_Button)
        # call_func = CustomContent()
        # call_func.init_currency_list()


    def Type(self,instance):
        print(self.ids.tab1.ids.val1.text)
        if instance.text == '.' and self.ids.tab1.ids.val1.text =='0' or '.' in self.ids.tab1.ids.val1.text:
            if instance.text!='.':
                self.ids.tab1.ids.val1.text+=instance.text
        else:
            if self.ids.tab1.ids.val1.text =='0':
                self.ids.tab1.ids.val1.text = instance.text
            else:
                self.ids.tab1.ids.val1.text+=instance.text



        if instance.text =='C' :
            if self.ids.tab1.ids.val1.text!='':
                self.ids.tab1.ids.val1.text = ''.join(self.ids.tab1.ids.val1.text.split(str(self.ids.tab1.ids.val1.text[-1])))
        print('hai premuto :',instance.text)


#CUSTOM CONTENT CLASS  :
class CustomContent(MDBoxLayout):
    prv_value = []
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
       
    def init_currency_list(self):
        
        currency_container = self.ids.currency_container
        try:

            CURRENCIES = conv.GET_CURRNCIES()
            for CODE,currency_name in CURRENCIES.items():
                card = MDCard(
                    size_hint = (1,None),
                    height = 60)

                rl = MDRelativeLayout(
                    size_hint_y = None,
                    height=60,pos_hint = {'center_x':.5,'center_y':.5})
                    
                item = TwoLineAvatarIconListItem(
                    text = str(CODE),
                    secondary_text = str(currency_name),
                    ripple_alpha = .1,
                    on_press = lambda x: self.CambiaValuta(x))
                    
                icon = IconLeftWidget(
                    icon="currency-usd")

                item.add_widget(icon)
                rl.add_widget(item)
                card.add_widget(rl)
                if card.parent:
                    pass
                else:
                    currency_container.add_widget(card)
            print(CURRENCIES.items(),'visto')
        except AttributeError as e :
            currency_container.add_widget(MDIcon(
                icon = 'alert.circle',
                font_size = 20,
                theme_text_color ='Error')
                )
        except WidgetException as e :
            pass


    def CambiaValuta(self,currency_code:str):
        '''
        CHIAMANADO QUESTA FUNZIONE CAMBI LA VALUTA SELEZIONATA
        --------------------------------------------------------------------------
        currency_code : il riffremiento della valuta selezionata dalla lista\n

        currency_code_label0 : [é IL WIDGET (MDLabel) che contiene l'indice della valuta sorgente che sta sopra]\n
        currency_code_label2  : [é IL WIDGET (MDLabel) che contiene l'indice della valuta di destinataria che sta sotto]\n
        
        '''
        try:
          
            k = MDApp.get_running_app().root.get_screen('home')
            # print(k.current_instance[-1])
            currency_code_label0 = [child for child in k.current_instance[-1].parent.children if isinstance(child,MDLabel)]
            currency_code_label1= [child2 for child2 in k.ids.tab1.ids.val2.parent.children if isinstance(child2,MDLabel)]
            self.prv_value.append(currency_code_label0[-1].text)
            currency_code_label0[-1].text = currency_code.text # > change the value
            #chiudi dialog
            dialog = self.parent.parent.parent
            dialog.dismiss()

        except IndexError as e:
          pass



# crea una class che eridita MDtextfiled per un campo input personlizzato
class Value1_Input_Field(MDTextField):
    '''

    VALUE1 --> [FLOAT > STR ]
    -----------------------------
    value1 é il Numeric property che passiamo il valore del\'input per
    poi trasformarlo in un float per poi di nuovo convertirlo in str()
    '''
    Value1 = StringProperty('0')
    alfa = ['a','b','c','d','e','f','j','h','i','g','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','ç','@','#']
    Num = [i for i in range(10)]
    print(Num)
    # print(f'{1000:,}'.replace(',','.'))
    # x = 1.0
    # print(int(x))

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    def on_focus(self, instance_text_field, focus: bool) -> None:
        try:
            #CONVERTI IL VOLORE DELL'INPUT SORGENTE IN FLOAT()
            #SE CONTIENE UN VALUE é PIU O MENO LUNGO 2 CHIFRE
            #SE LINPUT é VUOTO AZZERA IL CAMPO
            if self.text!='' :
                if len(self.text)!=1 and '.' not in self.text:

                    self.text = f'{float(self.text):2,}'
                else:
                    self.text = self.text
            else:
                self.text = self.Value1
        except ValueError as e :
            print(str(e))

class Value2_Input_Field(MDTextField):
    '''

    VALUE2 --> [FLOAT > STR ]
    -----------------------------
    value1 é il Numeric property che passiamo il valore del\'input per
    poi trasformarlo in un float per poi di nuovo convertirlo in str()
    '''
    Value2 = StringProperty('0')
    Num = [i for i in range(10)]
    print(Num)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    def on_focus(self, instance_text_field, focus: bool) -> None:
       if self.text =='' :
            self.text = self.Value2


class SplashScreen(MDScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #set il timeout della transizione 
        self.set_timeout(self.Transition)
    #questa funzione viene chiamata quando la connesione é assente 
    #per riprovare 
    def Retry(self,func):
        self.ids.spinner.active=1
        self.set_timeout(func)

    def set_timeout(self,func): 
        #imposta una durata causuale che lo screeniniziale deve aspettare prima di transitare all home screen
        #inizializza un oggetto che sceglie causualmnete  i valori elencati
        timeout = random.choice([6.0,7.0,4.0,3.5]) 
        def call_func(func):
            # chiama la funzione che che gestisce la transizione allo scadere del tempo impostato
            Clock.schedule_once(func,timeout) 
        return call_func(func)

    def Transition(self,*ags):
        

        try:
            #verifica se la connesione tra il prgramma  e l'api é stabile per permettere un request
            if conv.IMPOSTA_VALUTE()['STATUS']==False:
                self.ids.error.text = 'connessione assente'
                self.ids.alert.text_color = 'white'
                self.ids.spinner.active=0
                self.ids.Retry_button.text = 'Riprova'
            else:
                # puoi transitare e passare allo schermo principale
                self.manager.current='home'
        except Exception as e:
            print(str(e))

class MyApp(MDApp):
    def build(self):

        Window.size = (360,640)
        self.title = 'Convertitore Valuta'
        self.icon = 'home'
        self.theme_cls.material_style = 'M3'
        # Window.bind(on_resize = self.resize)
        Builder.load_file('Splash.kv')
        Builder.load_file('kv_file.kv')
        sm = MDScreenManager(transition=MDFadeSlideTransition())
        sm.add_widget(SplashScreen(name='Splash'))
        sm.add_widget(Home(name='home'))
        return sm
    def resize(self,instance,width,height):
        max_width,max_height = (360,800)
        if width < max_width or height < max_height:
            Window.size = (max(width,max_width),max(height,max_height))
    def on_start(self):
        pass
		

if __name__ == '__main__':
    MyApp().run()