import streamlit as st
from PIL import Image

from scrapping import scrape_all  # Your scraper file

from myblip import get_blip_caption  # Your Hugging Face API script
from gptdata import get_data,ask_gpt
from yolo_crop_utils import load_yolo_model, load_image_from_pil, detect_objects, crop_object
# 🧠 State Management
import cv2
if "description" not in st.session_state:
    st.session_state["description"] = ""
if "results" not in st.session_state:
    st.session_state["results"] = {}

# 🎨 UI Layout
st.markdown(
    """
    <h1 style='text-align: center; color: gold; text-shadow: 0 0 10px yellow; font-size: 50px;'>
        🛍️ Smart Cart
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("Upload an image and find the product across major platforms!")

# 📸 Image placeholder
image = None
image1=None
model = load_yolo_model()
detected_img=None
col1, col2 = st.columns(2)
with col1:
    tab1, tab2 = st.tabs(["Upload", "Camara"])
    with tab2:
        camera_image = st.camera_input("Capture Image")
        if camera_image:
            image = Image.open(camera_image)

    with tab1:
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            image1 = Image.open(uploaded_file)

if image:
    img_np = load_image_from_pil(image)
    boxes, detected_img = detect_objects(img_np, model)
    st.image(cv2.cvtColor(detected_img, cv2.COLOR_BGR2RGB), caption="Detected Objects")

    if boxes:
        st.write("Select an object to crop:")
        cols = st.columns(min(3, len(boxes)))
        for i, box_info in enumerate(boxes):
            with cols[i % len(cols)]:
                if st.button(f"Object {i+1}"):
                    cropped = crop_object(img_np, boxes, i)
                    st.session_state["cropped_image"] = cropped

if "cropped_image" in st.session_state and st.session_state["cropped_image"] is not None:
    st.image(
        cv2.cvtColor(st.session_state["cropped_image"], cv2.COLOR_BGR2RGB),
        caption="Cropped Product",
        use_container_width=True
    )
if st.session_state.get("cropped_image", None) is not None:
    image= st.session_state.get("cropped_image", None)
elif image1 is not None:
    st.image(image1, caption="Detected Objects")
    image=image1

platforms = st.multiselect("Choose platforms to search", ["Amazon", "Shopclues", "Meesho", "Snapdeal"], default=["Amazon", "Snapdeal"])

# 📋 On Upload
if image is not None:

    if st.button("🧠 Describe Product"):
        with st.spinner("Getting description from image..."):
            desc=get_blip_caption(image)
            prompt=f"you are a product name retriver from the sentence.give the product name to search in e-commerce site to get exact product.dont give extra information only give what i asked.sentence:{desc}.product name:"
            name=get_data(prompt)
            st.session_state["description"] = name
        st.success("Product details fetched succesfully ")

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
                title = item.get("title", "")
                desc = item.get("description", item.get("title", "")) + title
            else:
                desc = item.get("description", item.get("title", ""))
            gpt_reply = ask_gpt(desc,user_msg)
            answers.append(f"- {gpt_reply}")
        st.markdown(f"### 🛒 {plat}")
        st.markdown("\n".join(answers) if answers else "_No data available_")


