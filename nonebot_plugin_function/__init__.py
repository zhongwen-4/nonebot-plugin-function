import json, os
from httpx import AsyncClient
from nonebot import on_fullmatch, on_type, require, on_startswith
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, Bot, GroupMessageEvent, FriendRequestEvent, MessageEvent, PrivateMessageEvent, GroupRequestEvent, GroupIncreaseNoticeEvent
require("nonebot_plugin_alconna")
require("nonebot_plugin_waiter")
from nonebot_plugin_alconna.uniseg import UniMessage, Target, SupportScope
from nonebot_plugin_alconna.builtins.uniseg.music_share import MusicShare, MusicShareKind
from nonebot_plugin_waiter import waiter
from nonebot.plugin import PluginMetadata

#插件信息
__plugin_meta__ = PluginMetadata(
    name= "奇怪的小功能",
    description= "一些奇奇怪怪的功能和全是BUG的代码",
    type= "application",
    supported_adapters={"~onebot.v11"},
    usage="在群内发送消息即可",
    homepage="https://github.com/zhongwen-4/nonebot-plugin-function"
)

# 指令集
a_word = on_fullmatch("一言")
poke = on_type((PokeNotifyEvent,), handlers =[])
friend = on_type(FriendRequestEvent, handlers= [])
approve = on_startswith("同意")
Message_forwarding = on_type(PrivateMessageEvent, handlers= [])
invite = on_type(GroupRequestEvent, handlers= [])
increase = on_type(GroupIncreaseNoticeEvent, handlers= [])
msg_id = on_startswith("取信息")
debug = on_startswith("点歌")

@a_word.handle()
async def a_handle():
    async with AsyncClient() as client:
        text = await client.get("https://v1.hitokoto.cn/")

    text = text.json()
    print(text)
    source = text["from"]
    if (who := text["from_who"]) == None:
        who = "佚名"
    hitokoto = text["hitokoto"]
    await a_word.finish(f"{hitokoto}    ----{who}[{source}]")

@poke.handle()
async def poke_handle(bot: Bot, event: GroupMessageEvent):
    if event.sub_type == "poke":
        if str(event.get_user_id()) != event.self_id :
            t = Target(id = event.get_user_id(), private= True, scope = SupportScope.qq_client)
            async with AsyncClient() as client:
                text = await client.get("https://act.jiawei.xin:10086/lib/api/maren.php")
            await UniMessage(text.text).send(target= t)
            await bot.call_api("group_poke",group_id= event.group_id, user_id= event.get_user_id())
            await poke.finish("你戳你妈呢傻逼", at_sender = True)

@friend.handle()
async def f_handle(event: FriendRequestEvent):
    t = Target(id ="2401128923", private= True, scope = SupportScope.qq_client)
    get = await UniMessage(f"你收到了一个好友请求\nQQ号:{event.user_id}\n验证信息: {event.comment}").send(target= t)
    msg_id = event.user_id
    flag = event.flag
    w = {}
    w[msg_id] = flag
    if not os.path.exists("./Small_function_data.json"):
        os.system("{}".format("./Small_function_data.json"))

    with open("./Small_function_data.json", "w") as f:
        json.dump(
            w, f, indent= 4, ensure_ascii= True
            )
        
@approve.handle()
async def app_handle(bot: Bot, event: MessageEvent):
    i = event.message.extract_plain_text()
    a = i[2:]

    with open("./Small_function_data.json","r") as f:
        load = json.load(f)
    b = load[str(a)]
    await bot.set_friend_add_request(
        flag=b, approve=True, remark=""
        )
    
    t = Target(
        id ="2401128923", private= True, scope = SupportScope.qq_client
        )

    with open("./Small_function_data.json", "w") as f:
        json.dump(
            {}, f, indent= 4, ensure_ascii= True
            )
        
    await UniMessage("已同意").send(target= t)

@Message_forwarding.handle()
async def mf_handle(event: PrivateMessageEvent):
    msg = event.get_message()
    user_id = event.get_user_id()
    name = event.sender.nickname
    
    if user_id != "2401128923":
        t = Target(id ="2401128923", private= True, scope = SupportScope.qq_client)
        log = event.get_log_string()
        await UniMessage(f"{log}").send(target= t)
        await UniMessage(f"收到来自{name}{user_id}的消息: {msg}").finish(target= t)

@invite.handle()
async def i_handle(event: GroupRequestEvent):
    if event.sub_type == "invite":
        user_id = event.user_id
        group = event.group_id
        t = Target(id ="2401128923", private= True, scope = SupportScope.qq_client)
        await UniMessage(f"收到来自{user_id}的加群邀请: {group}").finish(target= t)
    
    else:
        if event.sub_type == "add":
            user_id = event.user_id
            group = event.group_id
            t = Target(id ="2401128923", private= True, scope = SupportScope.qq_client)
            await UniMessage(f"群{group}收到来自{user_id}加群请求").finish(target= t)

@msg_id.handle()
async def mi_handle(event: GroupMessageEvent, bot: Bot):
    if "at" in event.message:
        for m in event.message:
            if m.type == "at":
                user_id = m.data["qq"]
    else:
        user_id = event.get_message().extract_plain_text()
        user_id = user_id[3:]

    re = await bot.call_api("get_stranger_info", user_id= user_id) # type: ignore

    await msg_id.finish(str(re))

@debug.handle()
async def debug_handle(event: MessageEvent):
        title = event.get_message().extract_plain_text()
        title = title[2:]
        async with AsyncClient() as cli:
            p = {"name": title}
            url = await cli.get(f"https://api.xingzhige.com/API/Kugou_GN_new/", params= p)
            
            if url.status_code == 200:
                url= url.json()

                ti = [i["songname"] for i in url["data"] if "songname" in i]
                name = [i["name"] for i in url["data"] if "name" in i]

                output = "\n".join(f"{i+1}: {a_item} - {b_item}" for i,(a_item, b_item) in enumerate(zip(ti, name)))
                await debug.send(f"{output}\n\nPS: 请在十五秒内输入序号")
            
            else:
                await debug.finish("获取链接的时候404了", at_sender= True)

        @waiter(waits=["message"], keep_session=True)
        async def check(event: GroupMessageEvent):
            return event.get_plaintext()
        resp = await check.wait(timeout= 15)
        if resp is None:
            await debug.send("等待超时")
            return
        if not resp.isdigit() or int(resp) > 10 or int(resp) <= 0:
            await debug.send("你似乎点错了呢, 请重新点一次吧")
            return

        async with AsyncClient() as cli:
            p = {"name": title, "n": resp}
            url = await cli.get(f"https://api.xingzhige.com/API/Kugou_GN_new/", params= p)
            if url.status_code == 200:
                url= url.json()
                data = MusicShare(
                    kind= MusicShareKind.QQMusic,
                    title= url["data"]["songname"],
                    content= url["data"]["name"],
                    url= url["data"]["songurl"],
                    audio= url["data"]["src"],
                    thumbnail= url["data"]["cover"]
                )

                data = UniMessage(data)
                await data.finish()
            
            else:
                await debug.finish("获取不到歌曲信息")