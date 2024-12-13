import os
import asyncio
import numpy as np
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from tensorflow import keras
from PIL import Image
from aiogram import F
from keras._tf_keras.keras.models import load_model
from keras._tf_keras.keras.applications.densenet import preprocess_input
from keras._tf_keras.keras.preprocessing.image import img_to_array

API_TOKEN = 'your_bot_api_token'

path = './photos'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()  # Create a router instance

# Define the classes of mushrooms
classes = ['No mushrooms', 'Edible', 'Hallucinogenic', 'Inedible', 'Poisonous']


# Prediction function


def predict_mushrooms():
    result = []
    model = load_model('my_model.keras')  # Load the model once for efficiency
    path = './photos'

    for name_img in os.listdir(path):
        file_path = os.path.join(path, name_img)
        if os.path.isfile(file_path):  # Ensure it is a file, not a directory
            try:
                # Process the image
                img = Image.open(file_path)
                img = img.convert('RGB')
                img = img.resize((224, 224))
                img_array = img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                final_img = preprocess_input(img_array)

                # Make the prediction
                prediction = model(final_img, training=False)  # Use the model to predict
                result.append(np.argmax(prediction, axis=-1)[0])

                os.remove(file_path)  # Remove file after processing
            except Exception as e:
                print(f"Error processing {name_img}: {e}")

    return result


# Handlers
@router.message(Command(commands=['start']))
async def send_welcome(message: Message):
    await message.reply(
        "Hello! I can tell the type of mushroom from the photo. "
        "I can classify mushrooms as: edible, inedible, poisonous, or hallucinogenic."
    )

@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.reply("Send me a photo of the mushroom, and I'll tell you whether you can eat it or not.")


@router.message()
async def handle_docs_photo(message: Message):
    if message.content_type == 'photo':
        photo = message.photo[-1]  # Get the best resolution photo
        file = await bot.get_file(photo.file_id)
        file_path = f'{path}/{photo.file_id}.jpg'
        await bot.download_file(file.file_path, destination=file_path)

        # Process the image
        predictions = predict_mushrooms()
        for prediction in predictions:
            print(prediction)
            if prediction == 0:
                await message.reply(f"I found mushrooms in the photo.\nThis mushroom belongs to the species: Edible.")
            elif prediction==4:
                await message.reply(f"I found mushrooms in the photo.\nThis mushroom belongs to the species: Poisonous.")
               # await message.reply(f"I found mushrooms in the photo.\nThis mushroom belongs to the species: {classes[prediction]}.")
            elif prediction==1:
                await message.reply(f"I found mushrooms in the photo.\nThis mushroom belongs to the species: hallucinogenic.")
            elif prediction==2:
                await message.reply(f"I found mushrooms in the photo.\nThis mushroom belongs to the species: Inedible.")
            elif prediction==3:
                await message.reply("I didn't find any mushrooms in the photo.")



            

@router.message()
async def handle_unknown_message(message: Message):
    await message.reply(
        "I'm sorry, but I can only identify mushrooms. Please send me a photo of a mushroom."
    )


# Main function
async def main():
    dp.include_router(router)  # Register the router
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
