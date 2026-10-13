import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv

from keep_alive import keep_alive

# โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ตั้งค่า Intents (ใช้แค่ default ไม่ขอสิทธิ์อ่านข้อความเพื่อแก้ Error และเพิ่ม Privacy)
intents = discord.Intents.default()

# ==========================================
# 1. สร้างฟังก์ชัน Autocomplete สำหรับค้นหาชื่อมอนสเตอร์
async def monster_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    # ดึงรายชื่อมอนสเตอร์ทั้งหมดจาก key ของไฟล์ JSON (เช่น ajarakan, rathalos)
    monsters = list(monster_data.keys())
    
    # กรองเฉพาะชื่อที่มี "ตัวอักษร" ที่ผู้ใช้กำลังพิมพ์อยู่ (current)
    # Discord จำกัดให้โชว์ตัวเลือกได้สูงสุด 25 อัน จึงต้องใส่ [:25] ไว้ท้ายสุด
    choices = [
        app_commands.Choice(name=monster.capitalize(), value=monster)
        for monster in monsters if current.lower() in monster.lower()
    ]
    return choices[:25]
# ==========================================

class MHWBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ บอท {self.user} ออนไลน์และพร้อมใช้งานแล้ว!")

bot = MHWBot()

# ==========================================
# โหลดข้อมูลจากไฟล์ JSON เข้ามาเก็บในตัวแปร
with open('monsters.json', 'r', encoding='utf-8') as f:
    monster_data = json.load(f)
# ==========================================

# 2. คำสั่ง /monster (ผูกระบบ Autocomplete เข้าไป)
@bot.tree.command(name="monster", description="ค้นหาข้อมูลมอนสเตอร์ใน Monster Hunter Wilds")
@app_commands.autocomplete(name=monster_autocomplete) # <-- บรรทัดนี้คือตัวเชื่อมระบบ
async def monster(interaction: discord.Interaction, name: str):
    name_lower = name.lower()
    
    if name_lower in monster_data:
        data = monster_data[name_lower]
        
        embed = discord.Embed(
            title=f"🐉 {name.capitalize()}\n{data.get('name_jp', '')}", 
            color=discord.Color.dark_red()
        )
        
        embed.set_thumbnail(url=data.get("image_url", ""))
        
        embed.add_field(name="Elements", value=data.get("elements", "-"), inline=True)
        embed.add_field(name="Status Effects", value=data.get("status_effects", "-"), inline=True)
        embed.add_field(name="Weakest To", value=data.get("weakest_to", "-"), inline=True)
        
        embed.add_field(name="Capture HP", value=data.get("capture_hp", "-"), inline=True)
        embed.add_field(name="Limp HP", value=data.get("limp_hp", "-"), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True) 
        
        embed.add_field(
            name="🛠️ Item & Trap Effectiveness", 
            value=f"**Traps:** {data.get('traps', '-')}\n**Items:** {data.get('items', '-')}", 
            inline=False
        )
        
        embed.add_field(
            name="⚔️ Damage Effectiveness (จุดอ่อนหลัก)", 
            value=data.get("hitzones", "-"), 
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ ไม่พบข้อมูลของมอนสเตอร์: `{name}`", ephemeral=True)

keep_alive()
# รันบอทด้วย Token ที่ดึงมาจากไฟล์ .env
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ไม่พบ Token! กรุณาตรวจสอบไฟล์ .env ของคุณ")