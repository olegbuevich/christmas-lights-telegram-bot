import json
import os
import re
from functools import wraps

import boto3
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Dispatcher
)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
LIST_OF_ADMINS = [int(id) for id in os.environ.get("LIST_OF_ADMINS", "").split(",") if id.isnumeric()]

BRIGHTNESS_MENU = [
    [
        InlineKeyboardButton("10", callback_data="#BRI-25#"),
        InlineKeyboardButton("30", callback_data="#BRI-75#"),
        InlineKeyboardButton("40", callback_data="#BRI-100#"),
        InlineKeyboardButton("60", callback_data="#BRI-150#"),
        # InlineKeyboardButton("90", callback_data="#BRI-225#"),
    ],
    [
        InlineKeyboardButton("20", callback_data="#BRI-50#"),
        InlineKeyboardButton("75", callback_data="#BRI-190#"),
    ],
    [
        InlineKeyboardButton("50", callback_data="#BRI-125#"),
        InlineKeyboardButton("100", callback_data="#BRI-255#"),
    ],
    [
        InlineKeyboardButton("Exit", callback_data="#menu#"),
    ],
]
EFFECTS_MENU = [
    [
        InlineKeyboardButton("None", callback_data="#EFF-SOLID#"),
        InlineKeyboardButton("Fill", callback_data="#EFF-FILLCOLOR#"),
    ],
    [
        InlineKeyboardButton("Snow", callback_data="#EFF-SNOW#"),
        InlineKeyboardButton("Sparkles", callback_data="#EFF-SPARKLES#"),
    ],
    [
        InlineKeyboardButton("Matrix", callback_data="#EFF-MATRIX#"),
        InlineKeyboardButton("Starfall", callback_data="#EFF-STARFALL#"),
    ],
    [
        InlineKeyboardButton("Ball", callback_data="#EFF-BALL#"),
        InlineKeyboardButton("Balls", callback_data="#EFF-BALLS#"),
    ],
    [
        InlineKeyboardButton("Fire 1", callback_data="#EFF-FIRE#"),
        InlineKeyboardButton("Fire 2", callback_data="#EFF-FIRE2#"),
    ],
    [
        InlineKeyboardButton("Tree", callback_data="#EFF-NYTREE#"),
    ],
    [
        InlineKeyboardButton("Exit", callback_data="#menu#"),
    ],
]


def send_aws_iot_mqtt(topic: str, message: str):
    iot_client = boto3.client("iot-data")
    iot_client.publish(topic=topic, payload=message)


def send_mqtt_command(data: dict):
    command_topic = "diy/christmas-lights/command"
    send_aws_iot_mqtt(command_topic, json.dumps(data))


def restricted(func):
    """Decorator."""
    @wraps(func)
    def wrapped(update, *args, **kwargs):
        """Restrict access to some bot commands."""
        # extract user_id from arbitrary update
        try:
            user_id = update.message.from_user.id
        except (NameError, AttributeError):
            try:
                user_id = update.inline_query.from_user.id
            except (NameError, AttributeError):
                try:
                    user_id = update.chosen_inline_result.from_user.id
                except (NameError, AttributeError):
                    try:
                        user_id = update.callback_query.from_user.id
                    except (NameError, AttributeError):
                        print("No user_id available in update.")
                        return
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, *args, **kwargs)
    return wrapped


@restricted
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('1️⃣ On/Off 0️⃣', callback_data='#state#')],
        [InlineKeyboardButton('🔥 Effect 🔥', callback_data='#effect#')],
        [InlineKeyboardButton('🌞 Brightness 🌑', callback_data='#brightness#')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Choose an action", reply_markup=reply_markup)
    return "main"


@restricted
def menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton('1️⃣ On/Off 0️⃣', callback_data='#state#')],
        [InlineKeyboardButton('🔥 Effect 🔥', callback_data='#effect#')],
        [InlineKeyboardButton('🌞 Brightness 🌑', callback_data='#brightness#')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Choose an action", reply_markup=reply_markup)
    return "main"


@restricted
def state(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton('On', callback_data='#ON#'),
            InlineKeyboardButton('Off', callback_data='#OFF#'),
        ],
        [
            InlineKeyboardButton("Return", callback_data="#menu#")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Choose a state", reply_markup=reply_markup)
    return "state"


@restricted
def state_switch(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if context.match.string in ["#ON#"]:
        send_mqtt_command({"state": "ON"})
    else:
        send_mqtt_command({"state": "OFF"})
    return "state"


@restricted
def effect(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    reply_markup = InlineKeyboardMarkup(EFFECTS_MENU)
    query.edit_message_text("Choose an effect", reply_markup=reply_markup)
    return "effect"


@restricted
def effect_switch(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if context.match.string in ["#EFF-SOLID#"]:
        send_mqtt_command({"effect": "solid"})
    elif context.match.string in ["#EFF-FILLCOLOR#"]:
        send_mqtt_command({"effect": "fill_color"})
    elif context.match.string in ["#EFF-SNOW#"]:
        send_mqtt_command({"effect": "snow"})
    elif context.match.string in ["#EFF-SPARKLES#"]:
        send_mqtt_command({"effect": "sparkles"})
    elif context.match.string in ["#EFF-MATRIX#"]:
        send_mqtt_command({"effect": "matrix"})
    elif context.match.string in ["#EFF-STARFALL#"]:
        send_mqtt_command({"effect": "starfall"})
    elif context.match.string in ["#EFF-BALL#"]:
        send_mqtt_command({"effect": "ball"})
    elif context.match.string in ["#EFF-BALLS#"]:
        send_mqtt_command({"effect": "balls"})
    elif context.match.string in ["#EFF-FIRE#"]:
        send_mqtt_command({"effect": "fire"})
    elif context.match.string in ["#EFF-FIRE2#"]:
        send_mqtt_command({"effect": "fire2"})
    elif context.match.string in ["#EFF-NYTREE#"]:
        send_mqtt_command({"effect": "nytree"})
    return "effect"


@restricted
def brightness(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    reply_markup = InlineKeyboardMarkup(BRIGHTNESS_MENU)
    query.edit_message_text("Set a brightness", reply_markup=reply_markup)
    return "brightness"


@restricted
def brightness_switch(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    value = re.sub(r'^#BRI-(\d+)#$', '\\1', context.match.string)
    if value.isdigit():
        send_mqtt_command({"brightness": int(value)})
    return "brightness"


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)


def handler(event, _):
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            "main": [
                CallbackQueryHandler(state, pattern='^#state#$'),
                CallbackQueryHandler(menu, pattern='^#menu#$'),
                CallbackQueryHandler(effect, pattern='^#effect#$'),
                CallbackQueryHandler(brightness, pattern='^#brightness#$'),
            ],
            "state": [
                CallbackQueryHandler(menu, pattern='^#menu#$'),
                CallbackQueryHandler(state_switch, pattern='^#ON#$'),
                CallbackQueryHandler(state_switch, pattern='^#OFF#$'),
            ],
            "effect": [
                CallbackQueryHandler(menu, pattern='^#menu#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-SOLID#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-FILLCOLOR#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-SNOW#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-SPARKLES#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-MATRIX#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-STARFALL#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-BALL#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-BALLS#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-FIRE#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-FIRE2#$'),
                CallbackQueryHandler(effect_switch, pattern='^#EFF-NYTREE#$'),
            ],
            "brightness": [
                CallbackQueryHandler(menu, pattern='^#menu#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-25#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-50#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-75#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-100#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-125#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-150#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-190#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-225#$'),
                CallbackQueryHandler(brightness_switch, pattern='^#BRI-255#$'),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    dispatcher.add_handler(conversation_handler)

    try:
        dispatcher.process_update(
            Update.de_json(json.loads(event["body"]), bot)
        )

    except Exception as e:
        print(e)
        return {"statusCode": 500}

    return {"statusCode": 200}
