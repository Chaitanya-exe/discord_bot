from typing import Final
from discord import Client, Intents, Message, utils
from asyncio import current_task, create_task
from dotenv import load_dotenv
from utils import get_response, parser
from datetime import datetime, timedelta
import os

load_dotenv()
TASK_COMPLETED = "task_completed"
TOKEN: Final[str] = os.getenv('TOKEN')

intents: Intents = Intents.default()
intents.message_content = True 
client: Client = Client(intents=intents)

reminders = {}

@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running')

@client.event
async def on_message(message: Message) -> None: 
    if message.author == client.user:
        return  
   
    command = message.content.split()[0].lower()
    args = message.content.split()[1:]

    if command == '!setreminder':

        if len(args) < 2:
            await message.channel.send("Please provide a time interval and task description (e.g., !setreminder 20m do laundry).")
            return

        # Parse time interval (e.g., 20m, 1h, 2d)
        try:
            valid_formats = ['m', 'd', 'h']
            time_value, unit = parser(args[0])
            if not time_value or not unit in valid_formats:
                raise ValueError
            time_interval = int(time_value) * (60 if unit == 'm' else (3600 if unit == 'h' else 86400))
        except ValueError:
            await message.channel.send("Invalid time format. Please use format like \"20m\", \"1h\", or \"2d\".")
            return

        task = " ".join(args[1:])

        reminder_id = f"{message.author.id}"
        if reminders.get(reminder_id, True):
            reminders[reminder_id] = []
        reminders[reminder_id].append({
            "task": task,
            "timeout": utils.utcnow() + timedelta(seconds=time_interval),
            "channel": message.channel,
            "author": message.author,
            "process": 0
        })
        await message.author.send(f"Reminder set for '{task}' in {time_interval // 60} minutes.")

        async def reminder_task(reminder):
            reminder['process'] = current_task()

            while True:
                await utils.sleep_until(reminder["timeout"])
                if reminder in reminders[reminder_id]:  
                    await reminder["author"].send(f"Hey {reminder['author'].mention}, this is a reminder for {reminder['task']}.\nIf you have completed the task then run !setcomplete (task) e.g !setcomplete perform server check")
                reminder["timeout"] += timedelta(seconds=time_interval) 

        task_reminder = reminders[reminder_id]
        create_task(reminder_task(task_reminder[-1]))

    elif command == '!setcompleted':
        reminder_id = f"{message.author.id}"
        arg = " ".join(args)
        client.dispatch(TASK_COMPLETED, user=message.author, task_name=arg, rid=reminder_id)

@client.event
async def on_task_completed(user, task_name, rid) -> None:
    if rid in reminders:
        for task_el in reminders[rid]:
            if task_name == task_el['task']:
                reminder_to_remove = task_el['process']
                reminder_to_remove.cancel()
                del task_el
                await user.send(f"Reminder removed for task {task_name}")
                return
        
        await user.send(f"Did not the find the reminder for: {task_name}")
        

                
       


def main() -> None:
    print("Firing the bot...\n")
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()