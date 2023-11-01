""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import os
import json
import requests
import datetime

from discord.ext import commands
from discord.ext.commands import Context

headers = {
  "Accept": "application/json"
}

query = {
  'key': os.environ["TRELLO_KEY"],
  'token': os.environ["TRELLO_TOKEN"]
}

ignored_label_id = os.environ["TRELLO_IGNORED_HEADER_ID"]

ignored_list_id_list = [
    os.environ["TRELLO_IGNORED_LIST_ID_1"],
    os.environ["TRELLO_IGNORED_LIST_ID_2"],
    os.environ["TRELLO_IGNORED_LIST_ID_3"]
]

member_id_to_name = {
    os.environ["TRELLO_SHOWAY_ID"]: "showay",
    os.environ["TRELLO_TOMMY_ID"]: "Tommy",
    os.environ["TRELLO_MEGAN_ID"]: "Megan"
}

class TrelloCard:
    def __init__(self, trello_card_dict):
        self._title = trello_card_dict["name"]
        self._id_members = None
        if len(trello_card_dict["idMembers"]):
            self._id_members = trello_card_dict["idMembers"]
        self._due = None
        if trello_card_dict["due"]:
            self._due = datetime.datetime.strptime(
                trello_card_dict["due"], '%Y-%m-%dT%H:%M:%S.000Z') + datetime.timedelta(hours=8)

    def time(self, render=False) -> datetime:
        if not render:
            return self._due if self._due else datetime.datetime.max - datetime.timedelta(hours=12)

    def stamp(self):
        return self.time().timestamp()

    def __str__(self):
        if self._due:
            return f"__[{self.time()}]__  {self._title}"        
        else:
            return f"{self._title}"


# Here we name the cog and create a new class for the cog.
class TrelloBot(commands.Cog, name="trello"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="trello",
        description="Get undone cards.",
    )
    async def get_undone(self, context: Context) -> None:
        board_ids = [
            os.environ["TRELLO_SOCIAL_MEDIA_BOARD_ID"],
            os.environ["TRELLO_TASK_BOARD_ID"]]
        board_names = ["Social Media Posts", "獸人的工作們！"]

        message = "# 待完成 \n"

        for board_name, board_id in zip(board_names, board_ids):
            info = self.get_open_card_info(board_id)
            message += f"\n> ## {board_name}\n"
            for mem, cards in info.items():
                if mem == "pending":
                    continue
                name = member_id_to_name[mem]
                message += f"> ### {name}\n"
                for card in cards:
                    message += f"> - {card}\n"
            if "pending" in info.keys():
                cards = info["pending"]
                message += "> ### 還沒分配的工作\n"
                for card in cards:
                    message += f"> - {card}\n"
        print(message)
        await context.send(message)
        
    def get_open_card_info(self, board_id: str):
        url = f"https://api.trello.com/1/boards/{board_id}/cards/open"
        response = requests.request(
           "GET",
           url,
           params=query
        )
        response = json.loads(response.text)
        member_id_to_task_dict = {}
        for card in response:
            if ignored_label_id in card["idLabels"]:
                continue
            if card["idList"] in ignored_list_id_list:
                continue
            if card["dueComplete"]:
                continue
            trello_card = TrelloCard(card)
            if len(card["idMembers"]) == 0:
                if "pending" not in member_id_to_task_dict.keys():
                    member_id_to_task_dict["pending"] = []
                member_id_to_task_dict["pending"].append(trello_card)
            else:
                for mem in card["idMembers"]:
                    if mem not in member_id_to_task_dict.keys():
                        member_id_to_task_dict[mem] = []
                    member_id_to_task_dict[mem].append(trello_card)
        for mem in member_id_to_task_dict.keys():
            member_id_to_task_dict[mem].sort(key=lambda x: x.stamp())
        return member_id_to_task_dict


    async def get_boards(self):
        url = "https://api.trello.com/1/members/me/boards"
        headers = {
          "Accept": "application/json"
        }
        query = {
          'key': os.environ["TRELLO_KEY"],
          'token': os.environ["TRELLO_TOKEN"]
        }
        response = requests.request(
           "GET",
           url,
           headers=headers,
           params=query
        )

        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

        


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(TrelloBot(bot))
