from sortedShin.bot.scripts.query import query

def setup(bot):
    @bot.command()
    async def search(ctx, *, text):
        results = query(text)
        if not results:
            await ctx.send("No results found.")
            return

        msg = "\n\n".join(
            f"▌ ◈ {r['name'].capitalize()} ◈\n    https://www.shinseina.world/post/{r['link'].split('/')[-1]}"
            for r in results[:5]
        )
        await ctx.send(msg)

    @search.error
    async def search_error(ctx, error):
        await ctx.send(f"Search failed: `{error}`")
