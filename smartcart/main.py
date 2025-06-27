import streamlit as st
from PIL import Image
from scrapping import scrape_all  # Your scraper file
# from llava_api import get_description_from_image  # Optional for LLaVA
from myblip import get_blip_caption  # Your Hugging Face API script
from gptdata import get_data,ask_gpt
# 🧠 State Management
if "description" not in st.session_state:
    st.session_state["description"] = ""
if "results" not in st.session_state:
    st.session_state["results"] = {}

# 🎨 UI Layout
st.title("🛍️ Smart Cart")
st.markdown("Upload an image and find the product across major platforms!")

# 📸 Upload Image
uploaded_img = st.file_uploader("Upload product image", type=["jpg", "png", "jpeg"])
platforms = st.multiselect("Choose platforms to search", ["Amazon", "Flipkart", "Meesho", "Snapdeal"], default=["Amazon", "Snapdeal"])

# 📋 On Upload
if uploaded_img:
    image = Image.open(uploaded_img).convert("RGB")
    st.image(image, caption="Uploaded Product", use_container_width=True)

    if st.button("🧠 Describe Product"):
        with st.spinner("Getting description from image..."):
            desc=get_blip_caption(uploaded_img)
            prompt=f"you are a product name retriver from the sentence.give the product name to search in e-commerce site to get exact product.dont give extra information only give what i asked.sentence:{desc}.product name:"
            name=get_data(prompt)
            st.session_state["description"] = name
        st.success("Product: " + st.session_state["description"])

# 🔍 On Search
if st.session_state["description"] and st.button("🔎 Search Product"):
    with st.spinner("Searching platforms..."):
        st.session_state["results"] = scrape_all(st.session_state["description"], platforms)

# 🖼️ Show Results
if st.session_state["results"]:
    for plat, items in st.session_state["results"].items():
        st.subheader(f"🔷 {plat}")
        for item in items:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(item["image"], width=120)
            with col2:
                st.markdown(f"**{item['title']}**")
                st.markdown(f"💰 {item['price']} | ⭐ {item['rating']} | 🗣️ {item['reviews']}")
                st.markdown(f"[🔗 View Product]({item['link']})")
                st.markdown("---")

# 💬 Chat Interface
st.subheader("🧠 Chat with Product")
user_msg = st.text_input("Ask something about this product...")

if user_msg:
    st.markdown("**Your Question:** " + user_msg)

    # Detect mentioned platform
    mentioned = [p for p in platforms if p.lower() in user_msg.lower()]
    if not mentioned:
        mentioned = ["Amazon", "Snapdeal"]  # default

    for plat in mentioned:
        answers = []
        items = st.session_state["results"].get(plat, [])
        for item in items:
            if item["description"]:
                title=item.get("title", "")
                desc = item.get("description",item.get("title",""))+title
            else:
                desc = item.get("description", item.get("title", ""))
            gpt_reply = ask_gpt(desc,user_msg)
            answers.append(f"- {gpt_reply}")
        st.markdown(f"### 🛒 {plat}")
        st.markdown("\n".join(answers) if answers else "_No data available_")


