import streamlit as st
import base64
from trunic_generator import english_to_trunic

# Load and inject the font once (Streamlit re-runs this on each interaction,
# but that's fine — it's fast)
def inject_font(font_family, ttf_path):
    with open(ttf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <style>
        @font-face {{
            font-family: '{font_family}';
            src: url('data:font/truetype;base64,{b64}') format('truetype');
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

inject_font("Trunic-Regular", r"build\Trunic-Regular.ttf")
inject_font("Trunic-Strikethrough", r"build\Trunic-Strikethrough.ttf")

st.title("Trunic Generator")

english = st.text_area("English")

strikethrough_enabled = st.checkbox("Strikethrough", True)
with st.container(horizontal=True, vertical_alignment="center"):
    st.write("Font size")
    font_size = st.number_input(
        label = "Font size",
        label_visibility = "collapsed",
        min_value = 0,
        max_value = 100,
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