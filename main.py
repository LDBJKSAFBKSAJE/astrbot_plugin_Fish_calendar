from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import aiohttp
import asyncio
from datetime import datetime, time
import pytz

@register("moyuribao", "橘子", "一个获取摸鱼日报视频的插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.reaction_time = 5  # 默认反应时间为5秒
        self.scheduled_time = time(9, 0)  # 默认每天9点发送
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.schedule_daily_task())

    # 设置每天发送时间的指令
    @filter.command("set_time")
    async def set_schedule_time(self, event: AstrMessageEvent):
        '''设置每天发送时间'''
        try:
            hour, minute = map(int, event.message_str.split(':'))
            if 0 <= hour < 24 and 0 <= minute < 60:
                self.scheduled_time = time(hour, minute)
                yield event.plain_result(f"每天发送时间已设置为 {hour}:{minute}")
            else:
                yield event.plain_result("请输入有效的时间（格式：HH:MM）")
        except ValueError:
            yield event.plain_result("请输入有效的时间（格式：HH:MM）")

    async def schedule_daily_task(self):
        '''定时任务，每天在指定时间发送摸鱼日报'''
        while True:
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            target_time = datetime.combine(now.date(), self.scheduled_time)
            if now >= target_time:
                target_time = datetime.combine((now + timedelta(days=1)).date(), self.scheduled_time)
            wait_seconds = (target_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            await self.send_moyuribao()

    async def send_moyuribao(self):
        '''发送摸鱼日报视频'''
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dayu.qqsuu.cn/moyuribaoshipin/apis.php") as response:
                if response.status == 200:
                    video_url = await response.text()
                    yield event.video_result(video_url)
                else:
                    yield event.plain_result("获取视频失败，请稍后再试")

    # 获取摸鱼日报视频的指令
    @filter.command("moyuribao")
    async def moyuribao(self, event: AstrMessageEvent):
        '''获取摸鱼日报视频'''
        await self.send_moyuribao()

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
