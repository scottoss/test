from redbot.core import commands
import time
from subprocess import run, CalledProcessError

class Mycog(commands.Cog):
    """My custom cog"""

    async def send_plugins(self, ctx):
        services = run(["/usr/bin/streamlink", "--plugins"], check=True, capture_output=True)
        return await ctx.send("Provide an active livestream URL from any of these services: "+str(services.stdout.decode()))

    def stop_ffmpeg(self):
        return run("screen -X -S streamcast quit", shell=True)

    def is_casting(self):
        out = run("screen -ls | grep streamcast", shell=True, capture_output=True)
        return out.stdout.decode().find("streamcast") >= 0

    @commands.command()
    async def unloadstream(self, ctx):
        if self.is_casting():
            self.stop_ffmpeg()
            return await ctx.send("Stream unloaded")
        else:
            return await ctx.send("No stream to unload")

    @commands.command()
    async def loadstream(self, ctx, query=None):
        print(query)
        if not query:
            return await self.send_plugins(ctx)
        geturl = run(["/usr/bin/streamlink", query, 'worst', "--stream-url"], capture_output=True)
        url = str(geturl.stdout.decode())
        if not url.startswith("http"):
            return await ctx.send(url)
        self.stop_ffmpeg()
        run("/usr/bin/screen -dmS streamcast /home/arch/cogs/mycog/cast.sh \""+url+"\"", shell=True)
        time.sleep(1)
        if self.is_casting():
            return await ctx.send("Stream loaded.")
        else:
            return await ctx.send("Something went wrong. Check the logs")

    @commands.command()
    async def playstream(self, ctx, query=None):
        await ctx.invoke(self.loadstream, query=query)

        audiocog = ctx.bot.get_cog("Audio")
        if not audiocog:
            return await ctx.send("You need to load the audio cog first")

        time.sleep(5) # wait a bit for icecast to be ready to serve the stream
        return await ctx.invoke(audiocog.play, query="http://localhost:8000/stream")


    @commands.command()
    async def stopstream(self, ctx):
        audiocog = ctx.bot.get_cog("Audio")
        if audiocog:
            await ctx.invoke(audiocog.stop)
        await ctx.invoke(self.unloadstream)

