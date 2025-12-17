import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="Editor de Imagens com Zoom",
    page_icon="🖼️",
    layout="wide"
)

# CSS personalizado para design moderno
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .upload-box {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 20px 0;
    }
    h1 {
        color: white;
        text-align: center;
        font-size: 3em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    h2 {
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .subtitle {
        color: white;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 30px;
        opacity: 0.9;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%);
        color: white;
        border-radius: 25px;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 3px 5px 2px rgba(255, 105, 135, .3);
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 10px 4px rgba(255, 105, 135, .4);
    }
    .stDownloadButton>button {
        background: linear-gradient(45deg, #2196F3 30%, #21CBF3 90%);
        color: white;
        border-radius: 25px;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 3px 5px 2px rgba(33, 203, 243, .3);
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown("<h1>🎨 Editor de Imagens Zoom & Texto</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Carregue uma imagem, adicione texto com zoom e salve com design moderno!</p>", unsafe_allow_html=True)

# Inicializar estados
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

# Layout em colunas
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload da Imagem")
    uploaded_file = st.file_uploader(
        "Escolha uma imagem (JPG, PNG, JPEG)",
        type=['jpg', 'jpeg', 'png'],
        help="Arraste e solte ou clique para selecionar"
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagem Original", use_container_width=True)

        st.markdown("### ✏️ Configurações")

        # Texto
        text_input = st.text_area(
            "Digite o texto que deseja adicionar:",
            placeholder="Exemplo: Bem-vindo ao meu mundo!",
            height=100
        )

        # Zoom
        zoom_level = st.slider(
            "🔍 Nível de Zoom",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Ajuste o zoom da imagem"
        )

        # Tamanho da fonte
        font_size = st.slider(
            "📏 Tamanho da Fonte",
            min_value=20,
            max_value=150,
            value=60,
            step=5
        )

        # Cor do texto
        text_color = st.color_picker(
            "🎨 Cor do Texto",
            value="#FFFFFF",
            help="Escolha a cor do texto"
        )

        # Posição do texto
        text_position = st.selectbox(
            "📍 Posição do Texto",
            ["Centro", "Topo", "Meio", "Base"],
            help="Escolha onde o texto aparecerá"
        )

        # Efeito de sombra
        add_shadow = st.checkbox("✨ Adicionar sombra ao texto", value=True)

        # Fundo semi-transparente
        add_background = st.checkbox("🎭 Adicionar fundo ao texto", value=True)

        # Botão de processar
        if st.button("🎯 Processar Imagem"):
            with st.spinner("Processando..."):
                # Aplicar zoom
                original_size = image.size
                new_size = (int(original_size[0] * zoom_level), int(original_size[1] * zoom_level))
                zoomed_image = image.resize(new_size, Image.Resampling.LANCZOS)

                # Criar imagem final com tamanho original (crop do centro se zoom > 1)
                if zoom_level > 1:
                    left = (new_size[0] - original_size[0]) // 2
                    top = (new_size[1] - original_size[1]) // 2
                    right = left + original_size[0]
                    bottom = top + original_size[1]
                    final_image = zoomed_image.crop((left, top, right, bottom))
                else:
                    # Se zoom < 1, centralizar na imagem original
                    final_image = Image.new('RGB', original_size, (255, 255, 255))
                    paste_x = (original_size[0] - new_size[0]) // 2
                    paste_y = (original_size[1] - new_size[1]) // 2
                    final_image.paste(zoomed_image, (paste_x, paste_y))

                # Adicionar texto se fornecido
                if text_input:
                    draw = ImageDraw.Draw(final_image)

                    # Tentar usar uma fonte melhor
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                    except:
                        font = ImageFont.load_default()

                    # Calcular posição do texto
                    bbox = draw.textbbox((0, 0), text_input, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]

                    width, height = final_image.size

                    if text_position == "Centro":
                        x = (width - text_width) // 2
                        y = (height - text_height) // 2
                    elif text_position == "Topo":
                        x = (width - text_width) // 2
                        y = height // 10
                    elif text_position == "Meio":
                        x = (width - text_width) // 2
                        y = height // 2 - text_height // 2
                    else:  # Base
                        x = (width - text_width) // 2
                        y = height - height // 10 - text_height

                    # Adicionar fundo semi-transparente
                    if add_background:
                        overlay = Image.new('RGBA', final_image.size, (0, 0, 0, 0))
                        overlay_draw = ImageDraw.Draw(overlay)
                        padding = 20
                        overlay_draw.rounded_rectangle(
                            [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                            radius=15,
                            fill=(0, 0, 0, 180)
                        )
                        final_image = final_image.convert('RGBA')
                        final_image = Image.alpha_composite(final_image, overlay)
                        final_image = final_image.convert('RGB')
                        draw = ImageDraw.Draw(final_image)

                    # Adicionar sombra
                    if add_shadow:
                        shadow_offset = 3
                        draw.text((x + shadow_offset, y + shadow_offset), text_input, font=font, fill=(0, 0, 0, 128))

                    # Adicionar texto principal
                    draw.text((x, y), text_input, font=font, fill=text_color)

                st.session_state.processed_image = final_image
                st.success("✅ Imagem processada com sucesso!")

with col2:
    st.markdown("### 🎨 Resultado")

    if st.session_state.processed_image:
        st.image(st.session_state.processed_image, caption="Imagem Processada", use_container_width=True)

        # Botão de download
        buf = io.BytesIO()
        st.session_state.processed_image.save(buf, format="PNG")
        buf.seek(0)

        st.download_button(
            label="💾 Baixar Imagem",
            data=buf,
            file_name="imagem_editada.png",
            mime="image/png"
        )

        st.markdown("---")
        st.markdown("#### 📊 Informações da Imagem")
        st.write(f"**Dimensões:** {st.session_state.processed_image.size[0]} x {st.session_state.processed_image.size[1]} pixels")
        st.write(f"**Formato:** PNG")
    else:
        st.info("👈 Configure as opções à esquerda e clique em 'Processar Imagem'")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: white; opacity: 0.8;'>Criado com ❤️ usando Streamlit | © 2025</p>",
    unsafe_allow_html=True
)
