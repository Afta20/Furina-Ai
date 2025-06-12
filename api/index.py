import os
import google.generativeai as genai
import gradio as gr

# --- 1. KONFIGURASI UNTUK DEPLOYMENT ---
# DIUBAH: Mengambil API Key hanya dari environment secrets, lebih aman.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("KESALAHAN: GEMINI_API_KEY tidak diatur. Harap atur di 'Repository secrets' pada Hugging Face Spaces.")

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
    
    def start_new_chat():
        chat = model.start_chat(history=[
            {'role': 'user', 'parts': [SYSTEM_PROMPT]},
            {'role': 'model', 'parts': ["Tentu saja! Panggung ini milikku! Apa yang akan kita ciptakan hari ini, partner in crime-ku?"]},
        ])
        return chat

    chat_session = start_new_chat()
    print("🧠 Otak (Gemini) telah terhubung dan siap beraksi!")
except Exception as e:
    raise RuntimeError(f"❌ Gagal terhubung atau mengonfigurasi Gemini. Error: {e}")

# --- 3. FUNGSI UNTUK LOGIKA CHATBOT ---
def handle_chat_interaction(user_message, chat_history):
    global chat_session
    try:
        response = chat_session.send_message(user_message)
        chat_history.append((user_message, response.text))
    except Exception as e:
        error_message = f"😵 Aduh! Sepertinya ada sedikit gangguan teknis di panggungku. Coba lagi nanti, ya! (Error: {e})"
        chat_history.append((user_message, error_message))
    return chat_history, ""

def clear_chat_history():
    global chat_session
    chat_session = start_new_chat()
    initial_message = chat_session.history[1].parts[0].text
    return [(None, initial_message)]

# --- 4. MEMBUAT ANTARMUKA GRAFIS (GUI) DENGAN GRADIO ---
print("🎨 Membangun panggung (GUI)...")
theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.blue, 
    secondary_hue=gr.themes.colors.sky
).set(
    body_background_fill="#F0F8FF",
    block_background_fill="white",
    button_primary_background_fill="*primary_500",
    button_primary_text_color="white",
)

# DIPERBAIKI: 'app' didefinisikan sebelum 'with' untuk memperbaiki error Pylance
app = gr.Blocks(theme=theme, title="Chat dengan Furina")

with app:
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
        # DIUBAH: Menggunakan URL avatar yang lebih stabil
        avatar_images=(None, "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Full_Sphere_Glow.svg/2048px-Full_Sphere_Glow.svg.png")
    )
    with gr.Row():
        user_input = gr.Textbox(
            show_label=False,
            placeholder="Ketik idemu di sini dan tekan Enter...",
            scale=4
        )
        send_button = gr.Button("Kirim", variant="primary", scale=1)
    clear_button = gr.Button("✨ Mulai Pertunjukan Baru (Hapus Histori)", variant="secondary")

    # --- 5. MENGHUBUNGKAN AKSI PENGGUNA KE FUNGSI ---
    send_button.click(
        fn=handle_chat_interaction,
        inputs=[user_input, chatbot_ui],
        outputs=[chatbot_ui, user_input]
    )
    user_input.submit(
        fn=handle_chat_interaction,
        inputs=[user_input, chatbot_ui],
        outputs=[chatbot_ui, user_input]
    )
    clear_button.click(
        fn=clear_chat_history,
        inputs=[],
        outputs=[chatbot_ui]
    )

# --- 6. MENJALANKAN APLIKASI ---
# Diperlukan oleh Hugging Face Spaces untuk menjalankan server
if __name__ == "__main__":
    app.launch()