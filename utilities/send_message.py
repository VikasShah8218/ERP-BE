from telegram import Bot

async def send_message(chat_id:list,message:str="Default Message"):
    bot = Bot(token='7318029936:AAG-mJ43TaJzPWCH_9spAKCVnRyDljvOLPE')
    print("Starting message to be sent ")
    if len(chat_id) > 0:
        error={}
        for i in chat_id:
            try:
                await bot.send_message(chat_id=i, text=message)
                print("Send MEssage Run")
            except Exception as e:
                error[i] = str(e)
        print(error) if len(error)>0 else None 

