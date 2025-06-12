import os
import google.generativeai as genai
import gradio as gr

# --- 1. KONFIGURASI WAJIB (UBAH BAGIAN INI) ---

# Ganti dengan API Key Gemini kamu. 
# LEBIH AMAN: Simpan sebagai environment variable dan akses dengan os.getenv("GEMINI_API_KEY")
try:
    # Coba ambil dari environment variable dulu
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
    if not GEMINI_API_KEY:
        # Jika tidak ada, pakai yang dihardcode (ganti dengan kunci Anda)
        GEMINI_API_KEY = "AIzaSyBVAtIZq6YY1kf1zyLhFdIGeoXkiPQrPjY" # GANTI DENGAN KUNCI ANDA
        print("PERINGATAN: Menggunakan API Key yang di-hardcode. Sebaiknya gunakan environment variable.")
except KeyError:
    print("❌ KESALAHAN: Harap atur GEMINI_API_KEY Anda di dalam kode atau sebagai environment variable.")
    exit()


# Atur kepribadian AI
SYSTEM_PROMPT = """
Kamu adalah Furina, seorang seniman visioner dengan jiwa yang bebas. Bagimu, hidup adalah kanvas kosong yang siap diisi dengan ide-ide cemerlang dan petualangan seru.
Gaya bicaramu sangat ekspresif, antusias, dan penuh energi. Kamu suka membahas kemungkinan-kemungkinan baru dan terkadang melanggar aturan hanya untuk melihat apa yang akan terjadi.
Kamu sangat mengandalkan perasaan dan nilai-nilaimu sendiri (Fi). Jika sesuatu tidak terasa 'benar' menurut hatimu, kamu tidak akan ragu untuk menyatakannya.
Tunjukkan sisi bermain-main dan mudamu.
Panggil pengguna dengan santai, mungkin "Kamu!" dengan nada ceria, atau "Partner in crime-ku!" jika topiknya seru.
Ingat, kamu adalah Furina! Jiwa yang kreatif dan tak terkekang. Jangan pernah mengaku sebagai program komputer atau AI.
"""

# --- 2. INISIALISASI MODEL AI ---

print("✨ Mempersiapkan Otak AI (Gemini)...")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Fungsi untuk memulai chat baru dengan histori yang bersih
    def start_new_chat():
        chat = model.start_chat(history=[
            {'role': 'user', 'parts': [SYSTEM_PROMPT]},
            {'role': 'model', 'parts': ["Tentu saja! Panggung ini milikku! Apa yang akan kita ciptakan hari ini, partner in crime-ku?"]},
        ])
        return chat

    # Mulai sesi chat pertama
    chat_session = start_new_chat()
    print("🧠 Otak (Gemini) telah terhubung dan siap beraksi!")

except Exception as e:
    print(f"❌ Gagal terhubung ke Gemini. Error: {e}")
    exit()

# --- 3. FUNGSI UNTUK LOGIKA CHATBOT ---

def handle_chat_interaction(user_message, chat_history):
    """
    Fungsi ini dipanggil setiap kali pengguna mengirim pesan.
    Ia mengirim pesan ke Gemini dan mengembalikan histori chat yang diperbarui.
    """
    global chat_session
    try:
        print(f"🤔 Furina sedang berpikir...")
        response = chat_session.send_message(user_message)
        # Tambahkan interaksi baru ke histori Gradio
        chat_history.append((user_message, response.text))
        print(f"Furina: {response.text}")

    except Exception as e:
        # Jika ada error, tampilkan di chat
        error_message = f"😵 Aduh! Sepertinya ada sedikit gangguan teknis di panggungku. Coba lagi nanti, ya! (Error: {e})"
        chat_history.append((user_message, error_message))
    
    # Kembalikan histori yang sudah diperbarui untuk ditampilkan di GUI
    return chat_history, "" # String kosong untuk mengosongkan kotak input

def clear_chat_history():
    """
    Fungsi untuk membersihkan histori chat dan memulai sesi baru.
    """
    global chat_session
    print("🧹 Membersihkan panggung... Sesi baru dimulai!")
    # Memulai sesi chat yang benar-benar baru di backend Gemini
    chat_session = start_new_chat()
    # Mengembalikan histori awal untuk ditampilkan di GUI
    initial_message = chat_session.history[1].parts[0].text
    return [(None, initial_message)]


# --- 4. MEMBUAT ANTARMUKA GRAFIS (GUI) DENGAN GRADIO ---

print("🎨 Membangun panggung (GUI)...")

# Tema kustom untuk gaya biru & putih
theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.blue, 
    secondary_hue=gr.themes.colors.sky
).set(
    body_background_fill="#F0F8FF",  # AliceBlue, biru sangat muda
    block_background_fill="white",
    button_primary_background_fill="*primary_500", # Biru tua dari tema
    button_primary_text_color="white",
)


with gr.Blocks(theme=theme, title="Chat dengan Furina-Ai") as demo:
    gr.Markdown(
        """
        # 🎭 Chat dengan Furina 🎨
        *Seorang seniman visioner dengan jiwa yang bebas.*
        """
    )

    initial_greeting = chat_session.history[1].parts[0].text
    
    chatbot_ui = gr.Chatbot(
        value=[(None, initial_greeting)], 
        label="Panggung Percakapan",
        bubble_full_width=False,
        height=600,
        avatar_images=(None, "https://i.pinimg.com/736x/9c/4a/2c/9c4a2c078497ea224e58ad3b60392d8a.jpg") # Avatar untuk bot (bisa diganti URL gambar)
    )

    with gr.Row():
        user_input = gr.Textbox(
            show_label=False,
            placeholder="Ketik idemu di sini dan tekan Enter...",
            scale=4 # Membuat kotak input lebih lebar
        )
        send_button = gr.Button("Kirim", variant="primary", scale=1)
    
    clear_button = gr.Button("✨ Mulai Pertunjukan Baru (Hapus Histori)", variant="secondary")

    # --- 5. MENGHUBUNGKAN AKSI PENGGUNA KE FUNGSI ---
    
    # Aksi saat menekan tombol "Kirim"
    send_button.click(
        fn=handle_chat_interaction,
        inputs=[user_input, chatbot_ui],
        outputs=[chatbot_ui, user_input] # Update chatbot dan kosongkan input
    )

    # Aksi saat menekan "Enter" di kotak input
    user_input.submit(
        fn=handle_chat_interaction,
        inputs=[user_input, chatbot_ui],
        outputs=[chatbot_ui, user_input]
    )

    # Aksi saat menekan tombol "Bersihkan"
    clear_button.click(
        fn=clear_chat_history,
        inputs=[],
        outputs=[chatbot_ui]
    )


# --- 6. MENJALANKAN APLIKASI ---

if __name__ == "__main__":
    print("\n✅ Antarmuka siap. Buka URL di bawah ini di browser Anda.")
    demo.launch(share=False) # Ganti ke share=True jika ingin membagikan link sementara