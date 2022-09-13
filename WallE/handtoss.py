import logging
from random import choice
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

CHART, MANUALCHART, MODE, COMMOVE, USERMOVE, SET = range(6)

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