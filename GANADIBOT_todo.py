import discord
from discord import app_commands
import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

todos_data = {}

# 데이터 파일 경로
DATA_FILE = 'todos.json'

class TodoClient(discord.Client):
    def __init__(self):
        # 기본 인텐트만 사용 (특권 인텐트 불필요)
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # 슬래시 명령어 동기화
        await self.tree.sync()
        print(f"슬래시 명령어 동기화 완료")

# 봇 클라이언트 생성
client = TodoClient()

def load_todos():
    """할일 데이터 로드"""
    global todos_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                todos_data = json.load(f)
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        todos_data = {}

def save_todos():
    """할일 데이터 저장"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(todos_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"데이터 저장 오류: {e}")

def get_user_todos(user_id):
    """사용자별 할일 목록 가져오기"""
    user_id = str(user_id)
    if user_id not in todos_data:
        todos_data[user_id] = []
    return todos_data[user_id]

@client.event
async def on_ready():
    """봇이 준비되었을 때"""
    print(f'{client.user}가 로그인했습니다!')
    load_todos()

@client.tree.command(name="할일추가", description="새로운 할일을 추가합니다")
@app_commands.describe(내용="추가할 할일 내용")
async def add_todo(interaction: discord.Interaction, 내용: str):
    """할일 추가"""
    user_todos = get_user_todos(interaction.user.id)

    todo_item = {
        'id': len(user_todos) + 1,
        'content': 내용,
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    user_todos.append(todo_item)
    save_todos()

    embed = discord.Embed(
        title="✅ 할일 추가됨",
        description=f"**{내용}**",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"ID: {todo_item['id']}")

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="할일목록", description="내 할일 목록을 보여줍니다")
async def list_todos(interaction: discord.Interaction):
    """할일 목록 조회"""
    user_todos = get_user_todos(interaction.user.id)

    if not user_todos:
        embed = discord.Embed(
            title="📝 할일 목록",
            description="등록된 할일이 없습니다.",
            color=0x808080
        )
        await interaction.response.send_message(embed=embed)
        return

    # 완료되지 않은 할일과 완료된 할일 분리
    pending_todos = [todo for todo in user_todos if not todo['completed']]
    completed_todos = [todo for todo in user_todos if todo['completed']]

    embed = discord.Embed(
        title="📝 할일 목록",
        color=0x0099ff,
        timestamp=datetime.now()
    )

    if pending_todos:
        pending_text = "\n".join([
            f"**{todo['id']}.** {todo['content']}"
            for todo in pending_todos
        ])
        embed.add_field(name="🔄 진행중", value=pending_text, inline=False)

    if completed_todos:
        completed_text = "\n".join([
            f"**{todo['id']}.** ~~{todo['content']}~~"
            for todo in completed_todos
        ])
        embed.add_field(name="✅ 완료됨", value=completed_text, inline=False)

    embed.set_footer(text=f"총 {len(user_todos)}개의 할일")

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="할일완료", description="할일을 완료 처리합니다")
@app_commands.describe(할일번호="완료할 할일의 번호")
async def complete_todo(interaction: discord.Interaction, 할일번호: int):
    """할일 완료"""
    user_todos = get_user_todos(interaction.user.id)

    # 해당 ID의 할일 찾기
    todo_item = None
    for todo in user_todos:
        if todo['id'] == 할일번호:
            todo_item = todo
            break

    if not todo_item:
        embed = discord.Embed(
            title="❌ 오류",
            description=f"ID {할일번호}인 할일을 찾을 수 없습니다.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if todo_item['completed']:
        embed = discord.Embed(
            title="⚠️ 경고",
            description="이미 완료된 할일입니다.",
            color=0xffaa00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    todo_item['completed'] = True
    todo_item['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_todos()

    embed = discord.Embed(
        title="🎉 할일 완료!",
        description=f"**{todo_item['content']}**",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"ID: {할일번호}")

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="할일삭제", description="할일을 삭제합니다")
@app_commands.describe(할일번호="삭제할 할일의 번호")
async def delete_todo(interaction: discord.Interaction, 할일번호: int):
    """할일 삭제"""
    user_todos = get_user_todos(interaction.user.id)

    # 해당 ID의 할일 찾기
    todo_index = -1
    for i, todo in enumerate(user_todos):
        if todo['id'] == 할일번호:
            todo_index = i
            break

    if todo_index == -1:
        embed = discord.Embed(
            title="❌ 오류",
            description=f"ID {할일번호}인 할일을 찾을 수 없습니다.",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    deleted_todo = user_todos.pop(todo_index)
    save_todos()

    embed = discord.Embed(
        title="🗑️ 할일 삭제됨",
        description=f"**{deleted_todo['content']}**",
        color=0xff6600,
        timestamp=datetime.now()
    )

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="할일초기화", description="모든 할일을 삭제합니다")
async def clear_todos(interaction: discord.Interaction):
    """모든 할일 삭제"""
    user_todos = get_user_todos(interaction.user.id)

    if not user_todos:
        embed = discord.Embed(
            title="ℹ️ 알림",
            description="삭제할 할일이 없습니다.",
            color=0x808080
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    todo_count = len(user_todos)
    todos_data[str(interaction.user.id)] = []
    save_todos()

    embed = discord.Embed(
        title="🧹 할일 목록 초기화",
        description=f"{todo_count}개의 할일이 모두 삭제되었습니다.",
        color=0xff3333,
        timestamp=datetime.now()
    )

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="도움말", description="봇 사용법을 보여줍니다")
async def help_command(interaction: discord.Interaction):
    """도움말"""
    embed = discord.Embed(
        title="📚 할일 관리봇 사용법",
        color=0x7289da,
        timestamp=datetime.now()
    )

    commands_info = [
        ("📝 `/할일추가 [내용]`", "새로운 할일을 추가합니다"),
        ("📋 `/할일목록`", "내 할일 목록을 확인합니다"),
        ("✅ `/할일완료 [번호]`", "할일을 완료 처리합니다"),
        ("🗑️ `/할일삭제 [번호]`", "할일을 삭제합니다"),
        ("🧹 `/할일초기화`", "모든 할일을 삭제합니다"),
        ("❓ `/도움말`", "이 도움말을 표시합니다")
    ]

    for cmd, desc in commands_info:
        embed.add_field(name=cmd, value=desc, inline=False)

    embed.set_footer(text="각 사용자별로 개별 할일 목록이 관리됩니다")

    await interaction.response.send_message(embed=embed)

# 봇 실행
if __name__ == "__main__":
    client.run(TOKEN)