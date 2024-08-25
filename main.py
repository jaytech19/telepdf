import os
import telebot
from telebot import types
from PyPDF2 import PdfWriter

API_TOKEN ="7268571031:AAEZjTKNFDts9Gqgg2hhP-VNq478Y5l-Dok"
chat_id = "6765727340"
bot = telebot.TeleBot(API_TOKEN)

merger = PdfWriter()
pdf_files = []
# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Selamat datang di TelePdf!
Fitur utama :
- Kompress, gabungkan file PDF
- Mengekstrak gambar dan teks dari PDF
- Mengkonversi file PDF menjadi gambar
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(content_types='document')
def receive_files(message):
    if(message.document.mime_type!="application/pdf"):
       bot.send_message(message.chat.id,"File yang Anda kirim bukan pdf, Silakan kirim file yang benar")
       return

    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    download_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as pdf:
        pdf_files.append(file_name)
        pdf.write(download_file)
    markup = types.InlineKeyboardMarkup(row_width=1)
    selesai = types.InlineKeyboardButton("selesai",callback_data='selesai')
    lanjut = types.InlineKeyboardButton("lanjut",callback_data='lanjut')
    batal = types.InlineKeyboardButton("batal",callback_data='batal')
    markup.add(selesai,lanjut,batal)
    bot.send_message(message.chat.id,f"Anda telah mengirimkan {len(pdf_files)} file",reply_markup=markup)


@bot.callback_query_handler(func=lambda message:True)
def callback_query(call):
    global pdf_files
    if call.data == 'selesai':
        bot.send_message(call.message.chat.id, 'Mohon tunggu file sedang diproses...')
        for pdf in pdf_files:
            merger.append(pdf)

        merger.write("merged-pdf.pdf")
        merger.close()


        with open("merged-pdf.pdf", 'rb') as pdf:
            bot.send_document(chat_id,pdf)
        for pdf in pdf_files:
            os.remove(pdf)
        os.remove("merged-pdf.pdf")
        pdf_files = []
    elif call.data == "lanjut":
        bot.send_message(call.message.chat.id, 'Silakan kirim file selanjutnya!')
    else:
        for pdf in pdf_files:
            os.remove(pdf)
        os.remove("merged-pdf.pdf")
        pdf_files = []
        bot.send_message(call.message.chat.id, 'Berhasil dibatalkan, file Anda telah dihapus dari server')

bot.infinity_polling()
