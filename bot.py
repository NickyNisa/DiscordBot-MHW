import discord
from discord.ext import commands

# ตั้งค่า Intents
intents = discord.Intents.default()
intents.message_content = True

# สร้างคลาสสำหรับ Bot เพื่อให้รองรับ Slash Commands
class MHWBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # ซิงค์คำสั่ง Slash Command ไปยัง Discord
        await self.tree.sync()
        print(f"✅ บอท {self.user} ออนไลน์และพร้อมใช้งานแล้ว!")

bot = MHWBot()

# ข้อมูลจำลอง (Mock Data) สำหรับมอนสเตอร์ (สามารถดึงจาก JSON หรือ Database ได้ในอนาคต)
monster_data = {
    "chatacabra": {
        "type": "Amphibian",
        "habitat": "Windward Plains",
        "weakness": "Water, Ice",
        "image_url": "https://url-รูปภาพ-มอนสเตอร์.com/chatacabra.png"
    },
    "doshaguma": {
        "type": "Fanged Beast",
        "habitat": "Windward Plains",
        "weakness": "Fire, Poison",
        "image_url": "https://url-รูปภาพ-มอนสเตอร์.com/doshaguma.png"
    }
}

# สร้าง Slash Command สำหรับหามอนสเตอร์
@bot.tree.command(name="monster", description="ค้นหาข้อมูลมอนสเตอร์ใน Monster Hunter Wilds")
async def monster(interaction: discord.Interaction, name: str):
    name_lower = name.lower()
    
    if name_lower in monster_data:
        data = monster_data[name_lower]
        
        # สร้าง Embed เพื่อให้ข้อมูลดูสวยงาม
        embed = discord.Embed(
            title=f"🐉 ข้อมูลของ {name.capitalize()}", 
            color=discord.Color.brand_green()
        )
        embed.add_field(name="ประเภท", value=data["type"], inline=True)
        embed.add_field(name="ถิ่นที่อยู่", value=data["habitat"], inline=True)
        embed.add_field(name="จุดอ่อนหลัก", value=f"**{data['weakness']}**", inline=False)
        
        # ถ้ามีรูปภาพให้ใส่แบบนี้ (คอมเมนต์ไว้ก่อน)
        # embed.set_thumbnail(url=data["image_url"])
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ ไม่พบข้อมูลของมอนสเตอร์: `{name}` ในฐานข้อมูล", ephemeral=True)

# ใส่ Token ของคุณตรงนี้
bot.run("นำ_TOKEN_ของคุณมาวางที่นี่")