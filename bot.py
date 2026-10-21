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

# ==========================================
# 1. โหลดข้อมูลจากไฟล์ JSON ไว้บนสุด เพื่อให้พร้อมใช้งานทันทีเมื่อเซิร์ฟเวอร์ตื่น
with open('monsters.json', 'r', encoding='utf-8') as f:
    monster_data = json.load(f)
# ==========================================

# ตั้งค่า Intents
intents = discord.Intents.default()

# ==========================================
# 2. สร้างฟังก์ชัน Autocomplete สำหรับค้นหาชื่อมอนสเตอร์
async def monster_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    monsters = list(monster_data.keys())
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

# 3. คำสั่ง /monster
@bot.tree.command(name="monster", description="ค้นหาข้อมูลมอนสเตอร์ใน Monster Hunter Wilds")
@app_commands.autocomplete(name=monster_autocomplete)
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

# 4. เรียกใช้เว็บจำลองและรันบอท
keep_alive()

# 5. คำสั่ง /info สำหรับดูสถานะของบอท
@bot.tree.command(name="info", description="แสดงข้อมูลและสถานะการทำงานของบอท")
async def info(interaction: discord.Interaction):
    # คำนวณค่าความหน่วง (Ping) เป็นมิลลิวินาที
    ping = round(bot.latency * 1000)
    
    # นับจำนวนเซิร์ฟเวอร์ (Guilds) ที่บอทสิงอยู่
    server_count = len(bot.guilds)
    
    # นับจำนวนมอนสเตอร์ทั้งหมดในไฟล์ JSON
    monster_count = len(monster_data)
    
    embed = discord.Embed(
        title="📊 ข้อมูลและสถานะของบอท (MHW Bot)", 
        description="บอทฐานข้อมูลสำหรับเกม Monster Hunter Wilds",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="📶 ความหน่วง (Ping)", value=f"`{ping} ms`", inline=True)
    embed.add_field(name="🌐 จำนวนเซิร์ฟเวอร์", value=f"`{server_count} Servers`", inline=True)
    embed.add_field(name="🐉 ข้อมูลมอนสเตอร์", value=f"`{monster_count} ตัว`", inline=True)
    embed.add_field(name="💻 ไลบรารี", value=f"`discord.py v{discord.__version__}`", inline=True)
    embed.add_field(name="ผู้พัฒนา", value="`Wasin Liamkaew`", inline=True)
    
    # ถ้ามีรูปโปรไฟล์บอท สามารถดึงมาโชว์ที่ Thumbnail ได้
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
        
    await interaction.response.send_message(embed=embed)
# ==========================================

# ==========================================
# 6. คำสั่ง /elemental_damage สำหรับดูข้อมูลธาตุและสถานะผิดปกติ
@bot.tree.command(name="elemental_damage", description="แสดงข้อมูลผลลัพธ์ของธาตุและสถานะผิดปกติต่างๆ")
async def elemental_damage(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ ข้อมูลธาตุและสถานะผิดปกติ (Elemental & Status Effects)", 
        description="ผลลัพธ์เมื่อนักล่า (Hunter) หรือมอนสเตอร์ติดสถานะต่างๆ",
        color=discord.Color.orange()
    )
    
    # หมวดหมู่: ธาตุหลัก (Elemental Blights)
    embed.add_field(
        name="🔥 Fireblight (ไฟ)", 
        value="ลดพลังชีวิต (HP) ลงเรื่อยๆ อย่างต่อเนื่อง\n*วิธีแก้: กลิ้งบนพื้น 3 ครั้ง (ถ้ากลิ้งบนน้ำจะหายทันที) หรือกิน Nulberry*", 
        inline=False
    )
    embed.add_field(
        name="💧 Waterblight (น้ำ)", 
        value="ความเร็วในการฟื้นฟูหลอด Stamina ช้าลงอย่างมาก\n*วิธีแก้: กิน Nulberry*", 
        inline=False
    )
    embed.add_field(
        name="⚡ Thunderblight (สายฟ้า)", 
        value="ทำให้มีโอกาสติดสถานะ Stun (มึนงง) ได้ง่ายขึ้นเมื่อโดนโจมตี\n*วิธีแก้: กิน Nulberry*", 
        inline=False
    )
    embed.add_field(
        name="❄️ Iceblight (น้ำแข็ง)", 
        value="การใช้ Stamina (เช่น กลิ้ง, วิ่ง) จะกินหลอด Stamina มากขึ้นกว่าปกติ\n*วิธีแก้: กิน Nulberry*", 
        inline=False
    )
    embed.add_field(
        name="🐉 Dragonblight (มังกร)", 
        value="ลบล้างค่าพลังธาตุและสถานะผิดปกติของอาวุธเราทั้งหมด (ตีเป็นกายภาพอย่างเดียว)\n*วิธีแก้: กิน Nulberry*", 
        inline=False
    )

    # หมวดหมู่: สถานะผิดปกติ (Abnormal Status)
    embed.add_field(
        name="☠️ Poison (พิษ)", 
        value="ลด HP อย่างต่อเนื่อง (รุนแรงกว่าไฟและกลิ้งให้ดับไม่ได้)\n*วิธีแก้: กิน Antidote หรือ Herbal Medicine*", 
        inline=False
    )
    embed.add_field(
        name="⚡ Paralysis (ชา) & 💤 Sleep (หลับ)", 
        value="**Paralysis:** ขยับตัวไม่ได้ชั่วขณะ เปิดโอกาสให้โดนโจมตีฟรี\n**Sleep:** หลับลงกับพื้น การโดนโจมตีครั้งแรกขณะหลับจะโดนดาเมจแรงขึ้น 2 เท่า", 
        inline=False
    )
    embed.add_field(
        name="💥 Blast (ระเบิด)", 
        value="สะสมเป็นฝุ่นผงตามตัว เมื่อโดนตีหรือปล่อยไว้จะระเบิดทำดาเมจตายตัวอย่างรุนแรง\n*วิธีแก้: กลิ้งบนพื้นซ้ำๆ จนฝุ่นหลุดออก*", 
        inline=False
    )
    embed.add_field(
        name="🩸 Bleed (เลือดไหล)", 
        value="ทุกครั้งที่ขยับตัวรุนแรง (วิ่ง, กลิ้ง, โจมตี) จะเสีย HP\n*วิธีแก้: นั่งยองๆ (Crouch) อยู่นิ่งๆ สักพัก หรือกิน Astera Jerky*", 
        inline=False
    )
    
    # รูปภาพประกอบ (ถ้ามีรูปตารางธาตุรวมๆ สามารถใส่ URL แทนที่ลิงก์นี้ได้)
    embed.set_thumbnail(url="https://monsterhunterwiki.org/images/thumb/9/91/UI-Confused.png/16px-UI-Confused.png.webp") # ใส่ไอคอนประดับ
    
    await interaction.response.send_message(embed=embed)
# ==========================================

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ไม่พบ Token! กรุณาตรวจสอบไฟล์ .env ของคุณ")