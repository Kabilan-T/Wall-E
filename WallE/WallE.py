import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

from WallE.bingo import Bingo
from WallE.guessnumber import Guess_number
from WallE.handtoss import Stone_Paper_Scissors

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
        self.GuessNumber = Guess_number()
        GuessNumber_handler = ConversationHandler(
            entry_points=[CommandHandler('guessnumber', self.GuessNumber.Start)],
            states={
                SET: [MessageHandler(Filters.regex('^[0-9]*$'), self.GuessNumber.SetMax)],
                USERMOVE: [MessageHandler(Filters.regex('^[0-9]*$'), self.GuessNumber.UserGuess)]},
            fallbacks=[CommandHandler('exit', self.GuessNumber.Exit)],
            allow_reentry= True)
        self.dispatcher.add_handler(GuessNumber_handler)
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
  




