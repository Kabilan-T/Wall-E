import logging
from random import sample, shuffle, randint, choice
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#state declarations
CHART, MANUALCHART, MODE, COMMOVE, USERMOVE, SET = range(6)

class MyBot ():
    '''Class for all sub programs of the bot''' 
    def __init__(self,token,name):
        '''Initialization'''
        self.name=name
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.MyBingo = Bingo(self.name)
        Bingo_handler = ConversationHandler(
            entry_points=[CommandHandler('bingo', self.MyBingo.Start)],
            states={
                CHART: [MessageHandler(Filters.regex('^(Yes|No)$'), self.MyBingo.CreateChart)],
                MANUALCHART : [MessageHandler(Filters.regex('^[0-9]*$'), self.MyBingo.ManualChart)],
                MODE: [MessageHandler(Filters.regex('^(First|Second)$'), self.MyBingo.SelectMode)],
                USERMOVE: [MessageHandler(Filters.regex('^[0-9]*$'), self.MyBingo.UserMove)]},
            fallbacks=[CommandHandler('exit', self.MyBingo.Exit)],
            allow_reentry= True)
        self.dispatcher.add_handler(Bingo_handler)
        self.SPS = Stone_Paper_Scissors()
        SPS_handler = ConversationHandler(
            entry_points=[CommandHandler('handtoss', self.SPS.Start)],
            states={
                USERMOVE: [MessageHandler(Filters.regex('^(Stone|Paper|Scissors)*$'), self.SPS.Result)]},
            fallbacks=[CommandHandler('exit', self.SPS.Exit)],
            allow_reentry= True)
        self.dispatcher.add_handler(SPS_handler)
        self.updater.start_polling()
        self.updater.idle()
       
    def start(self, update, context):
        '''Start Command'''
        logging.info(update.effective_chat.first_name+" have started the Bot")
        context.bot.send_message(update.effective_chat.id,"Hi "+update.effective_chat.first_name+", I'm "+self.name+" How may i help you?")
        self.help(update,context)

    def unknown(self,update, context):
        '''Unknown Command reply'''
        logging.info(update.effective_chat.first_name+" have given a unknown command")
        context.bot.send_message(update.effective_chat.id,"Sorry, I didn't understand that command.")

    def help(self, update, context):
        '''command to send the user list of all active commands'''
        logging.info(update.effective_chat.first_name+" have used help command")
        text="You can control me by sending following commands\n"
        command = []
        for handlers in self.dispatcher.handlers[0]: 
            if isinstance(handlers, CommandHandler):
                command.append(handlers.command)
            if isinstance(handlers, ConversationHandler):
                for subhandlers in handlers.entry_points :
                    command.append(subhandlers.command)
        for i in command : text+="/"+i[0]+"\n"
        context.bot.send_message(update.effective_chat.id,text)
  
class Bingo ():
    '''Class for Bingo Functions'''
    def __init__(self,name):
        '''Bingo Class Initilize'''
        self.name=name

    def Start(self, update, context):
        '''Bingo starts'''
        logging.info(update.effective_chat.first_name+" have started the Bingo game")
        self.score="Nil"
        context.bot.send_message(chat_id=update.effective_chat.id,text="Welcome to BINGO\n if you want to exit anytime send /exit")
        update.message.reply_text('Do you want auto Generated the chart?\nYes or No',reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
        return CHART

    def CreateChart(self, update, context):
        '''Chart creation auto or manual call function'''
        self.Computer = self.GernerateChart()
        AutoChart = update.message.text
        if AutoChart == 'Yes':  
            self.Player = self.GernerateChart()
            return self.AskMode(update,context)
        elif AutoChart == 'No': 
            self.Player=[]
            self.Row = 0
            self.Col = 0
            self.sub = []
            self.numboard = [[i*5+j for i in range (0,5)] for j in range (1,6)]
            EntryChart = [[str(i) if i!=0 else 'X' for i in j] for j in self.numboard]
            update.message.reply_text('Enter number for '+str(self.Row+1)+','+str(self.Col+1)+' position:',reply_markup=ReplyKeyboardMarkup(EntryChart, one_time_keyboard=True, resize_keyboard=True))            
            return MANUALCHART

    def ManualChart(self, update, context):
        '''User Entry Chart'''
        element = int(update.message.text)
        if self.Col < 5:
            self.sub.append(element)
            self.Col+=1
            if self.Col==5 and self.Row < 5:
                self.Player.append(self.sub)
                self.sub=[]
                self.Col=0
                self.Row+=1
        if self.Row==5 :
            return self.AskMode(update,context)
        else:
            self.StrikeValue(self.numboard,element)
            EntryChart = [[str(i) if i!=0 else 'X' for i in j] for j in self.numboard]
            update.message.reply_text('Enter number for '+str(self.Row+1)+','+str(self.Col+1)+' position:',reply_markup=ReplyKeyboardMarkup(EntryChart, one_time_keyboard=True, resize_keyboard=True))
            return MANUALCHART

    def AskMode(self, update, context):
        '''Ask the user for first or second player'''
        self.ChartDisplay(update, context, self.Player)
        update.message.reply_text('First player or Second player ',reply_markup=ReplyKeyboardMarkup([['First', 'Second']], one_time_keyboard=True))
        return MODE

    def ChartDisplay(self, update, context, Matrix):
        '''Display the chart to the user'''
        chart =""
        for i in Matrix : 
            for j in i: 
                if j > 9 : chart+='-'+str(j)+'-\t\t\t\t'
                elif j==0 : chart+='xxxx'+'\t\t\t\t'
                else : chart+='-0'+str(j)+'-\t\t\t\t'
            chart+='\n'
        context.bot.send_message(update.effective_chat.id,chart)
        
    def SelectMode(self, update, context):
        '''Player mode selection'''
        selectedmode = update.message.text
        if (selectedmode=='First') :
            self.UserKeyboard(update, context)
            return USERMOVE
        if (selectedmode=='Second') :
            return self.ComMove(update, context)

    def ComMove(self,update, context):
        '''Com Strike move'''
        t = self.GernerateStrikeNum(self.Computer)
        context.bot.send_message(update.effective_chat.id,self.name+" choose "+str(t))
        self.StrikeValue(self.Computer,t)
        self.StrikeValue(self.Player,t)
        if self.Score(update, context) in ["WIN","LOSE"]:
            context.bot.send_message(update.effective_chat.id,update.effective_chat.first_name+" Chart :")
            self.ChartDisplay(update, context, self.Player)
            context.bot.send_message(update.effective_chat.id,self.name+" Chart :")
            self.ChartDisplay(update, context, self.Computer)
            return self.Exit(update, context)
        else:
            self.UserKeyboard(update, context)
            return USERMOVE

    def UserMove(self, update, context):
        '''User Strike move and calls com'''
        t = int(update.message.text)
        self.StrikeValue(self.Computer,t)
        self.StrikeValue(self.Player,t)
        if self.Score(update, context) in ["WIN","LOSE"]:
            context.bot.send_message(update.effective_chat.id,update.effective_chat.first_name+" Chart :")
            self.ChartDisplay(update, context, self.Player)
            context.bot.send_message(update.effective_chat.id,self.name+" Chart :")
            self.ChartDisplay(update, context, self.Computer)
            return self.Exit(update, context)
        else: 
            next = self.ComMove(update, context)
            return next

    def UserKeyboard(self, update, context):
        '''User Keboard Markup as Bingo chart'''
        PlayerChart = [[str(i) if i!=0 else 'X' for i in j] for j in self.Player]
        update.message.reply_text('Enter your number :',reply_markup=ReplyKeyboardMarkup(PlayerChart, one_time_keyboard=True, resize_keyboard=True))

    def Score(self, update, context):
        '''Send Score and check if Win'''
        ComScore= self.CheckStrike(self.Computer)
        UserScore = self.CheckStrike(self.Player)
        Bingo = "BINGO"
        score=''
        if ComScore>0 : score+=self.name+' : '+Bingo[:ComScore]+'\t\t\t'
        if UserScore>0 : score+=update.effective_chat.first_name+' : '+Bingo[:UserScore]
        if score != '' and score != self.score: 
            context.bot.send_message(update.effective_chat.id, score)
            self.score=score
        if UserScore>=5:
            context.bot.send_message(update.effective_chat.id,"Congrats "+update.effective_chat.first_name+"! you have won")
            return "WIN"
        elif ComScore>=5:
            context.bot.send_message(update.effective_chat.id,"Sorry "+self.name+" beats you")
            return "LOSE"
        else :
            return "Continue"
 
    def Exit(self,update, context):
        '''Bingo Game Exit handler'''
        logging.info(update.effective_chat.first_name+" have exited Bingo Game")
        try:
            del self.MyBingo
            del self.Player
            del self.Computer
            del self.score
            del self.numboard
            del self.Col
            del self.Row
            del self.sub
        except:
            pass
        update.message.reply_text('Bye! send /Bingo to play again.',reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def GernerateChart(self):
        '''Random chart generation'''
        C = []
        V = [i for i in range (1,26,1)]
        shuffle(V)
        for i in range(0,5):
            C.append(sample(V,5))
            for j in C[i]:
                V.remove(j)
        return C

    def GernerateStrikeNum(self,C):
        '''To Choose Wise number'''
        count=0
        t=[]
        m=[]
        m=[C[m][m] for m in range(0,5)]
        n=m.count(0)
        if n>count and n<5 :
            count=n
            t=m.copy()
        m=[C[m][4-m] for m in range(0,5)]
        n=m.count(0)
        if n>count and n<5 :
            count=n
            t=m.copy()
        for i in range(0,5):
            m=C[i]
            n=m.count(0)
            if n>count and n<5 :
                count=n
                t=m.copy()
        for i in range(0,5) :
            m=[x[i] for x in C]
            n=m.count(0)
            if n>count and n<5 :
                count=n
                t=m.copy()
        if count ==0:
            num = C[2][2]
        else :
            num = choice([x for x in t if x!=0])
        return num

    def StrikeValue(self,S=[],val=0):
        '''Remove the value from its position'''
        t=[e for x in S for e in x].index(val)
        S[t//5][t%5]=0

    def CheckStrike(self,C=[]):
        '''calculates number of Strike'''
        strike=[0,0,0,0,0]
        count=0
        for i in range(0,5):
            if C[i]==strike :
                count+=1
        for i in range(0,5) :
            if [x[i] for x in C]==strike :
                count+=1
        if [C[m][m] for m in range(0,5)] == strike:
            count+=1
        if [C[m][4-m] for m in range(0,5)] == strike:
            count+=1
        return count    

class Stone_Paper_Scissors ():
    '''class for Stone_Paper_Scissors Function'''
    def __init__(self):
        '''SPS Class Initilize'''
        self.keyboard=[["Stone"],["Paper"],["Scissors"]]

    def Start(self,update, context):
        '''Request User move'''
        self.ComDecision = choice(["Stone","Paper","Scissors"])
        logging.info(update.effective_chat.first_name+" have started Stone-Pepper-Scissor")
        update.message.reply_text('Choose your move',reply_markup=ReplyKeyboardMarkup(self.keyboard, one_time_keyboard=True))
        return USERMOVE

    def Result(self,update, context):
        '''Computer choose and result'''
        self.UserDecision = update.message.text
        Result = self.logic(self.UserDecision,self.ComDecision)
        text=''
        if Result == 0 :  text = "Both Choose "+self.UserDecision+"\nDraw"
        elif Result == 1 :text = self.UserDecision+" beats "+self.ComDecision+"\nYou Win"
        elif Result == 2 :text = self.ComDecision+" beats "+self.UserDecision+"\nYou Lose"
        context.bot.send_message(update.effective_chat.id,text)
        return self.Exit(update, context)

    def logic(self,D1,D2):
        '''Stone Paper Scissors Logic'''
        if (D1==D2): return 0
        elif D1 == "Stone":
            if D2 == "Scissors": return 1
            if D2 == "Paper":return 2
        elif D1 == "Paper":
            if D2 == "Stone": return 1
            if D2 == "Scissors":return 2
        elif D1 == "Scissors":
            if D2 == "Paper": return 1
            if D2 == "Scissors":return 2

    def Exit(self,update, context):
        '''SPS Game Exit handler'''
        logging.info(update.effective_chat.first_name+" have exited StonePepperScissor")
        try:
            del self.UserDecision
            del self.ComDecision
        except:
            pass
        update.message.reply_text('Bye! send /Handtoss to play again.',reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

BotToken = '1355378842:AAEORuP1CJG4TntxGGUDP4lMEXj9-_NkwTc'
BotName = "Heisenberg"
Heisenberg=MyBot(token= BotToken,name= BotName)
