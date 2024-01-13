@bot.command()
async def roll(ctx):
    choices = ["Nano", "Hannah"]
    first = random.choice(choices)
    second = random.choice(choices)
    while second == first:
        second = random.choice(choices)
    
    
    
    await ctx.send(f"{first} is asking {second}")