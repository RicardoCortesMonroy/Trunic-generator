import streamlit as st
import base64
from trunic_generator import english_to_trunic
from pathlib import Path

BASE_DIR = Path(__file__).parent

# # Load and inject the font once (Streamlit re-runs this on each interaction,
# # but that's fine — it's fast)
# def inject_font(font_family: str, ttf_path: Path):
#     with open(ttf_path, "rb") as f:
#         b64 = base64.b64encode(f.read()).decode()

#     st.markdown(f"""
#         <style>
#         @font-face {{
#             font-family: '{font_family}';
#             src: url('data:font/truetype;base64,{b64}') format('truetype');
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

# inject_font("Trunic-Regular", BASE_DIR / "build" / "Trunic-Regular.ttf")
# inject_font("Trunic-Strikethrough", BASE_DIR / "build" / "Trunic-Strikethrough.ttf")


def get_url(font_name: Path) -> str:
    ttf_path = BASE_DIR / "build" / f"{font_name}.ttf"
    with open(ttf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'data:font/truetype;base64,{b64}'

st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'Trunic-Regular';
        src: url('{get_url("Trunic-Regular")}') format('truetype');
    }}
    @font-face {{
        font-family: 'Trunic-Strikethrough';
        src: url('{get_url("Trunic-Strikethrough")}') format('truetype');
    }}
    
    .hero {{
        position: relative;
        height: 160px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }}      

    .bg-glyphs {{
        position: absolute;
        inset: 0;
        font-family: 'Trunic-Strikethrough';
        font-size: 120px;
        top: 20px;
        opacity: 0.10;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
        white-space: nowrap;
    }}

    .title {{
        position: relative;
        z-index: 2;
        font-size: 3rem;
        font-weight: 700;
    }}
    </style>

    <div class="hero">
        <div class="bg-glyphs">&#xe084&#xe0b4&#xe12e&#xe0d0 &#xe022&#xe11d&#xe24d&#xe1d4</div>
        <div class="title">Trunic Generator</div>
    </div>
    """,
    unsafe_allow_html=True
)

english = st.text_area("English", value="Hello, World!")

strikethrough_enabled = st.checkbox("Strikethrough", True)
with st.container(horizontal=True, vertical_alignment="center"):
    st.write("Font size")
    font_size = st.number_input(
        label = "Font size",
        label_visibility = "collapsed",
        min_value=0,
        max_value=200,
        value=40,
        width = 130
    )


@st.cache_data
def english_to_trunic_cache(text):
    return english_to_trunic(text)

# if st.button("Generate"):
glyph_unicode_list = english_to_trunic_cache(english)
unicode_text = ''.join([c if not isinstance(c,int) else f"&#x{c:x}" for c in glyph_unicode_list])

font_family = "Trunic-Strikethrough" if strikethrough_enabled else "Trunic-Regular"

st.markdown(f"""
    <div style="
        font-family: {font_family}, serif;
        font-size: {font_size}px;
        line-height: 1.0;
        letter-spacing: 0.0em;
        padding: 1rem;
        border: 1px solid #ccc;
        border-radius: 8px;
        min-height: 80px;
    ">
        {unicode_text}
    </div>
    """,
    unsafe_allow_html=True
)