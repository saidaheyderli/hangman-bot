from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random

# Word list
WORDS = ["QAYMAG", "BERBAT", "JET", "MAMMADALI", "GAME", "KIWI", "IDEAL", "PIZZA", "BURGER", "BATMAN", "SPRITE", "ELON MUSK"]

HANGMAN_IMAGES = [
    "hangman0.jpg",
    "hangman1.jpg",
    "hangman2.jpg",
    "hangman3.jpg",
    "hangman4.jpg",
    "hangman5.jpg",
    "hangman6.jpg"
]

HANGMAN_IMAGES_REVERSED = HANGMAN_IMAGES[::-1]
MAX_ATTEMPTS = 6
games = {}

def new_game(user_id):
    word = random.choice(WORDS)
    hidden_word = ["_" for _ in word]
    return {"word": word, "hidden": hidden_word, "attempts": 0, "guessed": []}

def get_keyboard(game):
    buttons = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if letter not in game["guessed"]:
            buttons.append(InlineKeyboardButton(letter, callback_data=letter))
        else:
            buttons.append(InlineKeyboardButton("❌", callback_data="none"))
    keyboard = [buttons[i:i+6] for i in range(0, len(buttons), 6)]
    return InlineKeyboardMarkup(keyboard)


async def start_game_for_query(query, user_id):
    games[user_id] = new_game(user_id)
    game = games[user_id]

    with open(HANGMAN_IMAGES_REVERSED[game['attempts']], "rb") as photo:
        await query.message.reply_photo(
            photo=photo,
            caption=f"Word: {' '.join(game['hidden'])}\nWrong guesses: {game['attempts']}/{MAX_ATTEMPTS}",
            reply_markup=get_keyboard(game)
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    games[user_id] = new_game(user_id)
    game = games[user_id]

    with open(HANGMAN_IMAGES_REVERSED[game['attempts']], "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=f"Word: {' '.join(game['hidden'])}\nWrong guesses: {game['attempts']}/{MAX_ATTEMPTS}",
            reply_markup=get_keyboard(game)
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    
    if query.data == "PLAY_AGAIN":
        await start_game_for_query(query, user_id)
        await query.answer("New game started!")
        return
    elif query.data == "NO_PLAY":
        await query.answer("Okay! See you next time 🙂")
        return

    if user_id not in games:
        await query.answer("Please start a game first using /play!")
        return

    game = games[user_id]
    letter = query.data.upper()

    if letter == "NONE":
        await query.answer()
        return

    if letter in game["guessed"]:
        await query.answer("You already guessed this letter!")
        return

    game["guessed"].append(letter)

    if letter in game["word"]:
        for i, l in enumerate(game["word"]):
            if l == letter:
                game["hidden"][i] = letter
        await query.answer("Correct guess!")
    else:
        game["attempts"] += 1
        await query.answer("Wrong guess!")

    
    if "_" not in game["hidden"]:
        await query.message.reply_text(f"Congratulations! You guessed the word: {game['word']} 🤗")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data="PLAY_AGAIN"),
             InlineKeyboardButton("No", callback_data="NO_PLAY")]
        ])
        await query.message.reply_text("Do you want to play again?", reply_markup=keyboard)
        del games[user_id]
        return

    
    if game["attempts"] > MAX_ATTEMPTS:
        await query.message.reply_text(f"Game Over! The word was: {game['word']} 😔")

        
        with open("lost.mp4", "rb") as gif:
            await query.message.reply_animation(animation=gif)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data="PLAY_AGAIN"),
             InlineKeyboardButton("No", callback_data="NO_PLAY")]
        ])
        await query.message.reply_text("Do you want to play again?", reply_markup=keyboard)
        del games[user_id]
        return

    
    img_index = game["attempts"]
    if img_index > MAX_ATTEMPTS:
        img_index = MAX_ATTEMPTS

    with open(HANGMAN_IMAGES_REVERSED[img_index], "rb") as photo:
        await query.message.reply_photo(
            photo=photo,
            caption=f"Word: {' '.join(game['hidden'])}\nWrong guesses: {game['attempts']}/{MAX_ATTEMPTS}",
            reply_markup=get_keyboard(game)
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token("BOT_TOKEN").build()

    app.add_handler(CommandHandler("play", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()

