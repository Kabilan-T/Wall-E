import logging
from random import  randint
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

CHART, MANUALCHART, MODE, COMMOVE, USERMOVE, SET = range(6)

class Guess_number ():
    '''Class for Guess number functions'''
    def __init__(self):
        '''Guess number Class Initilize'''
        self.MaxOptions = [["10"],["100"],["1000"],["10000"]]

    def Start(self,update, context):
        '''Request uset to set maximum number'''
        logging.info(update.effective_chat.first_name+" have entered GuessNumber")
        self.RandomNumber = 0
        self.UserAttempt = 0
        self.RandMax = 0
        update.message.reply_text("Hi "+update.effective_chat.first_name+", set a range to choose",reply_markup=ReplyKeyboardMarkup(self.MaxOptions, one_time_keyboard=True))
        return SET

    def SetMax(self,update, context):
        '''Set maximum number and Generate random number'''
        self.RandMax = int(update.message.text)
        self.RandomNumber = randint(1,self.RandMax)
        logging.info(update.effective_chat.first_name+" choose "+str(self.RandMax)+" as maximum number")
        logging.info("Random number is "+str(self.RandomNumber))
        update.message.reply_text("Ok! I have choosed a number")
        update.message.reply_text("Guess what it is?")
        return USERMOVE

    def UserGuess(self,update, context):
        '''Checks user's guess and proceed'''
        self.Guess = int(update.message.text)
        logging.info(update.effective_chat.first_name+" Guessed "+str(self.Guess))
        self.UserAttempt += 1
        if (self.Guess > self.RandMax):
            update.message.reply_text("You're guessing out of range. Guess below "+str(self.RandMax))
            return USERMOVE
        elif (self.Guess > self.RandomNumber):
            update.message.reply_text("Guess lower !")
            return USERMOVE
        elif (self.Guess < self.RandomNumber):
            update.message.reply_text("Guess higher !")
            return USERMOVE
        elif (self.Guess == self.RandomNumber):
            update.message.reply_text("Hoorey your Guess is correct !")
            update.message.reply_text("You took "+str(self.UserAttempt)+" attempts")
            logging.info(update.effective_chat.first_name+" Guessed correct with "+str(self.UserAttempt)+" attempts")
            return self.Exit(update, context)

    def Exit(self,update, context):
        '''Guess number Exit handler'''
        logging.info(update.effective_chat.first_name+" have exited GuessNumber")
        update.message.reply_text("The number is "+str(self.RandomNumber))
        try:
            del self.RandomNumber
            del self.UserAttempt
            del self.RandMax
        except:
            pass
        update.message.reply_text('Bye! send /guessnumber to play again.',reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END